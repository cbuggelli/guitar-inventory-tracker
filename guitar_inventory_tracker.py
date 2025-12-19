import os
import csv
import requests
import datetime
import json
from typing import List, Dict
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

ALGOLIA_API_URL = f"https://{os.getenv('ALGOLIA_APP_ID')}-dsn.algolia.net/1/indexes/*/queries"
HEADERS = {
  "x-algolia-api-key": os.getenv("ALGOLIA_API_KEY"),
  "x-algolia-application-id": os.getenv("ALGOLIA_APP_ID"),
  "Content-Type": "application/json"
}

CATEGORY_MAP = {
  "Guitars": "categories.lvl0:Guitars",
  "Basses": "categories.lvl0:Bass",
  "Amplifiers": "categories.lvl1:Amplifiers%20%26%20Effects%20%3E%20Amplifiers",
  "Effects": "categories.lvl1:Amplifiers%20%26%20Effects%20%3E%20Effects"
}

FAVORITE_STORES = {"1": "Palm Desert", "2": "San Bernardino", "3": "Hollywood", "4": "Manhattan"}

def validate_store_name(store_name: str) -> bool:
  """Check if store name contains only letters and spaces."""
  return store_name.replace(" ", "").isalpha()

def fetch_inventory(store_name: str, category_filter: str) -> List[Dict]:
  facet_filters = f'["{category_filter}","condition.lvl0:Used",["stores:{store_name.lower()}"]]'
  params_string = f'query=&hitsPerPage=96&page=0&facetFilters={facet_filters}&facets=["*"]&numericFilters=["startDate<=1765567093"]&ruleContexts=["store"]'
  
  payload = {
    "requests": [
      {
        "indexName": "guitarcenter",
        "params": params_string
      }
    ]
  }
  response = requests.post(ALGOLIA_API_URL, headers=HEADERS, json=payload)
  response.raise_for_status()
  return response.json()['results'][0]['hits']

def load_previous_inventory(filepath: str) -> Dict[str, Dict]:
  if not os.path.exists(filepath):
    return {}
  with open(filepath, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    return {row['product_id']: row for row in reader}
  
def save_inventory(filepath: str, inventory: List[Dict]):
  fieldnames = ["product_id", "brand", "display_name", "current_price", "list_price", "price_history", "condition", "stickers", "date_added", "price_delta", "status", "date_sold"]
  with open(filepath, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for row in inventory:
      writer.writerow(row)

def normalize_item(hit: Dict, previous: Dict[str, Dict], today: str, new_items_list: List[str]) -> Dict:
  product_id = str(hit.get("productId", ""))
  brand = hit.get("brand", "")
  display_name = hit.get("displayName", "")
  current_price = float(hit.get("price", 0))
  list_price = float(hit.get("listPrice", 0))
  condition_obj = hit.get("condition", {})
  condition = condition_obj.get("lvl1", "Used").split(" > ")[-1] if isinstance(condition_obj, dict) else "Used"
  sticker_objs = hit.get("sticker", [])
  stickers = ", ".join([s.get("name", "") for s in sticker_objs])
  
  prev = previous.get(product_id)
  prev_price = float(prev["current_price"]) if prev else None
  price_delta = current_price - prev_price if prev_price is not None else 0
  
  # Build price history
  price_history = []
  if prev and prev.get("price_history"):
    # Parse existing price history (stored as string in CSV)
    try:
      price_history = json.loads(prev["price_history"])
    except json.JSONDecodeError:
      price_history = []
  
  # Add previous price to history if price changed
  if prev_price is not None and price_delta != 0:
    price_history.append(f"{prev_price:.2f}")
  
  # Log price changes
  if price_delta != 0:
    print(f"💰 Price change for {display_name}: \033[38;5;208m${prev_price:.2f}\033[0m → \033[32m${current_price:.2f}\033[0m ({'+' if price_delta > 0 else ''}{price_delta:.2f})")
  
  if not prev:
    print(f"🆕 New item added: {display_name} at ${current_price:.2f}")
    new_items_list.append(product_id)


  return {
    "product_id": product_id,
    "brand": brand,
    "display_name": display_name,
    "current_price": f"{current_price:.2f}",
    "list_price": f"{list_price:.2f}",
    "condition": condition,
    "stickers": stickers,
    "date_added": prev["date_added"] if prev else today,
    "price_delta": f"{price_delta:.2f}" if prev_price is not None else "0.00",
    "price_history": json.dumps(price_history),
    "status": "Available",
    "date_sold": ""
  }

def mark_sold_items(previous: Dict[str, Dict], current_product_ids: set, today: str) -> List[Dict]:
  sold = []
  for product_id, item in previous.items():
    if product_id not in current_product_ids:
      if item['status'] != 'Sold':
        print(f"❌ Item sold: {item['display_name']} (was ${item['current_price']})")
        item['status'] = 'Sold'
        item['date_sold'] = today
      sold.append(item)
  return sold

if __name__ == "__main__":
  print("\nFavorite Stores:")
  for key, store in FAVORITE_STORES.items():
    print(f"{key}. {store}")
  store_choice = input("\nEnter store name or choose number from favorites: ").strip()
  
  if store_choice in FAVORITE_STORES:
    store_name = FAVORITE_STORES[store_choice]
  else:
    store_name = store_choice
  
  if not validate_store_name(store_name):
    print("Error: Store name is invalid. It can only contain letters and spaces.")
    exit(1)
  
  print("\nSelect a category:")
  for i, cat in enumerate(CATEGORY_MAP.keys(), 1):
    print(f"{i}. {cat}")
  
  category_choice = input("\nEnter category number (1-4): ").strip()
  category_options = list(CATEGORY_MAP.keys())
  
  try:
    category_index = int(category_choice) - 1
    if category_index < 0 or category_index >= len(category_options):
      raise ValueError
    category = category_options[category_index]
    category_filter = CATEGORY_MAP[category]
  except (ValueError, IndexError):
    print("Error: Invalid category selection.")
    exit(1)
  
  # Generate CSV filename based on store name and category
  csv_filename = f"{store_name.lower().replace(' ', '_')}_used_{category.lower()}.csv"
  
  today = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()
  previous_inventory = load_previous_inventory(csv_filename)

  try:
    hits = fetch_inventory(store_name, category_filter)
    if not hits:
      print(f"No results found for {store_name} in category {category}. Try a different store or category.")
      exit(1)
  except Exception as e:
    print("Error fetching data:", e)
    exit(1)

  current_inventory = []
  current_product_ids = set()
  new_product_ids = []

  for hit in hits:
    item = normalize_item(hit, previous_inventory, today, new_product_ids)
    current_inventory.append(item)
    current_product_ids.add(item["product_id"])

  sold_items = mark_sold_items(previous_inventory, current_product_ids, today)
  
  # Separate new items and existing items
  new_items = [item for item in current_inventory if item["product_id"] in new_product_ids]
  existing_items = [item for item in current_inventory if item["product_id"] not in new_product_ids]
  
  # Order: new items first, then existing items, then sold items
  full_inventory = new_items + existing_items + sold_items

  save_inventory(csv_filename, full_inventory)
  print(f"✅ Inventory updated and saved to {csv_filename} with {len(new_items)} new items, {len(existing_items)} existing items, and {len(sold_items)} sold items.")

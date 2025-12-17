# Guitar Center Inventory Tracker

A Python script that tracks used musical instrument inventory at Guitar Center stores. Monitor price changes, new arrivals, and sold items across multiple store locations and product categories.

## Description

The script uses an Algolia app ID and API key that is obtainable from Guitar Center's website. You can find this by executing a search for gear on guitarcenter.com, opening the Network tab in the Chrome developer console, and finding a query that looks like this: `queries?x-algolia-agent=Algolia%20for%20JavaScript%20(5.15.0)%3B%20Lite%20(5.15.0)%3B%20Browser%3B%20instantsearch.js%20(4.75.5)%3B%20react%20(18.3.1)%3B%20react-instantsearch%20(7.13.8)%3B%20react-instantsearch-core%20(7.13.8)%3B%20next.js%20(14.2.30)%3B%20JS%20Helper%20(3.22.5)...`

The `x-algolia-api-key` and `x-algolia-application-id` can be viewed in the payload of that query. Copy those values to your .env file before running the script.

The purpose of this script is to use Guitar Center's existing search functionality to generate a list of products that can be referenced in a future search. This allows the user to track which gear has been added or sold since the script was last run, and how prices have changed.

## Features

- **Multi-Store Support**: Track inventory across different Guitar Center locations
- **Category Filtering**: Monitor Guitars, Basses, Amplifiers, or Effects
- **Price History**: Track price changes over time with full historical data
- **Notifications**:
  - 🆕 New items added to inventory
  - 💰 Price changes (increases/decreases)
  - ❌ Items sold/removed from inventory
- **CSV Export**: All data saved to organized CSV files
- **Persistent Tracking**: Maintains history across multiple runs

## Prerequisites

- Python 3.9 or higher
- pip3 (Python package installer)

### Installing Python

#### macOS

1. **Using Homebrew (Recommended)**:

   ```bash
   # Install Homebrew if you don't have it
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install Python
   brew install python
   ```

2. **Using the Official Installer**:

   - Download the latest Python installer from [python.org/downloads](https://www.python.org/downloads/)
   - Run the `.pkg` file and follow the installation wizard
   - Python 3 and pip3 will be installed automatically

3. **Verify Installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Windows

1. **Download the Installer**:

   - Visit [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.x installer for Windows

2. **Run the Installer**:

   - **Important**: Check the box "Add Python to PATH" at the bottom of the installer
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**:

   ```bash
   python --version
   pip --version
   ```

   Note: On Windows, you may use `python` and `pip` instead of `python3` and `pip3`

## Installation

1. **Clone or download this repository**

2. **Install required dependencies**:

   ```bash
   pip3 install requests python-dotenv
   ```

3. **Set up environment variables**:

   Create a `.env` file in the project directory:

   ```env
   ALGOLIA_API_KEY=your_api_key_here
   ALGOLIA_APP_ID=your_app_id_here
   ```

## Usage

Run the script:

```bash
python guitar_inventory_tracker.py
```

The script generates a CSV file at the root level containing a list of gear. Keep this file - it will be referenced in future script runs and updated with price changes, new items, and sold items.

### Interactive Prompts

1. **Select Store**: Choose from favorite stores or enter a custom store name

   - Palm Desert
   - San Bernardino
   - Hollywood
   - Manhattan

2. **Select Category**: Choose what to track
   - Guitars
   - Basses
   - Amplifiers
   - Effects

### Output

The script generates a CSV file named: `{store}_used_{category}.csv`

Example: `palm_desert_used_guitars.csv`

### CSV Columns

- `product_id`: Unique product identifier
- `brand`: Manufacturer name
- `display_name`: Full product name
- `current_price`: Current listed price
- `list_price`: Original/MSRP price
- `price_history`: JSON array of previous prices
- `condition`: Item condition (e.g., Great, Good, Fair)
- `stickers`: Special labels/tags (e.g., Vintage, B-Stock)
- `date_added`: Timestamp when item first appeared
- `price_delta`: Change from previous price
- `status`: Available or Sold
- `date_sold`: Timestamp when item was sold (if applicable)

## How It Works

1. **Fetches** current inventory from Guitar Center's API
2. **Loads** previous inventory from CSV (if exists)
3. **Compares** current vs. previous to detect:
   - New items
   - Price changes
   - Sold items
4. **Saves** updated inventory with:
   - New items first
   - Existing items second
   - Sold items last

## Console Output Examples

```
🆕 New item added: Fender American Professional II Stratocaster at $1499.99
💰 Price change for Gibson Les Paul Standard: $2299.99 → $1999.99 (-300.00)
❌ Item sold: PRS Custom 24 (was $3499.99)
```

## Configuration

### Adding Favorite Stores

Edit the `FAVORITE_STORES` dictionary in the script:

```python
FAVORITE_STORES = {
  "1": "Palm Desert",
  "2": "San Bernardino",
  "3": "Your Store Name",
  # Add more stores...
}
```

### Timezone

The script uses Pacific Time (America/Los_Angeles). To change:

```python
today = datetime.datetime.now(ZoneInfo("Your/Timezone")).isoformat()
```

Time zone support will be added at a later date.

## File Structure

```
guitar-inventory-tracker/
├── guitar_inventory_tracker.py   # Main script
├── .env                          # API credentials (not tracked)
├── .gitignore                    # Ignore sensitive files
├── README.md                     # This file
└── *.csv                         # Generated inventory files
```

## Troubleshooting

### Import Error: requests

```bash
pip3 install requests
```

### Import Error: dotenv

```bash
pip3 install python-dotenv
```

### No Results Found

- Verify store name is spelled correctly (case-insensitive)
- Check that the store has used items in the selected category
- Try a different store or category

## License

This project is provided as-is for personal use.

## Contributing

Feel free to fork and submit pull requests for improvements.

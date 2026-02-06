# Gold & Currency Tracker

A simple dashboard for tracking gold prices from Bulgarian sellers and currency exchange rates. Data is automatically collected every 8 minutes and displayed through clean, interactive charts.

**Live Demo:** [https://todorgeorgiev05.github.io/gold_scrape/](https://todorgeorgiev05.github.io/gold_scrape/)

![Project Preview](https://img.shields.io/badge/status-active-success) ![Last Updated](https://img.shields.io/badge/updated-automatically-blue)

---

## 🌟 What Does This Do?

This project automatically tracks and displays:

- **Gold Prices**: Compare buy/sell prices from Bulgarian gold dealers
  - **TopGold**: 100g gold bars (Valcambi)
  - **Zlaten Rezerv**: 100g gold bars (Valcambi)
  - **Tavex**: 1g and 100g gold bars (Valcambi)
- **Currency Rates**: Live EUR exchange rates and conversion tool using European Central Bank data
  - Includes BGN (Bulgarian Lev) with fixed peg to EUR at 1.95583
- **Historical Charts**: View price trends over 7 days, 30 days, or 1 year
  - Smart outlier detection prevents chart distortion from data glitches
  - Hourly bucketing for smooth charts with thousands of data points

All data updates automatically every 8 minutes via GitHub Actions - no manual work needed!

---

## 🚀 Using the Live Site

### Gold Prices Dashboard

1. Go to the [Gold Prices page](https://todorgeorgiev05.github.io/gold_scrape/gold.html)
2. **Choose a time range**: Click `7D`, `1M`, or `1Y` buttons to see different periods
3. **Select what to view**: 
   - Pick a seller from the "Chart" dropdown (tavex • 1g, tavex • 100g, topgold • 100g, zlatenrezerv • 100g)
   - Choose to see buy prices, sell prices, or both
4. **Compare prices**: The table at the bottom shows the latest prices from all sellers, sorted by buy price

**Understanding the prices:**
- **Buy price**: What you pay to purchase gold from the seller
- **Sell price**: What the seller pays you if you sell gold back to them  
- **Spread**: The difference between buy and sell (lower spread = better deal)

### Currency Converter

1. Go to the [Currency page](https://todorgeorgiev05.github.io/gold_scrape/fx.html)
2. Enter the amount you want to convert
3. Select your currencies from the dropdowns (includes BGN, USD, EUR, GBP, CZK, and 25+ others)
4. Click **Convert** to see the result
5. Use **Swap** to quickly reverse the conversion

The chart below shows how EUR exchange rates have changed over the last 30 days.

**Note**: BGN is pegged to the Euro at a fixed rate of 1.95583 BGN per EUR.

---

## 💻 Running Locally

Want to run this on your own computer? Here's how:

### Prerequisites

You only need:
- A web browser (Chrome, Firefox, Edge, Safari)
- Python 3.8 or newer ([Download here](https://www.python.org/downloads/))
- A text editor (optional, for customization)

### Step 1: Download the Project

**Option A - Using Git**:
```bash
git clone https://github.com/todorgeorgiev05/gold_scrape.git
cd gold_scrape
```

**Option B - Download ZIP**:
1. Go to the [GitHub repository](https://github.com/todorgeorgiev05/gold_scrape)
2. Click the green "Code" button → "Download ZIP"
3. Extract the ZIP file to a folder
4. Open terminal/command prompt in that folder

### Step 2: Install Required Packages

```bash
pip install requests beautifulsoup4
```

This installs the tools needed to scrape gold prices from websites.

**Troubleshooting:**
- If `pip` doesn't work, try `pip3` or `python -m pip install requests beautifulsoup4`

### Step 3: Collect Initial Data

Run the scraper:

```bash
python scrape_all.py
```

You should see output like:
```
topgold_100g: buy=13730.0 sell=13542.0
zlatenrezerv_100g: buy=13717.01 sell=13474.59
tavex_1g: buy=154.0 sell=140.0
tavex_100g: buy=13786.0 sell=13548.0
```

This creates `gold_prices.csv` with current prices.

### Step 4: Build the Website Data

```bash
python scripts/build_site_data.py
```

You should see:
```
CSV rows: 4
JSON rows (last 365 days): 4
Generated site/data/history.json, latest.json, meta.json
```

### Step 5: Open the Website

For best results, run a local server to avoid CORS issues:

```bash
cd site
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

Or simply double-click: `site/index.html`

---

## 🔄 Keeping Data Updated

### Manual Updates

```bash
python scrape_all.py                    # Scrape latest prices
python scripts/build_site_data.py       # Update JSON files
```

### Automatic Updates (GitHub Actions)

The workflow file (`.github/workflows/scrape.yml`) automatically:
- Runs every 8 minutes
- Scrapes new prices
- Updates CSV and JSON files
- Commits changes to your repo
- Deploys to GitHub Pages

No setup needed - just push to GitHub!

---

## 📁 Project Structure

```
gold_scrape/
│
├── site/                          # Website files
│   ├── index.html                 # Home page
│   ├── gold.html                  # Gold dashboard
│   ├── fx.html                    # Currency converter
│   ├── assets/
│   │   └── style.css              # Styling
│   └── data/                      # Generated JSON files
│       ├── history.json           # Historical data
│       ├── latest.json            # Latest prices
│       └── meta.json              # Metadata
│
├── scripts/
│   └── build_site_data.py         # CSV → JSON converter
│
├── scrape_all.py                  # Main scraper
├── gold_prices.csv                # Raw data (not in repo)
│
└── .github/workflows/
    └── scrape.yml                 # Automation config
```

---

## 🛠️ How It Works

### Data Pipeline

```
Every 8 minutes:
  scrape_all.py
    ↓ Visits seller websites
    ↓ Extracts prices with BeautifulSoup
    ↓ Appends to gold_prices.csv
  
  build_site_data.py
    ↓ Reads CSV
    ↓ Filters last 365 days
    ↓ Validates data
    ↓ Generates JSON files
  
  GitHub Actions
    ↓ Commits changes
    ↓ Deploys to GitHub Pages
```

### Scraping Details

**TopGold** (topgold.bg):
- Selectors: `span.price-value.sell-price` and `span.price-value.buy-price`
- Note: Their HTML labels are swapped

**Zlaten Rezerv** (zlatenrezerv.bg):
- Buy: `span.woocommerce-Price-amount.amount bdi`
- Sell: First table row

**Tavex** (tavex.bg):
- Searches page text for Bulgarian labels:
  - "Стойност на продукта" = buy price
  - "Цена при обратно изкупуване" = sell price
- Looks for Euro (€) symbols
- Has fallback logic for text variations

Each scraper:
- Cleans extracted text
- Uses regex `\d+(?:[.,]\d+)?` to find numbers
- Converts commas to dots
- Returns `(buy, sell)` tuple

### Currency Data

Uses [Frankfurter API](https://www.frankfurter.app/):
- Live ECB exchange rates
- 30+ currencies
- No API key needed
- BGN manually added (fixed peg)

### Smart Features

**Outlier Detection**:
- IQR (Interquartile Range) method
- Removes extreme spikes
- Keeps charts readable

**Hourly Bucketing**:
- Groups by hour
- Reduces 31,000+ points to ~8,760
- Smooth, performant charts

---

## 🎨 Customization

### Change Colors

Edit `site/assets/style.css`:

```css
:root {
  --bg: #0b0f19;      /* Background */
  --card: #11182a;    /* Cards */
  --text: #e8eefc;    /* Text */
  --muted: #a9b5d1;   /* Muted text */
  --border: #2a355a;  /* Borders */
  --link: #9db4ff;    /* Links */
}
```

### Adjust Data Retention

Edit `scripts/build_site_data.py`:

```python
KEEP_DAYS = 365  # Change to 30, 90, 180, etc.
```

### Change Scraping Frequency

Edit `.github/workflows/scrape.yml`:

```yaml
schedule:
  - cron: "*/8 * * * *"   # Every 8 minutes
  # or
  - cron: "*/15 * * * *"  # Every 15 minutes  
  - cron: "0 * * * *"     # Every hour
```

Use [crontab.guru](https://crontab.guru/) to create schedules.

---

## 🐛 Troubleshooting

### "No data yet" on gold page

**Fix:**
```bash
python scrape_all.py
python scripts/build_site_data.py
```

### Charts not showing

**Fix:**
1. Open browser console (F12) for errors
2. Validate JSON: `python -m json.tool site/data/history.json`
3. Run local server: `cd site && python -m http.server 8000`

### Scraper returns None

**Cause:** Websites changed HTML structure.

**Fix:** Inspect HTML, update selectors in `scrape_all.py`

### GitHub Actions failing

**Fix:**
1. Settings → Actions → General
2. Enable "Read and write permissions"
3. Check Actions tab for error details

---

## 📊 Data Formats

### gold_prices.csv
```csv
timestamp,site,buy,sell
2026-02-06T17:35:54+03:00,tavex_1g,153.0,139.0
```

### history.json
```json
[{
  "timestamp": "2026-02-06T17:35:54+03:00",
  "seller": "tavex_1g",
  "buy_price": 153.0,
  "sell_price": 139.0
}]
```

### meta.json
```json
{
  "last_updated_iso": "2026-02-06T17:35:54+03:00",
  "points": 31584,
  "days_kept": 365,
  "sellers": ["tavex_1g", "tavex_100g", "topgold_100g", "zlatenrezerv_100g"]
}
```

---

## 🤝 Contributing

- **Report bugs**: Open GitHub issue
- **Suggest features**: Share ideas in issues
- **Submit code**: Fork, modify, PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 🙏 Credits

- **Data**: TopGold, Zlaten Rezerv, Tavex
- **Currency**: [Frankfurter API](https://www.frankfurter.app/)
- **Charts**: [Chart.js](https://www.chartjs.org/)
- **Scraping**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

---

## 📧 Questions?

1. Check [Troubleshooting](#-troubleshooting)
2. Search [GitHub Issues](https://github.com/todorgeorgiev05/gold_scrape/issues)
3. Open new issue with details

---

## 🚀 Future Ideas

- [ ] Add more gold sellers
- [ ] Price alerts (email/SMS)
- [ ] Mobile app
- [ ] Stock tracking
- [ ] Silver/platinum/palladium
- [ ] Price predictions
- [ ] CSV export from website
- [ ] LBMA comparison

---

**Made with ❤️ for Bulgarian gold buyers**

*31,584 data points and counting!*

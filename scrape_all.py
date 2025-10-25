import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

# ---------------------
# Sites to scrape
# ---------------------
SITES = {
    "tavex_1g": "https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/",
    "tavex_100g": "https://tavex.bg/zlato/100-grama-zlatno-kulche-valcambi/",
    "zlatenrezerv_100g": "https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/",
    "topgold_100g": "https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
NUM_RE = re.compile(r"(\d{1,5}(?:[ \u00A0,\.]\d{3})*(?:[.,]\d+)?)")

# ---------------------
# Parsing function
# ---------------------
def parse_price(text):
    if not text:
        return None
    text = text.replace("\u00A0", "").replace(" ", "").replace(",", ".")
    m = NUM_RE.search(text)
    return float(m.group(1)) if m else None

# ---------------------
# Scrapers
# ---------------------
def scrape_tavex(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    spans = [s for s in soup.find_all("span") if "лв" in s.get_text()]
    prices = [parse_price(s.get_text()) for s in spans if parse_price(s.get_text()) is not None]
    buy = prices[0] if len(prices) > 0 else None
    sell = prices[1] if len(prices) > 1 else None
    return buy, sell

def scrape_zlaten(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Buy price
    buy_span = soup.select_one("span.woocommerce-Price-amount.amount bdi")
    buy = parse_price(buy_span.get_text()) if buy_span else None
    
    # Sell price from table
    table = soup.find("table")
    rows = table.find_all("tr") if table else []
    price_row = rows[1] if len(rows) > 1 else None
    sell = parse_price(price_row.find_all("td")[0].get_text()) if price_row else None
    return buy, sell

def scrape_topgold(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Sell
    sell_span = soup.select_one("span.price-value.sell-price span.woocommerce-Price-amount")
    sell = parse_price(sell_span.get_text()) if sell_span else None
    # Buy
    buy_span = soup.select_one("span.price-value.buy-price span.woocommerce-Price-amount")
    buy = parse_price(buy_span.get_text()) if buy_span else None
    return buy, sell

# ---------------------
# Scrape all sites
# ---------------------
def scrape_all():
    now = datetime.now().isoformat(timespec="seconds")
    data = []
    for site, url in SITES.items():
        if "tavex" in site:
            buy, sell = scrape_tavex(url)
        elif "zlaten" in site:
            buy, sell = scrape_zlaten(url)
        elif "topgold" in site:
            buy, sell = scrape_topgold(url)
        else:
            buy, sell = None, None
        data.append({"timestamp": now, "site": site, "buy": buy, "sell": sell})
        print(f"{site}: BUY={buy}, SELL={sell}")
    return data

# ---------------------
# Save CSV
# ---------------------
def save_csv(data):
    filename = "gold_prices.csv"
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved CSV: {filename}")

# ---------------------
# Main
# ---------------------
if __name__ == "__main__":
    data = scrape_all()
    save_csv(data)

import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}

SITES = {
    "tavex_1g": "https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/",
    "tavex_100g": "https://tavex.bg/zlato/100-grama-zlatno-kulche-valcambi/",
    "zlatenrezerv_100g": "https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/",
    "topgold_100g": "https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/"
}

NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")

def parse_price(text):
    if not text:
        return None
    # Keep only leva (remove euro symbols)
    text = text.replace("\xa0", "").replace("лв", "").replace(",", ".").strip()
    m = NUM_RE.search(text)
    return float(m.group(0)) if m else None

# --- Tavex scraper (works for 1g and 100g) ---
def scrape_tavex(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find all spans containing "лв"
    spans = [s for s in soup.find_all("span") if "лв" in s.get_text()]
    prices = []
    for s in spans:
        price = parse_price(s.get_text())
        if price is not None:
            prices.append(price)
    buy = prices[0] if len(prices) > 0 else None
    sell = prices[1] if len(prices) > 1 else None
    return buy, sell

# --- ZlatenRezerv scraper ---
def scrape_zlatenrezerv(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Buy price
    buy_span = soup.select_one("span.woocommerce-Price-amount.amount bdi")
    buy = parse_price(buy_span.get_text()) if buy_span else None

    # Sell price from table
    table = soup.find("table")
    sell = None
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            tds = rows[1].find_all("td")
            if tds:
                sell = parse_price(tds[0].get_text())
    return buy, sell

# --- TopGold scraper ---
def scrape_topgold(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Sell price
    sell_span = soup.select_one("span.price-value.sell-price span.woocommerce-Price-amount")
    sell = parse_price(sell_span.get_text()) if sell_span else None

    # Buy price
    buy_span = soup.select_one("span.price-value.buy-price span.woocommerce-Price-amount")
    buy = parse_price(buy_span.get_text()) if buy_span else None

    return buy, sell

# --- Main scraper ---
def scrape_all():
    now = datetime.now().isoformat(timespec='seconds')
    data = []

    for site, url in SITES.items():
        if "tavex" in site:
            buy, sell = scrape_tavex(url)
        elif "zlatenrezerv" in site:
            buy, sell = scrape_zlatenrezerv(url)
        elif "topgold" in site:
            buy, sell = scrape_topgold(url)
        else:
            buy, sell = None, None

        print(f"{site} - BUY: {buy}, SELL: {sell}")
        data.append({
            "timestamp": now,
            "site": site,
            "url": url,
            "buy": buy,
            "sell": sell
        })
    return data

# --- Save CSV with timestamped filename ---
def save_csv(data):
    filename = f"gold_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved CSV: {filename}")

if __name__ == "__main__":
    all_data = scrape_all()
    save_csv(all_data)

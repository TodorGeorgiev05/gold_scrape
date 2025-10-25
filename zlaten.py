import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import csv

URL = "https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

NUM_RE = re.compile(r"\d+(?:\.\d+)?")  # matches numbers like 22766.98

def parse_price(text):
    if not text:
        return None
    # Remove non-breaking spaces and extra characters
    text = text.replace("\xa0", "").replace(",", ".").strip()
    m = NUM_RE.search(text)
    return float(m.group(0)) if m else None

def scrape_zlatenrezerv(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # --- Buy price ---
    buy_span = soup.select_one("span.woocommerce-Price-amount.amount bdi")
    buy = parse_price(buy_span.get_text()) if buy_span else None
    
    
    table = soup.find("table")
    rows = table.find_all("tr")
    
    # Second row contains the actual prices
    price_row = rows[1] if len(rows) > 1 else None
    if not price_row:
        return None, None
    
    tds = price_row.find_all("td")
    
    # Only sell price is available
    sell = parse_price(tds[0].get_text()) if len(tds) > 0 else None
    
    return buy, sell

def save_csv(data, filename="gold_prices.csv"):
    keys = data[0].keys()
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    now = datetime.now().isoformat(timespec='seconds')
    buy, sell = scrape_zlatenrezerv(URL)
    print(f"BUY: {buy}, SELL: {sell}")
    
    data = [{"timestamp": now, "site": "zlatenrezerv_100g", "buy": buy, "sell": sell}]
    save_csv(data)

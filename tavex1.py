import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

URL = "https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Regex to match numbers like 22828,00 or 22 828,00
NUM_RE = re.compile(r"(\d{1,5}(?:[ \u00A0,\.]\d{3})*(?:[.,]\d+)?)")

def parse_price(text):
    if not text:
        return None
    # Remove spaces/non-breaking spaces and convert comma to dot
    text = text.replace("\u00A0", "").replace(" ", "").replace(",", ".")
    m = NUM_RE.search(text)
    if m:
        return float(m.group(1))
    return None

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

    # Optional: pick first as "buy", second as "sell" (may not be accurate)
    buy = prices[0] if len(prices) > 0 else None
    sell = prices[1] if len(prices) > 1 else None

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
    buy, sell = scrape_tavex(URL)
    print(f"BUY: {buy}, SELL: {sell}")

    # Save to CSV
    data = [{"timestamp": now, "site": "tavex_1g", "buy": buy, "sell": sell}]
    save_csv(data)

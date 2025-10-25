import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime, timezone, timedelta

# URLs
SITES = {
    "topgold_100g": "https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/",
    "zlatenrezerv_100g": "https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/",
    "tavex_1g": "https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/",
    "tavex_100g": "https://tavex.bg/zlato/100-grama-zlatno-kulche-valcambi/"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
NUM_RE = re.compile(r"\d+(?:[\.,]\d+)?")  # matches numbers like 22766.98

# --- Parsing helper ---
def parse_price(text):
    if not text:
        return None
    text = text.replace("\xa0", "").replace("лв","").replace("BGN","").replace(",","." ).strip()
    m = NUM_RE.search(text)
    return float(m.group(0)) if m else None

# --- Scrapers for each site ---
def scrape_topgold(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    sell_span = soup.select_one("span.price-value.sell-price span.woocommerce-Price-amount")
    buy_span = soup.select_one("span.price-value.buy-price span.woocommerce-Price-amount")
    sell = parse_price(sell_span.get_text()) if sell_span else None
    buy = parse_price(buy_span.get_text()) if buy_span else None
    return buy, sell

def scrape_zlatenrezerv(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    buy_span = soup.select_one("span.woocommerce-Price-amount.amount bdi")
    buy = parse_price(buy_span.get_text()) if buy_span else None
    table = soup.find("table")
    sell = None
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            tds = rows[1].find_all("td")
            if len(tds) > 0:
                sell = parse_price(tds[0].get_text())
    return buy, sell

def scrape_tavex(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    spans = [s for s in soup.find_all("span") if "лв" in s.get_text()]
    prices = [parse_price(s.get_text()) for s in spans if parse_price(s.get_text()) is not None]
    buy = prices[0] if len(prices) > 0 else None
    sell = prices[1] if len(prices) > 1 else None
    return buy, sell

SCRAPERS = {
    "topgold_100g": scrape_topgold,
    "zlatenrezerv_100g": scrape_zlatenrezerv,
    "tavex_1g": scrape_tavex,
    "tavex_100g": scrape_tavex
}

# --- Save CSV ---
def save_csv(data, filename="gold_prices.csv"):
    keys = data[0].keys()
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

# --- Main ---
if __name__ == "__main__":
    bulgaria_tz = timezone(timedelta(hours=3))
    now = datetime.now(tz=bulgaria_tz).isoformat(timespec='seconds')
    all_data = []
    for site, url in SITES.items():
        buy, sell = SCRAPERS[site](url)
        print(f"{site} → BUY: {buy}, SELL: {sell}")
        all_data.append({"timestamp": now, "site": site, "buy": buy, "sell": sell})
    save_csv(all_data)

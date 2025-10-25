import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

URL = "https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

NUM_RE = re.compile(r"\d+(?:\.\d+)?")

def parse_price(text):
    if not text:
        return None
    text = text.replace("\xa0","").replace("лв","").strip()
    m = NUM_RE.search(text)
    return float(m.group(0)) if m else None

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

if __name__ == "__main__":
    buy, sell = scrape_topgold(URL)
    print(f"BUY: {buy}, SELL: {sell}")

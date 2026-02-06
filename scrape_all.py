import csv
import re
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup


SITES = {
    "topgold_100g": "https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/",
    "zlatenrezerv_100g": "https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/",
    "tavex_1g": "https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/",
    "tavex_100g": "https://tavex.bg/zlato/100-grama-zlatno-kulche-valcambi/",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")

BG_TZ = timezone(timedelta(hours=3))


def parse_price(text: str):
    if not text:
        return None

    cleaned = (
        text.replace("\xa0", "")
       # .replace("лв", "")
       # .replace("BGN", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )

    m = NUM_RE.search(cleaned)
    return float(m.group(0)) if m else None


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def scrape_topgold(url: str):
    soup = get_soup(url)

    # NOTE: names in the HTML are "buy-price" and "sell-price"
    buy_el = soup.select_one("span.price-value.sell-price span.woocommerce-Price-amount")
    sell_el = soup.select_one("span.price-value.buy-price span.woocommerce-Price-amount")

    buy = parse_price(buy_el.get_text()) if buy_el else None
    sell = parse_price(sell_el.get_text()) if sell_el else None
    return buy, sell


def scrape_zlatenrezerv(url: str):
    soup = get_soup(url)

    buy_el = soup.select_one("span.woocommerce-Price-amount.amount bdi")
    buy = parse_price(buy_el.get_text()) if buy_el else None

    sell = None
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            tds = rows[1].find_all("td")
            if tds:
                sell = parse_price(tds[0].get_text())

    return buy, sell


def scrape_tavex(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Tavex product pages usually show:
    # "Стойност на продукта" (you pay) and "Цена при обратно изкупуване" (they buy back)
    sell_price = None  # what you pay (we'll store as buy)
    buyback_price = None  # what they pay you (we'll store as sell)

    strings = list(soup.stripped_strings)

    def next_price_after(label):
        for i, s in enumerate(strings):
            if label.lower() in s.lower():
                # search a bit forward for something containing €
                for j in range(i + 1, min(i + 25, len(strings))):
                    if "€" in strings[j]:
                        return parse_price(strings[j])
        return None

    sell_price = next_price_after("Стойност на продукта")
    buyback_price = next_price_after("Цена при обратно изкупуване")

    # fallback: sometimes text changes slightly
    if sell_price is None:
        sell_price = next_price_after("Стойност на продукта (1 бр.)")
    if buyback_price is None:
        buyback_price = next_price_after("обратно изкупуване")

    # Map to your CSV meaning:
    # buy = price you pay (sell_price)
    # sell = price they pay (buyback_price)
    buy = sell_price
    sell = buyback_price

    return buy, sell

SCRAPERS = {
    "topgold_100g": scrape_topgold,
    "zlatenrezerv_100g": scrape_zlatenrezerv,
    "tavex_1g": scrape_tavex,
    "tavex_100g": scrape_tavex,
}


def append_csv(rows, filename="gold_prices.csv"):
    if not rows:
        return

    keys = ["timestamp", "site", "buy", "sell"]
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)


def main():
    now = datetime.now(tz=BG_TZ).isoformat(timespec="seconds")

    out = []
    for site, url in SITES.items():
        scraper = SCRAPERS.get(site)
        if not scraper:
            continue

        buy = sell = None
        try:
            buy, sell = scraper(url)
            print(f"{site}: buy={buy} sell={sell}")
        except requests.RequestException as e:
            print(f"{site}: request failed ({e})")
        except Exception as e:
            print(f"{site}: parse failed ({e})")

        out.append({
            "timestamp": now,
            "site": site,
            "buy": buy,
            "sell": sell,
        })

    append_csv(out)


if __name__ == "__main__":
    main()

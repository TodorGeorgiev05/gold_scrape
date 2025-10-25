from datetime import datetime
import csv

# Import your separate scraper files
from tavex1 import scrape_tavex as scrape_tavex1
from tavex100 import scrape_tavex as scrape_tavex100
from zlaten import scrape_zlatenrezerv
from topgold import scrape_topgold

def save_csv(data, filename="gold_prices_new.csv"):
    keys = data[0].keys()
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    now = datetime.now().isoformat(timespec='seconds')
    data = []

    # Tavex 1g
    buy, sell = scrape_tavex1("https://tavex.bg/zlato/1-gram-abonamentno-zlatno-kulche-tavex/")
    data.append({"timestamp": now, "site": "tavex_1g", "buy": buy, "sell": sell})
    print(f"tavex_1g - BUY: {buy}, SELL: {sell}")

    # Tavex 100g
    buy, sell = scrape_tavex100("https://tavex.bg/zlato/100-grama-zlatno-kulche-valcambi/")
    data.append({"timestamp": now, "site": "tavex_100g", "buy": buy, "sell": sell})
    print(f"tavex_100g - BUY: {buy}, SELL: {sell}")

    # ZlatenRezerv 100g
    buy, sell = scrape_zlatenrezerv("https://www.zlatenrezerv.bg/investicionno-zlato/zlatni-kyulcheta/100-grama-zlatni-kyulcheta/valcambi-100-grama-zlatno-kyulche/")
    data.append({"timestamp": now, "site": "zlatenrezerv_100g", "buy": buy, "sell": sell})
    print(f"zlatenrezerv_100g - BUY: {buy}, SELL: {sell}")

    # Topgold 100g
    buy, sell = scrape_topgold("https://topgold.bg/product/100-grama-zlatno-kyulche-valcambi/")
    data.append({"timestamp": now, "site": "topgold_100g", "buy": buy, "sell": sell})
    print(f"topgold_100g - BUY: {buy}, SELL: {sell}")

    # Save all to CSV
    save_csv(data)

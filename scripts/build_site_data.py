import csv
import json
import os
from datetime import datetime, timedelta, timezone


ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT, "gold_prices.csv")
OUT_DIR = os.path.join(ROOT, "site", "data")

KEEP_DAYS = 365


def is_bad(value) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() == "none"


def parse_ts(ts: str) -> datetime | None:
    """
    CSV timestamps are ISO strings (often with +03:00).
    If no timezone is present, assume UTC.
    """
    if not ts:
        return None

    ts = ts.strip()
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def read_csv(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            ts = (r.get("timestamp") or "").strip()
            site = (r.get("site") or "").strip()
            buy = r.get("buy")
            sell = r.get("sell")

            if not ts or not site:
                continue
            if is_bad(buy) or is_bad(sell):
                continue

            dt = parse_ts(ts)
            if not dt:
                continue

            try:
                buy_f = float(buy)
                sell_f = float(sell)
            except ValueError:
                continue

            rows.append({
                "timestamp": ts,     # keep original string for the frontend
                "ts_utc": dt,        # internal only, removed later
                "seller": site,
                "buy_price": buy_f,
                "sell_price": sell_f,
            })

    rows.sort(key=lambda x: x["ts_utc"])
    return rows


def filter_last_days(rows, days: int):
    if not rows:
        return []

    newest = rows[-1]["ts_utc"]
    cutoff = newest - timedelta(days=days)

    filtered = [r for r in rows if r["ts_utc"] >= cutoff]
    for r in filtered:
        r.pop("ts_utc", None)

    return filtered


def build_latest(history):
    latest_by_seller = {}
    for r in history:
        latest_by_seller[r["seller"]] = r

    latest = list(latest_by_seller.values())
    latest.sort(key=lambda x: x["buy_price"])
    return latest


def write_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_rows = read_csv(CSV_PATH)
    history = filter_last_days(all_rows, KEEP_DAYS)
    latest = build_latest(history)

    meta = {
        "last_updated_iso": history[-1]["timestamp"] if history else None,
        "points": len(history),
        "days_kept": KEEP_DAYS,
        "sellers": sorted({r["seller"] for r in history}),
    }

    write_json(os.path.join(OUT_DIR, "history.json"), history)
    write_json(os.path.join(OUT_DIR, "latest.json"), latest)
    write_json(os.path.join(OUT_DIR, "meta.json"), meta)

    print(f"CSV rows: {len(all_rows)}")
    print(f"JSON rows (last {KEEP_DAYS} days): {len(history)}")
    print("Generated site/data/history.json, latest.json, meta.json")


if __name__ == "__main__":
    main()

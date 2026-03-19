#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
import requests

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = DATA_DIR / "fmp-candles-cache.json"

FMP_SYMBOL = "XAUUSD"
FMP_INTERVAL = "15min"
FMP_KEY = os.getenv("FMP_API_KEY") or "WhZvG1WwRoLOE0vJQGsiS9b5XqTft5rK"


def to_ts(date_str: str):
    return int(datetime.fromisoformat(date_str.replace("Z", "+00:00")).timestamp())


def normalize_rows(rows):
    candles = []
    for row in rows:
        try:
            candles.append(
                {
                    "time": to_ts(row["date"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                }
            )
        except Exception:
            continue
    candles.sort(key=lambda x: x["time"])
    return candles


def fetch_fmp_full():
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{FMP_INTERVAL}/{FMP_SYMBOL}?apikey={FMP_KEY}"
    r = requests.get(url, timeout=40)
    r.raise_for_status()
    return normalize_rows(r.json())


def fetch_fmp_incremental(last_ts: int):
    # ขอข้อมูลเฉพาะช่วงใหม่ + เผื่อ 1 วันซ้อนทับกันเพื่อแก้ late candle/revision
    start_dt = datetime.fromtimestamp(last_ts, tz=timezone.utc) - timedelta(days=1)
    end_dt = datetime.now(timezone.utc) + timedelta(days=1)
    from_s = start_dt.strftime("%Y-%m-%d")
    to_s = end_dt.strftime("%Y-%m-%d")
    url = (
        f"https://financialmodelingprep.com/api/v3/historical-chart/{FMP_INTERVAL}/{FMP_SYMBOL}"
        f"?from={from_s}&to={to_s}&apikey={FMP_KEY}"
    )
    r = requests.get(url, timeout=40)
    r.raise_for_status()
    return normalize_rows(r.json())


def load_cache():
    if not CACHE_FILE.exists():
        return []
    try:
        payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        arr = payload.get("candles", [])
        arr.sort(key=lambda x: x["time"])
        return arr
    except Exception:
        return []


def save_cache(candles, prev_count):
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "symbol": FMP_SYMBOL,
        "interval": FMP_INTERVAL,
        "updatedAt": now,
        "count": len(candles),
        "from": candles[0]["time"] if candles else None,
        "to": candles[-1]["time"] if candles else None,
        "newAdded": max(0, len(candles) - prev_count),
        "candles": candles,
    }
    CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_candles(old, new):
    merged = {c["time"]: c for c in old}
    for c in new:
        merged[c["time"]] = c
    out = list(merged.values())
    out.sort(key=lambda x: x["time"])
    return out


def main():
    old = load_cache()

    if old:
        last_ts = old[-1]["time"]
        new = fetch_fmp_incremental(last_ts)
        mode = "incremental"
        # safety net: ถ้าได้ข้อมูลน้อยผิดปกติให้ fallback full
        if len(new) < 20:
            new = fetch_fmp_full()
            mode = "full-fallback"
    else:
        new = fetch_fmp_full()
        mode = "full-bootstrap"

    merged = merge_candles(old, new)
    save_cache(merged, len(old))
    print(f"cache updated ({mode}): old={len(old)} newFetched={len(new)} merged={len(merged)}")


if __name__ == "__main__":
    main()

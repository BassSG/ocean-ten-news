#!/usr/bin/env python3
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import requests

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FMP_API_KEY = "WhZvG1WwRoLOE0vJQGsiS9b5XqTft5rK"
FMP_SYMBOL = "XAUUSD"
FMP_INTERVAL = "15min"
FMP_LIMIT = 1000

ALERT_ENDPOINTS = {
    "TESTER": "https://script.googleusercontent.com/macros/echo?user_content_key=AWDtjMU2tCv4s5PpqbuXHtCbN_157DNearfX4ZyVrGxMGAxfBK5IAU5toUBhyKH4KuXQSW7uy_AM2p1qvk2WrdCZ9JcvsW00stCXbN9cxPY-notapivwv6B-fD8zEGCbsD2mgiLF7rlecDRw_fJHrar6lsqBtIqseKe30OHIxWeugjPnu0cacQB5AgTS9bIT_83dhF7HH2ypWF3SZ4iJ4zn1j6EBk1gapwOk-QSHKj8KdAwWF0iQlHIz07y5gXIkMFmMHQ6V6aD46znEstmrcA3RIkDGnPfpUuIv9RtrsW--9rkZS8VBsmSsRNNPJVvdGw&lib=M9P9-wXZJoeI92PYVy9wcPM683hYefgmI",
    "EBass": "https://script.google.com/macros/s/AKfycbwD0UqNEHdfUz3kzkL6od1h2GTIoNiPTO_gbonWKi9_lLDi6La-7VihSkr7DIcdHjvkIw/exec?mode=pull&token=271063",
    "EKlaETun": "https://script.google.com/macros/s/AKfycbyoQMFqut3uEJ_x1u4PkbtTax_IUkPtLP1RnSoKB9Qbj5G_JyJSKl5ZiF4ydRUCYQ/exec?mode=pull&token=271063",
}


def iso_to_ts(value: str):
    if not value:
        return None
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def fetch_fmp_candles():
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{FMP_INTERVAL}/{FMP_SYMBOL}?apikey={FMP_API_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    rows = r.json()
    candles = []
    for row in rows:
        try:
            t = int(datetime.fromisoformat(row["date"].replace("Z", "+00:00")).timestamp())
            candles.append({
                "time": t,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            })
        except Exception:
            continue
    candles.sort(key=lambda x: x["time"])
    return candles[-FMP_LIMIT:]


def fetch_alert_rows(source, url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not isinstance(rows, list):
        return []
    for row in rows:
        row["_source"] = source
    return rows


def group_runs(rows):
    buckets = {}
    for r in rows:
        run_id = r.get("runId") or "no-run"
        buckets.setdefault(run_id, []).append(r)
    out = []
    for run_id, items in buckets.items():
        items.sort(key=lambda x: x.get("createdAt") or x.get("ts") or "")
        created = items[0].get("createdAt") or items[0].get("ts")
        out.append({"runId": run_id, "createdAt": created, "items": items})
    out.sort(key=lambda x: x.get("createdAt") or "", reverse=True)
    return out


def extract_plan(run):
    lv = {}
    order_type = None
    created_at = run.get("createdAt")
    for r in run.get("items", []):
        at = str(r.get("alertType") or "").upper()
        tp = r.get("targetPrice")
        if order_type is None and r.get("type"):
            order_type = str(r.get("type")).upper().replace(" ", "_")
        if at in ("ENTRY", "SL", "TP1", "TPMOST") and tp is not None:
            try:
                lv[at] = float(tp)
            except Exception:
                pass
    if "ENTRY" not in lv or "SL" not in lv:
        return None
    return {
        "entry": lv.get("ENTRY"),
        "sl": lv.get("SL"),
        "tp1": lv.get("TP1"),
        "tpMost": lv.get("TPMOST") or lv.get("TP1"),
        "orderType": order_type or "BUY_LIMIT",
        "createdAt": created_at,
    }


def evaluate_trade(plan, candles):
    order_ts = iso_to_ts(plan.get("createdAt"))
    side_long = "BUY" in (plan.get("orderType") or "")

    entry = float(plan["entry"])
    sl = float(plan["sl"])
    tp1 = float(plan["tp1"]) if plan.get("tp1") is not None else None
    tp_most = float(plan["tpMost"]) if plan.get("tpMost") is not None else None

    stream = [c for c in candles if (order_ts is None or c["time"] >= order_ts)]
    if not stream:
        return {
            "status": "no-candles",
            "triggered": False,
            "triggeredAt": None,
            "closeReason": None,
            "closedAt": None,
            "timeInTradeMin": None,
            "mfe": 0.0,
            "mae": 0.0,
        }

    triggered = False
    triggered_at = None
    close_reason = None
    closed_at = None

    mfe = 0.0
    mae = 0.0

    for c in stream:
        high, low = c["high"], c["low"]
        if not triggered:
            if side_long and low <= entry:
                triggered = True
                triggered_at = c["time"]
            elif (not side_long) and high >= entry:
                triggered = True
                triggered_at = c["time"]

        if not triggered:
            continue

        # excursion tracking
        if side_long:
            mfe = max(mfe, high - entry)
            mae = min(mae, low - entry)
        else:
            mfe = max(mfe, entry - low)
            mae = min(mae, entry - high)

        # conservative close priority: SL first on same candle
        if side_long:
            if low <= sl:
                close_reason = "SL"
                closed_at = c["time"]
                break
            if tp_most is not None and high >= tp_most:
                close_reason = "TPMost"
                closed_at = c["time"]
                break
            if tp1 is not None and high >= tp1 and close_reason is None:
                close_reason = "TP1"
                closed_at = c["time"]
        else:
            if high >= sl:
                close_reason = "SL"
                closed_at = c["time"]
                break
            if tp_most is not None and low <= tp_most:
                close_reason = "TPMost"
                closed_at = c["time"]
                break
            if tp1 is not None and low <= tp1 and close_reason is None:
                close_reason = "TP1"
                closed_at = c["time"]

    status = "pending"
    if triggered:
        status = "triggered"
    if close_reason == "TP1":
        status = "tp1-hit"
    elif close_reason == "TPMost":
        status = "tpmost-hit"
    elif close_reason == "SL":
        status = "sl-hit"

    end_ts = closed_at or (stream[-1]["time"] if triggered else None)
    time_in_trade = None
    if triggered_at and end_ts:
        time_in_trade = max(0, int((end_ts - triggered_at) / 60))

    return {
        "status": status,
        "triggered": triggered,
        "triggeredAt": triggered_at,
        "closeReason": close_reason,
        "closedAt": closed_at,
        "timeInTradeMin": time_in_trade,
        "mfe": round(float(mfe), 3),
        "mae": round(float(mae), 3),
    }


def summarize(journal_items):
    total = len(journal_items)
    triggered = sum(1 for x in journal_items if x["result"]["triggered"])
    sl = sum(1 for x in journal_items if x["result"]["closeReason"] == "SL")
    tp1 = sum(1 for x in journal_items if x["result"]["closeReason"] == "TP1")
    tpmost = sum(1 for x in journal_items if x["result"]["closeReason"] == "TPMost")
    return {
        "totalOrders": total,
        "triggeredOrders": triggered,
        "slHits": sl,
        "tp1Hits": tp1,
        "tpMostHits": tpmost,
        "winRate": round(((tp1 + tpmost) / triggered * 100.0), 2) if triggered else 0.0,
    }


def main():
    now = datetime.now(timezone.utc).isoformat()
    candles = fetch_fmp_candles()

    all_items = []
    for source, endpoint in ALERT_ENDPOINTS.items():
        try:
            rows = fetch_alert_rows(source, endpoint)
        except Exception as e:
            all_items.append({
                "source": source,
                "error": str(e),
                "runs": []
            })
            continue

        runs = group_runs(rows)
        enriched_runs = []
        for run in runs:
            plan = extract_plan(run)
            if not plan:
                continue
            result = evaluate_trade(plan, candles)
            enriched_runs.append({
                "source": source,
                "runId": run["runId"],
                "createdAt": plan.get("createdAt"),
                "orderType": plan.get("orderType"),
                "entry": plan.get("entry"),
                "sl": plan.get("sl"),
                "tp1": plan.get("tp1"),
                "tpMost": plan.get("tpMost"),
                "result": result,
            })
        all_items.extend(enriched_runs)

    payload = {
        "generatedAt": now,
        "symbol": FMP_SYMBOL,
        "interval": FMP_INTERVAL,
        "candles": {
            "count": len(candles),
            "from": candles[0]["time"] if candles else None,
            "to": candles[-1]["time"] if candles else None,
        },
        "summary": summarize(all_items),
        "orders": all_items,
    }

    latest_file = DATA_DIR / "trade-journal-latest.json"
    latest_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    hist_file = DATA_DIR / "trade-journal-history.jsonl"
    with hist_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    print(f"Wrote {latest_file}")
    print(f"Appended {hist_file}")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()

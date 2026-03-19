#!/usr/bin/env python3
import json
import os
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FMP_API_KEY = os.getenv("FMP_API_KEY") or "WhZvG1WwRoLOE0vJQGsiS9b5XqTft5rK"
FMP_SYMBOL = "XAUUSD"
FMP_INTERVAL = "15min"
FMP_LIMIT = 1000
CANDLE_CACHE_FILE = DATA_DIR / "fmp-candles-cache.json"
ORDER_STATE_FILE = DATA_DIR / "order-state.json"
HISTORY_MAX_LINES = 5000

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


def request_json_with_retry(url: str, timeout: int = 30, max_retries: int = 3):
    last_err = None
    for i in range(max_retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            if i < max_retries - 1:
                time.sleep(2 ** i)
    raise last_err


def atomic_write_json(path: Path, payload: dict):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def validate_candles(candles):
    """Data Quality Gate for candle cache before publish."""
    issues = []
    if not candles:
        return False, ["candles-empty"]
    prev = None
    for c in candles:
        t = c.get("time")
        o, h, l, cl = c.get("open"), c.get("high"), c.get("low"), c.get("close")
        if not isinstance(t, int):
            issues.append("invalid-time")
            break
        if None in (o, h, l, cl):
            issues.append("null-ohlc")
            break
        if h < l or not (l <= o <= h) or not (l <= cl <= h):
            issues.append("ohlc-out-of-range")
            break
        if prev is not None and t <= prev:
            issues.append("non-monotonic-time")
            break
        prev = t
    return len(issues) == 0, issues


def fetch_fmp_candles():
    # ใช้ cache ถาวรเป็นหลัก เพื่อลด API cost
    if CANDLE_CACHE_FILE.exists():
        try:
            payload = json.loads(CANDLE_CACHE_FILE.read_text(encoding="utf-8"))
            arr = payload.get("candles", [])
            arr.sort(key=lambda x: x.get("time", 0))
            normalized = []
            for c in arr:
                try:
                    normalized.append({
                        "time": int(c["time"]),
                        "open": float(c["open"]),
                        "high": float(c["high"]),
                        "low": float(c["low"]),
                        "close": float(c["close"]),
                    })
                except Exception:
                    continue
            if normalized:
                return normalized[-FMP_LIMIT:]
        except Exception:
            pass

    # fallback: ดึงสดเฉพาะกรณี cache หาย/พัง
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{FMP_INTERVAL}/{FMP_SYMBOL}?apikey={FMP_API_KEY}"
    rows = request_json_with_retry(url)
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
    rows = request_json_with_retry(url)
    if not isinstance(rows, list):
        return []

    # de-dup rows (idempotency guard)
    seen = set()
    deduped = []
    for row in rows:
        rid = row.get("id") or f"{row.get('runId')}|{row.get('alertType')}|{row.get('targetPrice')}|{row.get('createdAt') or row.get('ts')}"
        if rid in seen:
            continue
        seen.add(rid)
        row["_source"] = source
        deduped.append(row)
    return deduped


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


def load_order_state():
    if not ORDER_STATE_FILE.exists():
        return {}
    try:
        return json.loads(ORDER_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_order_state(state):
    atomic_write_json(ORDER_STATE_FILE, state)


def apply_state_machine(prev_status, result):
    """State machine: pending -> triggered -> tp1-hit -> tpmost-hit/sl-hit (closed)
    closed state is terminal, no regression.
    """
    terminal = {"sl-hit", "tpmost-hit"}
    rank = {
        "pending": 0,
        "triggered": 1,
        "tp1-hit": 2,
        "tpmost-hit": 3,
        "sl-hit": 3,
        "no-candles": -1,
    }

    new_status = result.get("status", "pending")
    if prev_status in terminal:
        result["status"] = prev_status
        if prev_status == "sl-hit":
            result["closeReason"] = "SL"
        elif prev_status == "tpmost-hit":
            result["closeReason"] = "TPMost"
        return result

    if rank.get(new_status, 0) < rank.get(prev_status or "pending", 0):
        result["status"] = prev_status
        return result

    return result


def append_history_if_changed(path: Path, payload: dict):
    # idempotency guard: append only when content fingerprint changed
    compact = {
        "symbol": payload.get("symbol"),
        "interval": payload.get("interval"),
        "summary": payload.get("summary"),
        "orders": [
            {
                "orderKey": o.get("orderKey"),
                "status": (o.get("result") or {}).get("status"),
                "closeReason": (o.get("result") or {}).get("closeReason"),
                "triggeredAt": (o.get("result") or {}).get("triggeredAt"),
                "closedAt": (o.get("result") or {}).get("closedAt"),
            }
            for o in payload.get("orders", [])
        ],
    }
    fp = hashlib.sha256(json.dumps(compact, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    last_fp = None
    if path.exists():
        try:
            last_line = path.read_text(encoding="utf-8").splitlines()[-1]
            last_obj = json.loads(last_line)
            last_fp = (last_obj.get("meta") or {}).get("fingerprint")
        except Exception:
            last_fp = None

    if fp == last_fp:
        return False

    out = dict(payload)
    out["meta"] = {"fingerprint": fp}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")
    return True


def trim_history_file(path: Path, max_lines: int):
    if not path.exists() or max_lines <= 0:
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= max_lines:
            return
        keep = lines[-max_lines:]
        path.write_text("\n".join(keep) + "\n", encoding="utf-8")
    except Exception:
        # best-effort trim only; never break main flow
        pass


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
    ok, issues = validate_candles(candles)
    state = load_order_state()

    # Data Quality Gate: ถ้า candle ไม่ผ่าน ให้ใช้ snapshot ล่าสุดแทน
    if not ok:
        latest_file = DATA_DIR / "trade-journal-latest.json"
        if latest_file.exists():
            prev = json.loads(latest_file.read_text(encoding="utf-8"))
            prev["generatedAt"] = now
            prev["qualityGate"] = {"ok": False, "issues": issues, "fallback": "previous-latest"}
            atomic_write_json(latest_file, prev)
            print(json.dumps({"qualityGate": prev["qualityGate"]}, ensure_ascii=False))
            return

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

            order_key = f"{source}:{run['runId']}"
            result_live = evaluate_trade(plan, candles)
            prev = state.get(order_key, {})
            prev_status = prev.get("status")
            result = apply_state_machine(prev_status, result_live)

            # persist current state snapshot per order
            state[order_key] = {
                "status": result.get("status"),
                "closeReason": result.get("closeReason"),
                "updatedAt": now,
                "triggeredAt": result.get("triggeredAt"),
                "closedAt": result.get("closedAt"),
            }

            enriched_runs.append({
                "source": source,
                "runId": run["runId"],
                "orderKey": order_key,
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
        "qualityGate": {"ok": True, "issues": []},
        "candles": {
            "count": len(candles),
            "from": candles[0]["time"] if candles else None,
            "to": candles[-1]["time"] if candles else None,
        },
        "summary": summarize(all_items),
        "orders": all_items,
    }

    latest_file = DATA_DIR / "trade-journal-latest.json"
    atomic_write_json(latest_file, payload)

    save_order_state(state)

    hist_file = DATA_DIR / "trade-journal-history.jsonl"
    appended = append_history_if_changed(hist_file, payload)
    trim_history_file(hist_file, HISTORY_MAX_LINES)

    print(f"Wrote {latest_file}")
    print(f"History append: {'yes' if appended else 'skip (no state change)'}")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()

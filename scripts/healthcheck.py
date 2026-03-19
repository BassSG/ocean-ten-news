#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT = DATA / "system-health.json"

FMP_CACHE = DATA / "fmp-candles-cache.json"
JOURNAL = DATA / "trade-journal-latest.json"
ORDER_STATE = DATA / "order-state.json"

MAX_FMP_STALE_MIN = 90
MAX_JOURNAL_STALE_MIN = 90


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def age_min(dt):
    if not dt:
        return None
    return int((datetime.now(timezone.utc) - dt).total_seconds() // 60)


def main():
    now = datetime.now(timezone.utc)
    issues = []

    fmp = read_json(FMP_CACHE)
    jr = read_json(JOURNAL)
    st = read_json(ORDER_STATE)

    fmp_updated = parse_iso((fmp or {}).get("updatedAt"))
    jr_updated = parse_iso((jr or {}).get("generatedAt"))

    fmp_age = age_min(fmp_updated)
    jr_age = age_min(jr_updated)

    if not fmp:
        issues.append("missing:fmp-candles-cache.json")
    if not jr:
        issues.append("missing:trade-journal-latest.json")
    if st is None:
        issues.append("missing:order-state.json")

    if fmp_age is None or fmp_age > MAX_FMP_STALE_MIN:
        issues.append(f"stale:fmp-cache>{MAX_FMP_STALE_MIN}m")
    if jr_age is None or jr_age > MAX_JOURNAL_STALE_MIN:
        issues.append(f"stale:trade-journal>{MAX_JOURNAL_STALE_MIN}m")

    payload = {
        "checkedAt": now.isoformat(),
        "ok": len(issues) == 0,
        "issues": issues,
        "freshnessMinutes": {
            "fmpCache": fmp_age,
            "tradeJournal": jr_age,
        },
        "counts": {
            "fmpCandles": (fmp or {}).get("count"),
            "ordersInLatestJournal": len((jr or {}).get("orders", [])) if jr else None,
            "trackedOrderStates": len(st.keys()) if isinstance(st, dict) else None,
        },
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False))
    if not payload["ok"]:
        sys.exit(2)


if __name__ == "__main__":
    main()

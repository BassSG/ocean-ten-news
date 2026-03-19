# Ocean Ten News — Rollback Baseline

## Primary system baseline (user-confirmed)
- Date: 2026-03-19
- Purpose: Main production baseline for order-visual system (FMP candles + endpoint overlays + trigger/SL/TP visual flow)
- Commit: `8378e76`
- Git tag: `stable/order-system-baseline-20260319`

## Rollback rule
If future changes break behavior, rollback target is:
1. `stable/order-system-baseline-20260319` (preferred)
2. commit `8378e76`

## User intent summary
This baseline is designated as the **main system version**. Future backend trigger-history enhancements should preserve this behavior and be reversible to this baseline.

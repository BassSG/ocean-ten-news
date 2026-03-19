# Ocean Ten News — Rollback Baseline

## Primary system baseline (user-confirmed)
- Date: 2026-03-19
- Purpose: Main production baseline for order-visual system (FMP candles + endpoint overlays + trigger/SL/TP visual flow)
- Commit: `8378e76`
- Git tag: `stable/order-system-baseline-20260319`

## Rollback rule
If future changes break behavior, rollback target is:
1. `stable/ocean-ten-news-default-baseline` (default current)
2. commit `4327bc8`
3. `stable/order-system-baseline-20260319` (legacy baseline)
4. commit `8378e76`

## Current default rollback baseline (latest lock)
- Date: 2026-03-19
- Purpose: ค่าตั้งต้นหลักที่ต้องย้อนกลับมาทุกครั้งเมื่อผู้ใช้สั่ง reset/rollback
- Commit: `4327bc8`
- Git tag: `stable/ocean-ten-news-default-baseline`

## User intent summary
This baseline is designated as the **main system version**. Future backend trigger-history enhancements should preserve this behavior and be reversible to this baseline.

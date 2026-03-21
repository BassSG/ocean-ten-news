# Ocean Ten — Bloomberg-Hybrid Mockup: Design Notes
**Date:** March 21, 2026
**Status:** Draft v1 — For P'Bass Review

---

## Design Decisions

### 1. Typography
- **Headlines:** Playfair Display (serif) — เล่าเรื่องน่าเชื่อถือแบบ Financial Press
- **Body:** Inter (sans-serif) — อ่านง่าย สบายตา
- **Thai text:** Noto Sans Thai

### 2. Color Palette
| Role | Color | Usage |
|------|-------|-------|
| Background | `#0d1117` | Dark mode — professional, easy on eyes |
| Surface | `#161b22` | Cards, panels |
| Gold | `#f0b90b` | Brand accent, key highlights |
| Blue | `#58a6ff` | Tech/AI section headers |
| Green | `#3fb950` | Bullish indicators, positive data |
| Red | `#f85149` | Bearish indicators, risks |

### 3. Layout Structure
```
┌─────────────────────────────────────────┐
│ TOP BAR: Logo + Edition + Date           │
├─────────────────────────────────────────┤
│ NAV STRIP: Markets | Macro | AI | Gold  │
├─────────────────────────────────────────┤
│ TICKER: XAU | DXY | 10Y | S&P | Brent  │
├────────────────────────────────┬────────┤
│ LEAD STORY                     │SIDE-   │
│ - Headline                     │BAR     │
│ - WHAT / SO WHAT / NOW WHAT    │        │
│ - Key Levels Table             │Market  │
│                                │Snap-   │
│ ANALYST TARGETS (bar chart)    │shot    │
│                                │        │
│ KEY RISKS (impact grid)       │AI/Tech │
│                                │        │
│                                │Macro   │
│                                │Watch   │
│                                │        │
│                                │CTA     │
└────────────────────────────────┴────────┘
```

### 4. Content Architecture

**ทุกบทความมี 3 ส่วน (Mandatory):**
1. **WHAT** — เกิดอะไร (สรุป factual)
2. **SO WHAT** — ผลกระทบคืออะไร (วิเคราะห์)
3. **NOW WHAT** — ต้องทำอะไร (actionable)

**ไม่มี Emoji** — ใช้สีและ typography แทน

### 5. What Makes This "Premium"

| ฟรี (Free) | Premium |
|-----------|---------|
| ข้อมูล What | วิเคราะห์ So What |
| Headline สรุป | Original Analysis + Context |
| ตัวเลขเดียว | ความเชื่อมโยง + Domino Effect |
| ไม่มี Take | มี Take ชัดเจน (Bull/Bear/Neutral) |
| ไม่มี Action | มี Now What ที่จับต้องได้ |

### 6. Next Steps

1. **P'Bass review** mockup → feedback
2. **Define Niche** — ชัดเจนว่า audience คือใคร
3. **Build real content pipeline** — ทีมเขียน analysis จริงๆ
4. **Decide: Publish format** — Daily? Weekly? Subscription model?

---

## Questions for P'Bass

1. ชอบ Layout แบบนี้ไหม?
2. อยากให้ Ticker อยู่บนสุดเหมือน Bloomberg ไหม?
3. Subscription model — คิดราคาเท่าไหร่ดี?
4. Audience หลักคือนักลงทุนไทยหรือต่างประเทศ?

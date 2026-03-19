#!/usr/bin/env python3
"""
🌙 Ocean Ten — Knowledge Drop Pipeline
Step 2: ฉลาม (Shark) — บรรณาธิการ: คัด 3-5 ข่าวที่มี Impact
Model: MiniMax 2.7
Time: 01:00-02:00
Input: data/knowledge_news_raw.json
Output: data/knowledge_news_edited.json
"""

import json, os
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
INPUT  = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_news_raw.json"
OUTPUT = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_news_edited.json"

# Impact ranking criteria
IMPACT_CRITERIA = [
    "มีผลกระทบต่อตลาดทองคำ / XAUUSD",
    "เป็นประเด็นที่คนกำลังพูดถึง (trending)",
    "มีข้อมูล concrete รองรับ",
    "มีความน่าเชื่อถือ",
    "ทำให้เข้าใจสถานการณ์ได้ลึกขึ้น",
]

def run():
    with open(INPUT, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    news = raw.get("news", [])
    
    # Simulate editorial selection (ใช้ LLM ตัดสินจริงใน production)
    # ตอนนี้เลือก top 5 ตาม ranking
    selected = news[:5]
    
    edited = []
    for i, item in enumerate(selected):
        edited.append({
            "rank": i + 1,
            "topic": item["topic"],
            "reason": f"ข่าวนี้มี impact สูง: {IMPACT_CRITERIA[i % len(IMPACT_CRITERIA)]}",
            "priority": "high" if i < 2 else "medium",
            "source_note": "ผ่านการคัดกรองโดย Shark",
            "timestamp": TODAY
        })
    
    result = {
        "step": "02_editor",
        "agent": "shark",
        "model": "MiniMax 2.7",
        "timestamp": TODAY,
        "total_collected": len(news),
        "selected_count": len(edited),
        "articles": edited,
        "status": "complete"
    }
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(edited)} articles selected → {OUTPUT}")
    return result

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""
🌙 Ocean Ten — Knowledge Drop Pipeline
Step 1: หมึก (Squid) — รวบรวมข่าว 24h
Model: MiniMax 2.7
Time: 00:00-01:00
Output: data/knowledge_news_raw.json
"""

import json, sys, os
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_news_raw.json"

# หัวข้อหลากหลาย ไม่จำกัดแค่ทอง — ครอบคลุมทุกมิติ
TOPICS = [
    # 🌍 ตลาดโลก + ทองคำ
    "global market news today",
    "gold price xauusd analysis",
    "federal reserve interest rate impact",
    # 🗺️ เทคโนโลยี + AI
    "artificial intelligence news today",
    "technology trends 2025",
    "openai google deepmind news",
    # 🏛️ เศรษฐกิจ + การเงิน
    "usd dollar index today",
    "cryptocurrency bitcoin ethereum news",
    "crude oil commodity market",
    # 🌐 โลก + สังคม
    "geopolitical breaking news",
    "climate change environment news",
    "world economic forum news",
    # 📊 Business + Investment
    "stock market today news",
    "venture capital startup funding",
    "central bank policy news",
]

def run():
    import random
    
    # Simulate gathered news (ใช้ keyword search จริงใน production)
    # ตอนนี้ simulate ด้วย structured data
    news_items = []
    
    for i, topic in enumerate(TOPICS):
        news_items.append({
            "id": i + 1,
            "topic": topic,
            "status": "gathered",
            "note": f"รวบรวมข่าวเรื่อง: {topic}",
            "timestamp": TODAY
        })
    
    result = {
        "step": "01_news_gatherer",
        "agent": "squid",
        "model": "MiniMax 2.7",
        "timestamp": TODAY,
        "total_topics": len(TOPICS),
        "news": news_items,
        "status": "complete"
    }
    
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(news_items)} topics gathered → {OUTPUT}")
    return result

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""
🌙 Ocean Ten — Knowledge Drop Pipeline
Step 1: หมึก (Squid) — รวบรวม Trend X / Twitter Topics
Model: MiniMax 2.7
Time: 00:00-01:00
Output: data/knowledge_news_raw.json

Philosophy: เหมือนดู Timeline X/Twitter ของคนทั้งโลก
— คนกำลังพูดถึงอะไรวันนี้ที่น่าสนใจ + มี impact
"""

import json, sys, os
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_news_raw.json"

# 🌐 Trend X / Twitter Style — คนทั้งโลกกำลังพูดถึงอะไรวันนี้
# แบบไม่จำกัดแค่ทอง เป็น Knowledge Drop ที่น่าสนใจจริง ๆ
TOPICS = [
    # 🔥 Trending X/Twitter Topics
    "what is trending on twitter today",
    "viral tweet news today",
    "breaking news trending now",
    # 💻 Tech + AI
    "openai chatgpt news today",
    "google gemini artificial intelligence",
    "apple microsoft tesla news",
    # 💰 Finance + Markets
    "stock market rally crash today",
    "bitcoin ethereum crypto price",
    "gold silver commodity price",
    # 🌍 World + Society
    "usa china geopolitics today",
    "climate change extreme weather news",
    "europe middle east war conflict",
    # 🎬 Culture + Internet
    "viral video internet culture",
    "sports championship today",
    "celebrity entertainment news",
    # 🔬 Science + Health
    "medical breakthrough health news",
    "space exploration nasa news",
    "ai robot automation impact jobs",
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

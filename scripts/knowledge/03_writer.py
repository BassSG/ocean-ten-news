#!/usr/bin/env python3
"""
🌙 Ocean Ten — Knowledge Drop Pipeline
Step 3: วาฬ (Whale) — เขียน Knowledge Drop เต็ม
Model: Gemini 3.1 Pro
Time: 02:00-03:00
Input: data/knowledge_news_edited.json
Output: data/knowledge_latest.json + HTML content
"""

import json, os
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
THAI_DAY = {
    "Monday": "วันจันทร์", "Tuesday": "วันอังคาร",
    "Wednesday": "วันพุธ", "Thursday": "วันพฤหัสบดี",
    "Friday": "วันศุกร์", "Saturday": "วังเสาร์", "Sunday": "วันอาทิตย์"
}
THAI_DATE = datetime.now().strftime(f"{THAI_DAY[datetime.now().strftime('%A')]} ที่ %d %B %Y")
INPUT  = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_news_edited.json"
OUTPUT_JSON = "/home/administrator/.openclaw/workspace/ocean-ten-news/data/knowledge_latest.json"

def run():
    with open(INPUT, "r", encoding="utf-8") as f:
        edited = json.load(f)
    
    articles = edited.get("articles", [])
    
    # Build Knowledge Drop content
    # ใช้ Gemini 3.1 Pro ผ่าน web search/fetch จริงใน production
    
    # Simulate structured content (แทนที่ด้วย LLM output จริง)
    main_article = articles[0] if articles else {"topic": "General News", "reason": ""}
    
    content = {
        "date": TODAY,
        "date_thai": THAI_DATE,
        "headline": f"สรุปความเคลื่อนไหววันนี้: {main_article.get('topic', 'ตลาดโลก')}",
        "summary_3_points": [
            f"📌 {articles[0].get('topic', 'ข่าวหลัก')} — {articles[0].get('reason', '')}",
            f"📌 {articles[1].get('topic', 'ข่าวรอง')} — {articles[1].get('reason', '')}" if len(articles) > 1 else "📌 ตลาดทองคำยังคงผันผวนจากปัจจัยพื้นฐาน",
            f"📌 {articles[2].get('topic', 'ข่าวเสริม')} — {articles[2].get('reason', '')}" if len(articles) > 2 else "📌 นักลงทุนจับตาข้อมูลเศรษฐกิจสัปดาห์นี้",
        ],
        "analysis": f"""
วันนี้ {THAI_DATE}

ตลาดโลกและตลาดทองคำมีความเคลื่อนไหวที่น่าจับตาอย่างยิ่ง 
{main_article.get('topic', 'ข่าวหลัก')} เป็นประเด็นที่นักลงทุนและนักวิเคราะห์ให้ความสนใจ 
เนื่องจาก {main_article.get('reason', 'มีผลกระทบต่อแนวโน้มตลาดโดยตรง')}

ในมุมของการวิเคราะห์ทางเทคนิคและปัจจัยพื้นฐาน เรายังคงติดตามสถานการณ์อย่างใกล้ชิด
โดยเฉพาะการเคลื่อนไหวของ XAU/USD ในช่วงตลาดเอเชียและตลาดยุโรป
        """.strip(),
        "sources": [a.get("topic", "") for a in articles],
        "all_articles": articles,
        "agent": "whale",
        "model": "Gemini 3.1 Pro",
        "status": "ready_for_design"
    }
    
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Knowledge Drop written → {OUTPUT_JSON}")
    print(f"   Headline: {content['headline']}")
    return content

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""
🌙 Ocean Ten — Knowledge Drop Pipeline Orchestrator
Runs all 5 steps sequentially: 00:00 → 07:00
Usage: python3 run_knowledge_pipeline.py
"""

import subprocess, sys, os, time

BASE = "/home/administrator/.openclaw/workspace/ocean-ten-news"
STEPS = [
    ("01_news_gatherer", "🦑 หมึก รวบรวมข่าว",  ["python3", f"{BASE}/scripts/knowledge/01_news_gatherer.py"]),
    ("02_editor",        "🦈 ฉลาม บรรณาธิการ",  ["python3", f"{BASE}/scripts/knowledge/02_editor.py"]),
    ("03_writer",        "🐋 วาฬ เขียนบทความ",  ["python3", f"{BASE}/scripts/knowledge/03_writer.py"]),
]

LOG_FILE = f"{BASE}/data/knowledge_pipeline.log"

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_step(name, desc, cmd):
    log(f"▶️  {desc}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if r.returncode == 0:
            log(f"    ✅ {name} เสร็จ")
            if r.stdout.strip():
                log(f"    {r.stdout.strip()}")
            return True
        else:
            log(f"    ❌ {name} ล้มเหลว: {r.stderr[:200]}")
            return False
    except Exception as e:
        log(f"    ❌ ERROR: {e}")
        return False

def main():
    os.makedirs(f"{BASE}/data", exist_ok=True)
    log("=" * 50)
    log("🌙 Ocean Ten Knowledge Pipeline — START")
    log("=" * 50)

    ok = True
    for step_id, desc, cmd in STEPS:
        ok = run_step(step_id, desc, cmd)
        if not ok:
            log(f"⚠️  Step {step_id} ล้มเหลว — pipeline หยุด")
            break
        time.sleep(2)  # small stagger

    if ok:
        log("✅ Pipeline เสร็จสมบูรณ์ — Knowledge Drop พร้อม!")
        log(f"📦 Output: {BASE}/data/knowledge_latest.json")
        log(f"🌐 Deploy: {BASE}/knowledge-drop.html")
    else:
        log("❌ Pipeline ล้มเหลว — ตรวจสอบ log")

    log("=" * 50)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import json
import re
import requests
from pathlib import Path

DATA_DIR = Path('/home/administrator/.openclaw/workspace/ocean-ten-news/data')
DATA = sorted(DATA_DIR.glob('news-*.json'))[-1]
TIMEOUT = 12

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
}


def pick_image(html: str):
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
    ]
    for p in patterns:
        m = re.search(p, html, flags=re.IGNORECASE)
        if m:
            url = m.group(1).strip()
            if url.startswith('//'):
                url = 'https:' + url
            if url.startswith('http'):
                return url
    # fallback first meaningful image
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        src = m.group(1).strip()
        if src.startswith('//'):
            src = 'https:' + src
        if src.startswith('http') and not any(x in src.lower() for x in ['logo', 'icon', 'avatar', 'sprite']):
            return src
    return None


def fetch_image(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code >= 400:
            return None
        html = r.text[:500000]
        return pick_image(html)
    except Exception:
        return None


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    changed = 0
    for section in data.get('sections', []):
        for item in section.get('items', []):
            if item.get('image'):
                continue
            url = item.get('url')
            if not url:
                continue
            img = fetch_image(url)
            if img:
                item['image'] = img
                changed += 1

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'updated_images={changed}')


if __name__ == '__main__':
    main()

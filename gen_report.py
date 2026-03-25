#!/usr/bin/env python3
"""
Premium Tech/AI Report Generator for ocean-ten-news
Reads insights_data.json and generates tech-ai-report.html
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ── Load data ──────────────────────────────────────────────────────────────
with open('data/insights_data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

insights = raw if isinstance(raw, list) else raw.get('insights', [])

COMPANY_EMOJI = {
    'openai': '🤖', 'google': '🔍', 'nvidia': '🎮',
    'apple': '🍎', 'china': '🐉', 'amd': '🔴',
    'microsoft': '🌐', 'anthropic': '🧠', 'apple-google': '🍎🔍',
    'usa': '🇺🇸', 'eu': '🇪🇺', 'asia': '🌏',
}

IMPACT_COLORS = {'high': ('HIGH', 'high', 'rgba(244,63,94,.15)', '#f43f5e'),
                 'medium': ('MEDIUM', 'medium', 'rgba(249,115,22,.12)', '#f97316'),
                 'low': ('LOW', 'low', 'rgba(16,185,129,.12)', '#10b981')}

def esc(s):
    if not s: return ''
    return (str(s)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;'))

def insight_card(item, rank):
    idx   = item.get('id', f'insight-{rank}')
    emoji = COMPANY_EMOJI.get(item.get('company', ''), '📡')
    imp   = item.get('impact', 'medium')
    imp_label, imp_cls, imp_bg, imp_color = IMPACT_COLORS.get(imp, IMPACT_COLORS['medium'])
    why_preview = esc(item.get('why_matters', ''))[:130]

    # Category tag colour
    cat = item.get('category', 'ai').upper()
    tag_color = {'ai': 'rgba(6,182,212,.12)#06b6d4', 'macro': 'rgba(240,185,11,.12)#f0b90b',
                 'chip': 'rgba(168,85,247,.12)#a855f7', 'robotics': 'rgba(16,185,129,.12)#10b981'}.get(item.get('category', 'ai'), 'rgba(6,182,212,.12)#06b6d4')
    tc_bg, tc_color = tag_color.split('#')

    html = f'<div class="insight-card {imp_cls}-impact" id="{idx}">\n'
    html += '<div class="particle-container"><div class="particle"></div><div class="particle"></div>'
    html += '<div class="particle"></div><div class="particle"></div><div class="particle"></div>'
    html += '<div class="particle"></div></div>\n'
    html += f'<div class="insight-header"><div class="insight-header-left">'
    html += f'<div class="insight-rank">{rank}</div>'
    html += f'<div class="company-badge">{emoji}</div></div>'
    html += '<div style="display:flex;gap:8px;align-items:center">'
    html += f'<span class="insight-tag" style="background:{tc_bg};color:{tc_color};border:1px solid {tc_bg}">{cat}</span>'
    html += f'<span class="impact-badge {imp_cls}"><span class="impact-dot"></span>{imp_label}</span>'
    html += '</div></div>\n'
    html += f'<div class="insight-headline">{esc(item.get("title",""))}</div>\n'
    html += f'<div class="insight-source">{esc(item.get("source","ไม่ระบุแหล่งที่มา"))}</div>\n'

    for tier, cls, label in [
        ('what', 'tier-what', 'What'),
        ('why_matters', 'tier-why', 'Why It Matters'),
        ('so_what', 'tier-so', 'So What'),
        ('now_what', 'tier-now', 'Now What'),
    ]:
        val = item.get(tier, '')
        if val:
            body = f'<strong>{esc(val)}</strong>' if tier == 'so_what' else esc(val)
            html += f'<div class="tier-block"><div class="tier-label {cls}">{label}</div>'
            html += f'<div class="tier-body">{body}</div></div>\n'

    html += '<div class="why-preview"><div class="why-preview-label">💡 Why It Matters</div>'
    html += f'<div class="why-preview-text">{why_preview}</div></div>\n'
    html += '</div>\n\n'
    return html

def toc_item(item, rank):
    idx   = item.get('id', f'insight-{rank}')
    emoji = COMPANY_EMOJI.get(item.get('company', ''), '📡')
    imp   = item.get('impact', 'medium')
    imp_cls = imp
    return (f'<a class="toc-item" href="#{idx}">\n'
            f'<div class="toc-rank">{rank}</div>'
            f'<div class="toc-company">{emoji}</div>'
            f'<div class="toc-text"><div class="toc-label">{esc(item.get("title",""))}</div></div>'
            f'<span class="toc-impact {imp_cls}">{imp_cls}</span></a>\n\n')

# ── Build HTML sections ───────────────────────────────────────────────────
insights_html = ''.join(insight_card(item, i+1) for i, item in enumerate(insights))
toc_html      = ''.join(toc_item(item, i+1)       for i, item in enumerate(insights))

# ── Read template ────────────────────────────────────────────────────────
with open('tech-ai-report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace insights section
start = html.find('<div id="insightsList">')
end   = html.find('</div>\n</section>', start) + len('</div>\n</section>')
if start != -1 and end > start:
    html = html[:start] + '<div id="insightsList">\n' + insights_html + html[end:]
else:
    print('WARNING: could not find insightsList marker', file=sys.stderr)

# Replace TOC
start_toc = html.find('<div class="toc-title">📑 สารบัญ</div>')
end_toc   = html.find('</div>\n</aside>', start_toc) + len('</div>\n</aside>')
if start_toc != -1 and end_toc > start_toc:
    html = html[:start_toc] + '<div class="toc-title">📑 สารบัญ</div>\n' + toc_html + html[end_toc:]

# Update date
from datetime import datetime, timezone, timedelta

# Bangkok timezone
bkk_offset = timedelta(hours=7)
bkk_tz = timezone(bkk_offset)
bkk = datetime.now(bkk_tz)

# Write output
with open('tech-ai-report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Generated tech-ai-report.html with {len(insights)} insights')

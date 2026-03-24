#!/usr/bin/env python3
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/insights_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

insights = data['insights']
company_emoji = {'openai': '🤖', 'google': '🔍', 'nvidia': '🎮', 'apple': '🍎', 'china': '🐉'}

def esc(s):
    if not s: return ''
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# Build insights HTML
insights_html = ''
for i, item in enumerate(insights):
    rank = i + 1
    emoji = company_emoji.get(item.get('company', ''), '📡')
    imp = item.get('impact', 'medium')
    imp_label = imp.upper()
    why_preview = esc(item.get('why_matters', ''))[:120]
    card_class = imp + '-impact'
    insights_html += f'<div class="insight-card {card_class}" id="insight-{item.get("id", rank)}">\n'
    insights_html += '<div class="particle-container"><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div></div>\n'
    insights_html += '<div class="insight-header"><div class="insight-header-left"><div class="insight-rank">' + str(rank) + '</div><div class="company-badge">' + emoji + '</div></div>'
    insights_html += '<div style="display:flex;gap:8px;align-items:center"><span class="insight-tag tag-ai">AI</span>'
    insights_html += f'<span class="impact-badge {imp}"><span class="impact-dot"></span>{imp_label}</span></div></div>\n'
    insights_html += '<div class="insight-headline">' + esc(item.get('title', '')) + '</div>\n'
    insights_html += '<div class="insight-source">' + esc(item.get('source', 'ไม่ระบุแหล่งที่มา')) + '</div>\n'
    if item.get('what'):
        insights_html += '<div class="tier-block"><div class="tier-label tier-what">What</div><div class="tier-body">' + esc(item.get('what', '')) + '</div></div>\n'
    if item.get('why_matters'):
        insights_html += '<div class="tier-block"><div class="tier-label tier-why">Why It Matters</div><div class="tier-body">' + esc(item.get('why_matters', '')) + '</div></div>\n'
    if item.get('so_what'):
        insights_html += '<div class="tier-block"><div class="tier-label tier-so">So What</div><div class="tier-body"><strong>' + esc(item.get('so_what', '')) + '</strong></div></div>\n'
    if item.get('now_what'):
        insights_html += '<div class="tier-block"><div class="tier-label tier-now">Now What</div><div class="tier-body">' + esc(item.get('now_what', '')) + '</div></div>\n'
    insights_html += '<div class="why-preview"><div class="why-preview-label">💡 Why It Matters</div><div class="why-preview-text">' + why_preview + '</div></div>\n'
    insights_html += '</div>\n\n'

# Build TOC
toc_html = ''
for i, item in enumerate(insights):
    rank = i + 1
    emoji = company_emoji.get(item.get('company', ''), '📡')
    imp = item.get('impact', 'medium')
    toc_html += f'<a class="toc-item" href="#insight-{item.get("id", rank)}">\n'
    toc_html += f'<div class="toc-rank">{rank}</div><div class="toc-company">{emoji}</div>'
    toc_html += f'<div class="toc-text"><div class="toc-label">{esc(item.get("title",""))}</div></div>'
    toc_html += f'<span class="toc-impact {imp}">{imp}</span></a>\n\n'

# The complete HTML

#!/usr/bin/env python3
import json

# Read insights data
with open('/home/administrator/.openclaw/workspace/ocean-ten-news/data/insights_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

insights = data['insights']

# Company emoji map
company_emoji = {
    'openai': '🤖', 'google': '🔍', 'nvidia': '🎮',
    'apple': '🍎', 'china': '🐉'
}

# Impact color class
def impact_class(impact):
    return f'{impact}-impact'

def esc(s):
    if not s: return ''
    return (str(s)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;'))

# Build insights HTML
insights_html = ''
for i, item in enumerate(insights):
    rank = i + 1
    emoji = company_emoji.get(item.get('company', ''), '📡')
    imp = item.get('impact', 'medium')
    imp_label = imp.upper()
    why_preview = esc(item.get('why_matters', ''))[:120]

    insights_html += f'''<div class="insight-card {impact_class(imp)}" id="insight-{item.get('id', rank)}">
  <div class="particle-container">
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
  </div>
  <div class="insight-header">
    <div class="insight-header-left">
      <div class="insight-rank">{rank}</div>
      <div class="company-badge">{emoji}</div>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <span class="insight-tag tag-ai">AI</span>
      <span class="impact-badge {imp}"><span class="impact-dot"></span>{imp_label}</span>
    </div>
  </div>
  <div class="insight-headline">{esc(item.get('title', ''))}</div>
  <div class="insight-source">{esc(item.get('source', 'ไม่ระบุแหล่งที่มา'))}</div>'''

    if item.get('what'):
        insights_html += f'''
  <div class="tier-block">
    <div class="tier-label tier-what">What</div>
    <div class="tier-body">{esc(item.get('what', ''))}</div>
  </div>'''

    if item.get('why_matters'):
        insights_html += f'''
  <div class="tier-block">
    <div class="tier-label tier-why">Why It Matters</div>
    <div class="tier-body">{esc(item.get('why_matters', ''))}</div>
  </div>'''

    if item.get('so_what'):
        insights_html += f'''
  <div class="tier-block">
    <div class="tier-label tier-so">So What</div>
    <div class="tier-body"><strong>{esc(item.get('so_what', ''))}</strong></div>
  </div>'''

    if item.get('now_what'):
        insights_html += f'''
  <div class="tier-block">
    <div class="tier-label tier-now">Now What</div>
    <div class="tier-body">{esc(item.get('now_what', ''))}</div>
  </div>'''

    insights_html += f'''
  <div class="why-preview">
    <div class="why-preview-label">💡 Why It Matters</div>
    <div class="why-preview-text">{why_preview}</div>
  </div>
</div>'''

# Build TOC HTML
toc_html = ''
for i, item in enumerate(insights):
    rank = i + 1
    emoji = company_emoji.get(item.get('company', ''), '📡')
    imp = item.get('impact', 'medium')
    toc_html += f'''<a class="toc-item" href="#insight-{item.get('id', rank)}" onclick="scrollToInsight(event,'insight-{item.get('id', rank)}')">
  <div class="toc-rank">{rank}</div>
  <div class="toc-company">{emoji}</div>
  <div class="toc-text">
    <div class="toc-label">{esc(item.get('title', ''))}</div>
  </div>
  <span class="toc-impact {imp}">{imp}</span>
</a>'''

# Build JS for dynamic loading and TOC
js = f'''    <script>
    function escHtml(str){{if(!str)return'';return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}}
    function updateClock(){{
      var now=new Date();
      var bkk=new Date(now.toLocaleString('en-US',{{timeZone:'Asia/Bangkok'}}));
      var h=String(bkk.getHours()).padStart(2,'0');
      var m=String(bkk.getMinutes()).padStart(2,'0');
      var s=String(bkk.getSeconds()).padStart(2,'0');
      var el=document.getElementById('liveClock');
      if(el)el.textContent=h+':'+m+':'+s+' ICT';
      var meta=document.getElementById('metaTimeChip');
      if(meta)meta.textContent=h+':'+m+' น. (ICT)';
      var d=String(bkk.getDate()).padStart(2,'0');
      var mo=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
      var y=bkk.getFullYear()+543;
      var dateEl=document.getElementById('reportDate');
      if(dateEl)dateEl.textContent=d+' '+mo[bkk.getMonth()]+' '+y+' • วิเคราะห์โดย Ocean Ten AI';
    }}
    updateClock();setInterval(updateClock,1000);

    function scrollToInsight(e, id){{e.preventDefault();document.getElementById(id).scrollIntoView{{behavior:'smooth',block:'start'}}}};

    // Reading progress bar
    window.addEventListener('scroll', function(){{
      var el=document.getElementById('readingProgress');
      if(!el)return;
      var total=document.documentElement.scrollHeight - window.innerHeight;
      var pct=total>0?(window.scrollY/total*100):0;
      el.style.width=pct+'%';
    }});

    // TOC active state on scroll
    var insightIds={json.dumps([item.get('id', str(i+1)) for i,item in enumerate(insights)])};
    var tocItems=document.querySelectorAll('.toc-item');
    var observer=new IntersectionObserver(function(entries){{
      entries.forEach(function(entry){{
        if(entry.isIntersecting){{
          tocItems.forEach(function(t){{t.classList.remove('active')}});
          var match=document.querySelector('.toc-item[href="#'+entry.target.id+'"]');
          if(match)match.classList.add('active');
        }}
      }})}}
    ,{{threshold:0.3}});
    setTimeout(function(){{
      insightIds.forEach(function(id){{
        var el=document.getElementById(id);
        if(el)observer.observe(el);
      }})}},500);

    // Load data from JSON
    fetch('/data/insights_data.json')
      .then(function(r){{return r.json()}})
      .then(function(json){{
        // Already rendered via static HTML, but update meta
        var aiItems=json.insights||[];
        if(aiItems.length){{
          document.getElementById('action1').textContent='AI Infrastructure + Enterprise Adoption';
          document.getElementById('action2').textContent='ความเสี่ยง: AI Regulation, การแข่งขันสูง';
          document.getElementById('action3').textContent='ขาขึ้น — Mass Adoption กำลังเกิด';
          document.getElementById('action4').textContent='GPT-5.4, Vera Rubin, Gemini Updates';
          var trendEl=document.getElementById('megaTrend');
          if(trendEl)trendEl.textContent='Agentic AI Mass Adoption + AI Hardware Revolution';
        }}
      }})
      .catch(function(e){{console.warn('JSON load skipped, using static HTML')}});

    // Share buttons
    function shareCopy(){{navigator.clipboard.writeText(window.location.href).then(function(){{alert('ลิงก์ถูกคัดลอกแล้ว!')}})}}
    function shareTwitter(){{window.open('https://twitter.com/intent/tweet?text=Tech+AI+Report+by+Ocean+Ten&url='+encodeURIComponent(window.location.href),'_blank')}}
    function shareFacebook(){{window.open('https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(window.location.href),'_blank')}}
    function submitFeedback(){{
      var input=document.getElementById('feedbackInput');
      if(input&&input.value.trim()){{
        alert('ขอบคุณสำหรับ feedback! ทีม Ocean Ten จะพิจารณาข้อเสนอแนะของคุณ 💙');
        input.value='';
      }}else if(input){{alert('กรุณาใส่ข้อเสนอแนะก่อนส่ง')}}
    }}
    </script>'''

# Full HTML
html = f'''{'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI & Tech Report — Ocean Ten</title>
  <meta name="theme-color" content="#030712">
  <meta name="description" content="Premium Tech & AI Research Report — OpenAI, NVIDIA, Apple, Google, Tesla, Microsoft — Ocean Ten">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+Thai:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-void: #030712; --bg-deep: #060d1f; --bg-panel: #0d1526; --bg-card: #0f1e35; --bg-card-hover: #142342;
      --border-dim: rgba(6,182,212,0.12); --border-glow: rgba(6,182,212,0.40);
      --cyan: #06b6d4; --cyan-bright: #22d3ee; --cyan-dim: #0891b2; --cyan-glow: rgba(6,182,212,0.15);
      --gold: #f0b90b; --gold-dim: #b8860b; --gold-glow: rgba(240,185,11,0.12);
      --purple: #a855f7; --green: #10b981; --red: #f43f5e; --orange: #f97316;
      --text-primary: #f1f5f9; --text-secondary: #94a3b8; --text-muted: #475569;
      --font-display: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    *{margin:0;padding:0;box-sizing:border-box} html{scroll-behavior:smooth}
    body{font-family:var(--font-display);background:var(--bg-void);color:var(--text-primary);min-height:100vh;overflow-x:hidden}
    body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 900px 600px at 15% -5%, rgba(6,182,212,0.07) 0%, transparent 60%),radial-gradient(ellipse 800px 500px at 85% 105%, rgba(240,185,11,0.05) 0%, transparent 55%),radial-gradient(ellipse 600px 400px at 50% 50%, rgba(168,85,247,0.03) 0%, transparent 60%);pointer-events:none;z-index:0;animation:ambientShift 18s ease-in-out infinite alternate}
    @keyframes ambientShift{0%{opacity:1}50%{opacity:.7}100%{opacity:1}}
    body::after{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(6,182,212,0.02) 1px, transparent 1px),linear-gradient(90deg, rgba(6,182,212,0.02) 1px, transparent 1px);background-size:72px 72px;pointer-events:none;z-index:0;mask-image:radial-gradient(ellipse 80% 80% at 50% 0%, black 30%, transparent 80%)}
    .reading-progress{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--cyan),var(--gold));z-index:9999;transition:width .1s linear;box-shadow:0 0 10px rgba(6,182,212,0.5)}
    .must-know-banner{position:relative;z-index:50;background:linear-gradient(135deg,rgba(6,182,212,0.12) 0%,rgba(240,185,11,0.08) 100%);border-bottom:1px solid rgba(6,182,212,0.25);padding:12px 24px;display:flex;align-items:center;justify-content:center;gap:12px;animation:slideDown .5s ease-out}
    @keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
    .must-know-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:linear-gradient(135deg,var(--red),#dc2626);border-radius:100px;font-size:10px;font-weight:800;color:#fff;text-transform:uppercase;letter-spacing:1.5px;animation:pulseGlow 2s infinite;flex-shrink:0}
    @keyframes pulseGlow{0%,100%{box-shadow:0 0 8px rgba(244,63,94,0.5)}50%{box-shadow:0 0 20px rgba(244,63,94,0.9)}}
    .must-know-text{font-size:12px;color:var(--text-secondary);font-weight:500} .must-know-text strong{color:var(--cyan-bright)}
    .must-know-close{background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:16px;padding:0 4px;transition:color .2s;flex-shrink:0} .must-know-close:hover{color:var(--red)}
    .topbar{position:sticky;top:0;z-index:100;backdrop-filter:blur(20px) saturate(180%);-webkit-backdrop-filter:blur(20px) saturate(180%);background:rgba(3,7,18,.85);border-bottom:1px solid var(--border-dim)}
    .topbar-inner{max-width:1200px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;justify-content:space-between;gap:16px}
    .topbar-brand{display:flex;align-items:center;gap:12px;text-decoration:none}
    .brand-logo{width:36px;height:36px;background:linear-gradient(135deg,var(--cyan),var(--cyan-dim));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}
    .brand-text{font-family:'Inter',sans-serif;font-size:15px;font-weight:800;letter-spacing:-0.5px}
    .brand-oc{color:var(--cyan-bright)} .brand-en{color:var(--text-primary)}
    .brand-sub{font-size:9px;color:var(--text-muted);text-transform:uppercase;letter-spacing:2px}
    .live-indicator{display:inline-flex;align-items:center;gap:6px;font-size:10px;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:1px;flex-shrink:0}
    .live-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:livePulse 1.5s infinite}
    @keyframes livePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.3)}}
    .topbar-right{display:flex;align-items:center;gap:16px}
    .live-clock{font-size:12px;font-weight:600;color:var(--cyan);font-variant-numeric:tabular-nums;letter-spacing:.5px}
    .back-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;font-size:11px;font-weight:600;color:var(--text-secondary);background:var(--bg-card);border:1px solid var(--border-dim);border-radius:6px;text-decoration:none;transition:all .2s}
    .back-btn:hover{color:var(--cyan);border-color:var(--border-glow);background:var(--bg-card-hover)}
    .main-layout{max-width:1200px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:1fr 260px;gap:36px;position:relative;z-index:1}
    @media(max-width:900px){.main-layout{grid-template-columns:1fr;display:block}.toc-sidebar{display:none}}
    .toc-sidebar{position:sticky;top:88px;height:fit-content;max-height:calc(100vh - 120px);overflow-y:auto;padding:28px 0}
    .toc-sidebar::-webkit-scrollbar{width:3px} .toc-sidebar::-webkit-scrollbar-track{background:transparent}
    .toc-sidebar::-webkit-scrollbar-thumb{background:var(--border-glow);border-radius:2px}
    .toc-title{font-size:10px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:2.5px;margin-bottom:12px;padding-left:4px}
    .toc-item{display:flex;align-items:center;gap:10px;padding:10px 12px;background:var(--bg-card);border:1px solid var(--border-dim);border-radius:8px;margin-bottom:6px;cursor:pointer;transition:all .25s;text-decoration:none;color:inherit;border-left:3px solid transparent}
    .toc-item:hover{background:var(--bg-card-hover);border-color:var(--border-glow);border-left-color:var(--cyan);transform:translateX(4px)}
    .toc-item.active{background:rgba(6,182,212,0.08);border-color:var(--cyan);border-left-color:var(--cyan)}
    .toc-rank{width:22px;height:22px;background:var(--bg-panel);border-radius:5px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:var(--text-muted);flex-shrink:0;transition:all .25s}
    .toc-item:hover .toc-rank,.toc-item.active .toc-rank{background:var(--cyan-glow);color:var(--cyan)}
    .toc-company{font-size:16px;flex-shrink:0;line-height:1}
    .toc-text{flex:1;min-width:0}
    .toc-label{font-size:11px;font-weight:600;color:var(--text-secondary);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .25s}
    .toc-item:hover .toc-label{color:var(--text-primary)}
    .toc-impact{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;padding:2px 7px;border-radius:100px;flex-shrink:0}
    .toc-impact.high{background:rgba(244,63,94,.15);color:var(--red)}
    .toc-impact.medium{background:rgba(249,115,22,.12);color:var(--orange)}
    .toc-impact.low{background:rgba(16,185,129,.12);color:var(--green)}
    .content-area{padding:40px 0 80px}
    .hero-section{padding:48px 0 36px;text-align:center;animation:fadeUp .7s ease-out both}
    @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
    .report-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 16px;background:linear-gradient(135deg,rgba(6,182,212,0.1),rgba(6,182,212,0.05));border:1px solid var(--border-glow);border-radius:100px;font-size:10px;font-weight:700;color:var(--cyan-bright);text-transform:uppercase;letter-spacing:2.5px;margin-bottom:20px}
    .report-badge .dot{width:6px;height:6px;background:var(--cyan);border-radius:50%;animation:pulseDot 2s infinite}
    @keyframes pulseDot{0%,100%{opacity:1}50%{opacity:.4}}
    .hero-date{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:16px}
    .hero-title{font-family:'Inter',sans-serif;font-size:clamp(28px,6vw,52px);font-weight:900;line-height:1.1;letter-spacing:-1.5px;margin-bottom:16px;color:var(--text-primary)}
    .hero-title span{color:var(--cyan-bright)}
    .hero-title em{font-style:normal;color:var(--gold)}
    .hero-sub{font-size:clamp(14px,2vw,17px);color:var(--text-secondary);line-height:1.7;max-width:600px;margin:0 auto 24px}
    .hero-meta{display:flex;align-items:center;justify-content:center;gap:20px;flex-wrap:wrap}
    .meta-chip{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:var(--bg-card);border:1px solid var(--border-dim);border-radius:6px;font-size:11px;color:var(--text-secondary)}
    .divider{height:1px;background:linear-gradient(90deg,transparent,var(--border-dim),transparent);margin:36px 0}
    .section-label{font-size:10px;font-weight:700;color:var(--cyan);text-transform:uppercase;letter-spacing:3px;margin-bottom:16px;display:flex;align-items:center;gap:10px}
    .section-label::before{content:'';width:20px;height:2px;background:var(--cyan);flex-shrink:0}
    .insights-section{margin-bottom:48px;animation:fadeUp .7s .15s ease-out both}
    .insight-card{background:var(--bg-card);border:1px solid var(--border-dim);border-radius:16px;padding:28px;margin-bottom:20px;position:relative;overflow:hidden;transition:border-color .35s,background .35s,transform .35s;box-shadow:0 4px 24px rgba(0,0,0,0.2)}
    .insight-card::before{content:'';position:absolute;inset:-1px;border-radius:17px;padding:1px;background:linear-gradient(135deg,transparent 30%,rgba(6,182,212,0.4) 50%,transparent 70%);-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:0;transition:opacity .4s;pointer-events:none}
    .insight-card::after{content:'';position:absolute;top:-60%;left:-60%;width:220px;height:220px;background:radial-gradient(circle,rgba(6,182,212,0.05) 0%,transparent 70%);pointer-events:none;transition:opacity .4s;opacity:0}
    .insight-card:hover{border-color:var(--border-glow);background:var(--bg-card-hover);transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,0.3)}
    .insight-card:hover::before{opacity:1} .insight-card:hover::after{opacity:1}
    .insight-card.high-impact::before{background:linear-gradient(135deg,rgba(244,63,94,0.5),rgba(244,63,94,0.2),rgba(240,185,11,0.3),rgba(244,63,94,0.5));background-size:300% 300%;animation:borderGlow 4s ease infinite}
    @keyframes borderGlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
    .insight-card.high-impact::after{background:radial-gradient(circle,rgba(244,63,94,0.08) 0%,transparent 70%);opacity:1!important}
    .insight-card.medium-impact::before{background:linear-gradient(135deg,transparent 30%,rgba(249,115,22,0.5) 50%,transparent 70%)}
    .insight-card.low-impact::before{background:linear-gradient(135deg,transparent 30%,rgba(16,185,129,0.5) 50%,transparent 70%)}
    .particle-container{position:absolute;inset:0;pointer-events:none;overflow:hidden;border-radius:16px}
    .particle{position:absolute;bottom:-10px;width:3px;height:3px;border-radius:50%;opacity:0;animation:particleFloat 4s ease-in-out infinite}
    @keyframes particleFloat{0%{opacity:0;transform:translateY(0) scale(0)}15%{opacity:.9}85%{opacity:.2}100%{opacity:0;transform:translateY(-320px) scale(1)}}
    .insight-card.high-impact .particle:nth-child(1){left:15%;animation-delay:0s;background:var(--red);box-shadow:0 0 6px rgba(244,63,94,0.8)}
    .insight-card.high-impact .particle:nth-child(2){left:30%;animation-delay:.8s;background:var(--gold);box-shadow:0 0 6px rgba(240,185,11,0.6)}
    .insight-card.high-impact .particle:nth-child(3){left:75%;animation-delay:1.6s;background:var(--red);box-shadow:0 0 6px rgba(244,63,94,0.8)}
    .insight-card.high-impact .particle:nth-child(4){left:50%;animation-delay:2.4s;background:var(--cyan);box-shadow:0 0 6px rgba(6,182,212,0.6)}
    .insight-card.high-impact .particle:nth-child(5){left:85%;animation-delay:3.2s;background:var(--purple);box-shadow:0 0 6px rgba(168,85,247,0.6)}
    .insight-card.high-impact .particle:nth-child(6){left:60%;animation-delay:1.2s;background:var(--gold);box-shadow:0 0 6px rgba(240,185,11,0.6)}
    .insight-header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px;position:relative;z-index:2;flex-wrap:wrap}
    .insight-header-left{display:flex;align-items:center;gap:12px}
    .insight-rank{width:32px;height:32px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;color:var(--cyan);flex-shrink:0}
    .company-badge{font-size:22px;flex-shrink:0;filter:drop-shadow(0 0 4px rgba(255,255,255,0.1));line-height:1}
    .insight-tag{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;padding:4px 10px;border-radius:4px;flex-shrink:0}
    .tag-ai{background:rgba(6,182,212,.12);color:var(--cyan);border:1px solid rgba(6,182,212,.3)}
    .tag-chip{background:rgba(168,85,247,.12);color:var(--purple);border:1px solid rgba(168,85,247,.3)}
    .impact-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:100px;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;flex-shrink:0;transition:all .3s}
    .impact-badge.high{background:rgba(244,63,94,.15);color:var(--red);border:1px solid rgba(244,63,94,.4);box-shadow:0 0 14px rgba(244,63,94,0.3)}
    .impact-badge.medium{background:rgba(249,115,22,.12);color:var(--orange);border:1px solid rgba(249,115,22,.3)}
    .impact-badge.low{background:rgba(16,185,129,.12);color:var(--green);border:1px solid rgba(16,185,129,.3)}
    .impact-badge .impact-dot{width:5px;height:5px;border-radius:50%}
    .impact-badge.high .impact-dot{background:var(--red);box-shadow:0 0 4px var(--red);animation:pulseDot 1.5s infinite}
    .impact-badge.medium .impact-dot{background:var(--orange)} .impact-badge.low .impact-dot{background:var(--green)}
    .why-preview{position:absolute;bottom:0;left:0;right:0;padding:20px 28px;background:linear-gradient(to top,rgba(3,7,18,.97) 0%,rgba(3,7,18,.88) 55%,transparent 100%);transform:translateY(102%);transition:transform .4s cubic-bezier(.4,0,.2,1);z-index:3;border-radius:0 0 16px 16px;pointer-events:none}
    .insight-card:hover .why-preview{transform:translateY(0)}
    .why-preview-label{font-size:9px;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;display:flex;align-items:center;gap:6px}
    .why-preview-text{font-size:13px;color:var(--text-secondary);line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .3s}
    .insight-card:hover .why-preview-text{color:var(--text-primary)}
    .insight-headline{font-size:clamp(16px,2.5vw,20px);font-weight:800;line-height:1.3;color:var(--text-primary);letter-spacing:-.3px;margin-bottom:10px;position:relative;z-index:2}
    .insight-source{font-size:10px;color:var(--text-muted);margin-bottom:14px;display:flex;align-items:center;gap:4px;position:relative;z-index:2}
    .tier-block{margin-bottom:14px;position:relative;z-index:2}
    .tier-label{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;display:flex;align-items:center;gap:8px}
    .tier-what{color:var(--cyan)} .tier-what::before{content:'▸';color:var(--cyan)}
    .tier-why{color:var(--gold)} .tier-why::before{content:'▸';color:var(--gold)}
    .tier-so{color:var(--green)} .tier-so::before{content:'▸';color:var(--green)}
    .tier-now{color:var(--purple)} .tier-now::before{content:'▸';color:var(--purple)}
    .tier-body{font-size:14px;line-height:1.75;color:var(--text-secondary)} .tier-body strong{color:var(--text-primary)}
    .action-section{margin-bottom:48px;animation:fadeUp .7s .3s ease-out both}
    .action-card{background:linear-gradient(135deg,var(--bg-card) 0%,rgba(6,182,212,.05) 100%);border:1px solid var(--border-glow);border-radius:12px;padding:28px;position:relative;overflow:hidden}
    .action-card::after{content:'';position:absolute;top:-50%;right:-10%;width:200px;height:200px;background:radial-gradient(circle,rgba(6,182,212,.07) 0%,transparent 70%);pointer-events:none}
    .action-title{font-size:12px;font-weight:700;color:var(--cyan);text-transform:uppercase;letter-spacing:2.5px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
    .action-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
    .action-item{background:rgba(3,7,18,.5);border:1px solid var(--border-dim);border-radius:8px;padding:16px}
    .action-item-label{font-size:9px;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px}
    .action-item-value{font-size:13px;font-weight:700;color:var(--text-primary);line-height:1.4}
    .trend-section{margin-bottom:48px;animation:fadeUp .7s .4s ease-out both}
    .trend-card{background:var(--bg-card);border:1px solid var(--border-dim);border-radius:12px;padding:24px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
    .trend-icon{width:48px;height:48px;background:rgba(6,182,212,0.1);border:1px solid var(--border-glow);
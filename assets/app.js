const date = "2026-03-18";
const sourcePath = `data/news-${date}.json`;

const heroImageMap = {
  'thai-politics': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=1600&q=80',
  'thai-economy': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1600&q=80',
  'world': 'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1600&q=80',
  'gold': 'https://images.unsplash.com/photo-1610375461246-83df859d849d?auto=format&fit=crop&w=1600&q=80'
};

const sectionStyle = {
  'thai-politics': { badge: 'การเมือง', tone: 'hot', readTime: 'อ่าน 3 นาที' },
  'thai-economy': { badge: 'เศรษฐกิจ', tone: 'focus', readTime: 'อ่าน 2 นาที' },
  'world': { badge: 'ต่างประเทศ', tone: 'alert', readTime: 'อ่าน 3 นาที' },
  'gold': { badge: 'ทองคำ', tone: 'market', readTime: 'อ่าน 2 นาที' }
};

let rawData = null;
let currentFilter = 'all';

function allItems() {
  return rawData.sections.flatMap((s, idxS) => s.items.map((item, idxI) => ({
    section: s,
    item,
    rankScore: (10 - idxS) * 10 - idxI
  })));
}

function createCard(sectionId, sectionName, item, idx) {
  const style = sectionStyle[sectionId] || { badge: sectionName, tone: 'focus', readTime: 'อ่าน 2 นาที' };
  const thumb = heroImageMap[sectionId] || heroImageMap.world;
  const score = Math.max(7, 10 - idx);

  return `
    <article class="card">
      <div class="thumb" style="background-image:url('${thumb}')">
        <span class="chip chip-${style.tone}">${style.badge}</span>
        <span class="score">Impact ${score}/10</span>
      </div>
      <div class="card-body">
        <h3>${item.headline}</h3>
        <div class="meta">${style.readTime} · แหล่งข่าว: ${item.source}</div>
        <p>${item.summary}</p>
        <p class="impact"><strong>Impact:</strong> ${item.impact}</p>
        <a class="link" href="${item.url}" target="_blank" rel="noopener noreferrer">อ่านต่อทันที ↗</a>
      </div>
    </article>
  `;
}

function renderHero() {
  const first = allItems()[0];
  const hero = document.getElementById('hero');
  const bg = heroImageMap[first.section.id] || heroImageMap.world;

  hero.style.backgroundImage = `url('${bg}')`;
  hero.innerHTML = `
    <div class="hero-content">
      <span class="kicker">🔥 ข่าวเด่นที่สุดวันนี้</span>
      <h2>${first.item.headline}</h2>
      <p>${first.item.summary}</p>
      <div class="hero-cta-wrap">
        <span class="hero-score">Impact 10/10</span>
        <a class="hero-cta" href="${first.item.url}" target="_blank" rel="noopener noreferrer">อ่านข่าวนี้ทันที</a>
      </div>
    </div>
  `;
}

function renderMustRead() {
  const el = document.getElementById('mustRead');
  const top3 = allItems().slice(0, 3);
  el.innerHTML = `
    <h3>📌 ต้องอ่านก่อน 3 ข่าว</h3>
    <div class="must-grid">
      ${top3.map((x, i) => `
        <a class="must-item" href="${x.item.url}" target="_blank" rel="noopener noreferrer">
          <span class="num">#${i + 1}</span>
          <span>${x.item.headline}</span>
        </a>
      `).join('')}
    </div>
  `;
}

function renderBreaking() {
  const el = document.getElementById('breakingTrack');
  const text = allItems().slice(0, 5).map(x => `• ${x.item.headline}`).join('   ');
  el.innerHTML = `<div class="marquee">${text} &nbsp;&nbsp;&nbsp; ${text}</div>`;
}

function renderQuickList() {
  const el = document.getElementById('quickList');
  const rows = allItems().slice(0, 6).map((x, i) => `
    <li>
      <span class="rank">${i + 1}</span>
      <a href="${x.item.url}" target="_blank" rel="noopener noreferrer">${x.item.headline}</a>
    </li>
  `).join('');
  el.innerHTML = rows;
}

function renderCards() {
  const root = document.getElementById('cards');
  const rows = rawData.sections
    .filter(s => currentFilter === 'all' || s.id === currentFilter)
    .flatMap(s => s.items.map((item, i) => createCard(s.id, s.name, item, i)))
    .join('');

  root.innerHTML = rows || '<p>ไม่พบข่าวในหมวดนี้</p>';

  document.querySelectorAll('.btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === currentFilter);
  });
}

function buildFilters() {
  const bar = document.getElementById('filters');
  const tabs = [{ id: 'all', name: 'ทั้งหมด' }, ...rawData.sections.map(s => ({ id: s.id, name: s.name }))];
  bar.innerHTML = tabs.map(x => `<button class="btn ${x.id === 'all' ? 'active' : ''}" data-filter="${x.id}">${x.name}</button>`).join('');

  bar.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    currentFilter = btn.dataset.filter;
    renderCards();
  });
}

function renderMeta() {
  document.getElementById('brief-date').textContent = `อัปเดต ${rawData.date} (${rawData.timezone})`;
  document.getElementById('brief-note').textContent = rawData.note || '';
}

async function loadData() {
  const res = await fetch(sourcePath + `?t=${Date.now()}`);
  rawData = await res.json();
}

async function init() {
  await loadData();
  renderMeta();
  buildFilters();
  renderHero();
  renderMustRead();
  renderBreaking();
  renderQuickList();
  renderCards();
}

document.getElementById('refreshBtn').addEventListener('click', async () => {
  await init();
});

init().catch(err => {
  document.getElementById('cards').innerHTML = `<p>โหลดข่าวไม่สำเร็จ: ${err.message}</p>`;
});

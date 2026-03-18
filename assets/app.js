const date = "2026-03-18";
const sourcePath = `data/news-${date}.json`;

const heroImageMap = {
  'thai-politics': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=1600&q=80',
  'thai-economy': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1600&q=80',
  'world': 'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1600&q=80',
  'gold': 'https://images.unsplash.com/photo-1610375461246-83df859d849d?auto=format&fit=crop&w=1600&q=80'
};

let rawData = null;
let currentFilter = 'all';

function allItems() {
  return rawData.sections.flatMap(s => s.items.map(item => ({ section: s, item })));
}

function createCard(sectionName, item) {
  return `
    <article class="card">
      <span class="tag">${sectionName}</span>
      <h3>${item.headline}</h3>
      <div class="meta">แหล่งข่าว: ${item.source}</div>
      <p>${item.summary}</p>
      <p class="impact"><strong>Impact:</strong> ${item.impact}</p>
      <a class="link" href="${item.url}" target="_blank" rel="noopener noreferrer">อ่านข่าวต้นทาง ↗</a>
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
      <span class="kicker">ไฮไลต์วันนี้ · ${first.section.name}</span>
      <h2>${first.item.headline}</h2>
      <p>${first.item.summary}</p>
      <a href="${first.item.url}" target="_blank" rel="noopener noreferrer">อ่านข่าวเต็มจากแหล่งต้นทาง ↗</a>
    </div>
  `;
}

function renderQuickList() {
  const el = document.getElementById('quickList');
  const rows = allItems().slice(0, 6).map(x => `<li>${x.item.headline}</li>`).join('');
  el.innerHTML = rows;
}

function renderCards() {
  const root = document.getElementById('cards');
  const rows = rawData.sections
    .filter(s => currentFilter === 'all' || s.id === currentFilter)
    .flatMap(s => s.items.map(item => createCard(s.name, item)))
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
  renderQuickList();
  renderCards();
}

document.getElementById('refreshBtn').addEventListener('click', async () => {
  await init();
});

init().catch(err => {
  document.getElementById('cards').innerHTML = `<p>โหลดข่าวไม่สำเร็จ: ${err.message}</p>`;
});

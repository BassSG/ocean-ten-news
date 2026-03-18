const date = "2026-03-18";
const sourcePath = `data/news-${date}.json`;

let rawData = null;
let currentFilter = 'all';

function createCard(sectionName, item) {
  return `
    <article class="card">
      <span class="tag">${sectionName}</span>
      <h3>${item.headline}</h3>
      <div class="meta">แหล่งข่าว: ${item.source}</div>
      <p>${item.summary}</p>
      <p class="impact"><strong>Impact:</strong> ${item.impact}</p>
      <p><a class="link" href="${item.url}" target="_blank" rel="noopener noreferrer">เปิดแหล่งข่าว</a></p>
    </article>
  `;
}

function render() {
  const root = document.getElementById('cards');
  const title = document.getElementById('brief-title');
  const dateEl = document.getElementById('brief-date');
  const note = document.getElementById('brief-note');

  title.textContent = rawData.title;
  dateEl.textContent = `วันที่ ${rawData.date} (${rawData.timezone})`;
  note.textContent = rawData.note || '';

  const html = rawData.sections
    .filter(s => currentFilter === 'all' || s.id === currentFilter)
    .flatMap(s => s.items.map(item => createCard(s.name, item)))
    .join('');

  root.innerHTML = html || '<p>ไม่พบข่าวในหมวดนี้</p>';

  document.querySelectorAll('.btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === currentFilter);
  });
}

function buildFilters() {
  const bar = document.getElementById('filters');
  const all = [{ id: 'all', name: 'ทั้งหมด' }, ...rawData.sections.map(s => ({ id: s.id, name: s.name }))];
  bar.innerHTML = all.map(x => `<button class="btn ${x.id==='all'?'active':''}" data-filter="${x.id}">${x.name}</button>`).join('');

  bar.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    currentFilter = btn.dataset.filter;
    render();
  });
}

async function init() {
  const res = await fetch(sourcePath);
  rawData = await res.json();
  buildFilters();
  render();
}

init().catch(err => {
  document.getElementById('cards').innerHTML = `<p>โหลดข่าวไม่สำเร็จ: ${err.message}</p>`;
});

const CACHE_NAME = 'ocean-ten-news-v2';
const APP_SHELL = [
  '/ocean-ten-news/',
  '/ocean-ten-news/index.html',
  '/ocean-ten-news/knowledge-drop.html',
  '/ocean-ten-news/manifest.webmanifest',
  '/ocean-ten-news/manifest-knowledge.webmanifest',
  '/ocean-ten-news/manifest-chart.webmanifest',
  '/ocean-ten-news/assets/styles.css',
  '/ocean-ten-news/assets/app.js',
  '/ocean-ten-news/assets/icons/icon-192.svg',
  '/ocean-ten-news/assets/icons/icon-512.svg',
  '/ocean-ten-news/assets/icons/icon-xau-192.png',
  '/ocean-ten-news/assets/icons/icon-xau-512.png',
  '/ocean-ten-news/data/news-2026-03-18.json',
  '/ocean-ten-news/data/knowledge_latest.json',
  '/ocean-ten-news/data/knowledge_news_raw.json',
  '/ocean-ten-news/data/knowledge_news_edited.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  event.respondWith(
    fetch(req)
      .then((res) => {
        const cloned = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, cloned));
        return res;
      })
      .catch(() => caches.match(req).then(r => r || caches.match('/ocean-ten-news/index.html')))
  );
});

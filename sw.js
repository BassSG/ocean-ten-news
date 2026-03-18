const CACHE_NAME = 'ocean-ten-news-v1';
const APP_SHELL = [
  '/ocean-ten-news/',
  '/ocean-ten-news/index.html',
  '/ocean-ten-news/assets/styles.css',
  '/ocean-ten-news/assets/app.js',
  '/ocean-ten-news/manifest.webmanifest',
  '/ocean-ten-news/assets/icons/icon-192.svg',
  '/ocean-ten-news/assets/icons/icon-512.svg',
  '/ocean-ten-news/data/news-2026-03-18.json'
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

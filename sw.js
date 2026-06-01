const CACHE = '0.1.0-beta';
const API_CACHE = 'api-cache';
const FILES = [
  '/',
  '/webapp.html',
  'https://telegram.org/js/telegram-web-app.js',
  'https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800;900&display=swap'
];

// Установка — кэшируем статику
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(FILES).catch(() => {}))
  );
  self.skipWaiting();
});

// Активация — удаляем старый кэш статики
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE && k !== API_CACHE).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = e.request.url;

  // GET /api/items — stale-while-revalidate
  if (url.includes('/api/items') && e.request.method === 'GET') {
    e.respondWith(
      caches.open(API_CACHE).then(cache =>
        cache.match(e.request).then(cached => {
          const fetchPromise = fetch(e.request).then(res => {
            if (res.ok) cache.put(e.request, res.clone());
            return res;
          });
          // есть кэш — отдаём сразу, обновляем фоном
          return cached || fetchPromise;
        })
      )
    );
    return;
  }

  // Остальные API запросы (POST, notify, expenses) — только сеть
  if (url.includes('/api/')) {
    e.respondWith(fetch(e.request));
    return;
  }

  // Статика — сначала кэш, потом сеть
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});

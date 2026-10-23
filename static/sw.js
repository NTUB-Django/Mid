const CACHE_NAME = 'ntub-mid-v1';
const PRECACHE_ASSETS = [
  '/static/css/app.css',
  '/static/css/course-workspace.css?v=20261018b',
  '/static/css/workspaces.css?v=20261018c',
  '/static/css/design-system.css?v=20261018d',
  '/static/js/navigation.js?v=20261018b',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/img/timetable-icon.svg',
  '/static/icons/icon-512.png',
];
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('Pre-cache partial failure:', err);
      });
    })
  );
  self.skipWaiting();
});
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => (key.startsWith('ntub-timetable-') || key.startsWith('ntub-mid-')) && key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        return (
          cached ||
          fetch(request).then((response) => {
            if (response.ok && response.type === 'basic') {
              return caches.open(CACHE_NAME).then((cache) =>
                cache.put(request, response.clone()).then(() => response)
              );
            }
            return response;
          })
        );
      })
    );
  }
});

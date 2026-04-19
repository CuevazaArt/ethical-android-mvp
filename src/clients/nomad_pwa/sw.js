const CACHE_NAME = 'nomad-bridge-v2';
const ASSETS = [
  '/',
  '/index.html',
  '/style.css',
  '/app.js',
  '/media_engine.js',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Best effort caching so it doesn't block install on LAN
      return cache.addAll(ASSETS).catch(e => console.warn('Cache add error', e));
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only handle HTTP/HTTPS, ignore WebSockets (ws/wss)
  if (!event.request.url.startsWith('http')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache dynamic assets if needed, but we mostly care about offline fallback
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

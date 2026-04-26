const CACHE_NAME = 'nomad-bridge-v7';
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

  // Stale-While-Revalidate strategy
  event.respondWith(
    fetch(event.request).then((res) => {
      let copy = res.clone();
      caches.open(CACHE_NAME).then(c => c.put(event.request, copy));
      return res;
    }).catch(() => caches.match(event.request))
  );
});

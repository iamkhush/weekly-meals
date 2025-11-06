
const CACHE_NAME = 'meals-cache-v1';
const OFFLINE_URLS = [
  '/weekly-meals/',
  '/weekly-meals/meals/',
  '/weekly-meals/weekly-plan/',
  // Add more URLs as needed for offline support
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(OFFLINE_URLS);
    })
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  // Only handle requests under /weekly-meals/
  if (!event.request.url.includes('/weekly-meals/')) return;
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).catch(() => {
        // Fallback to main page if offline and navigation request
        if (event.request.mode === 'navigate') {
          return caches.match('/weekly-meals/');
        }
      });
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
});

// Listen for messages from the page to cache dynamic URLs
self.addEventListener('message', function(event) {
  if (event.data && event.data.action === 'cache-url' && event.data.url) {
    caches.open(CACHE_NAME).then(cache => {
      cache.add(event.data.url);
    });
  }
});

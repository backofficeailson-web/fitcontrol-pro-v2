/* =============================================================================
 * FitControl Pro 2.0 — Service Worker
 * Strategy:
 *   - Pre-cache app shell (CSS/JS/icons) on install.
 *   - Network-first for navigations with offline fallback to /offline.
 *   - Stale-while-revalidate for static assets.
 *   - Never cache auth/POST/admin endpoints.
 * since 2018 Ailson Soares
 * =========================================================================== */

const VERSION       = 'fitcontrol-v2.0.0';
const STATIC_CACHE  = `static-${VERSION}`;
const RUNTIME_CACHE = `runtime-${VERSION}`;
const OFFLINE_URL   = '/offline';

const PRECACHE_URLS = [
  '/offline',
  '/manifest.json',
  '/static/css/tokens.css',
  '/static/css/base.css',
  '/static/css/components.css',
  '/static/css/layout.css',
  '/static/css/dashboard.css',
  '/static/css/mobile.css',
  '/static/js/app.js',
  '/static/js/pwa.js',
  '/static/img/icons/icon-192.png',
  '/static/img/icons/icon-512.png',
];

// --- Install: pre-cache shell ---
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) =>
      cache.addAll(PRECACHE_URLS).catch((err) => {
        console.warn('[SW] Precache partial failure:', err);
      })
    ).then(() => self.skipWaiting())
  );
});

// --- Activate: clean old caches ---
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// --- Fetch strategy ---
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Never touch non-GET (login POST, CSRF, etc.)
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Bypass auth and API endpoints entirely
  if (url.pathname.startsWith('/auth/') ||
      url.pathname.startsWith('/api/')  ||
      url.pathname.startsWith('/healthz') ||
      url.pathname.startsWith('/readyz')) {
    return;
  }

  // HTML navigations -> network-first, fallback to offline page
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Static assets -> stale-while-revalidate
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const networkFetch = fetch(req)
          .then((res) => {
            const copy = res.clone();
            caches.open(STATIC_CACHE).then((c) => c.put(req, copy));
            return res;
          })
          .catch(() => cached);
        return cached || networkFetch;
      })
    );
  }
});

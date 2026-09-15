const CACHE_NAME = "migrantia-v2";
const STATIC_ASSETS = [
  "/",
  "/static/css/main.css",
  "/static/js/i18n.js",
  "/static/js/api.js",
  "/static/js/speech.js",
  "/static/js/app.js",
  "/static/manifest.json"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Em desenvolvimento, busca da rede primeiro para evitar JS desatualizado
  if (event.request.url.includes("/api/")) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

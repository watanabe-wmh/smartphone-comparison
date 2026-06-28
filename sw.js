// 初台グルメマップ Service Worker（オフライン対応・ホーム画面追加）
// アプリシェル＋データをキャッシュ。地図タイルや店舗写真など外部リソースは
// 量が多く動的なためキャッシュせずネットワーク任せにする。
const CACHE = 'gourmet-v1';
const ASSETS = [
  './', 'index.html', 'manifest.json',
  'vendor/leaflet.css', 'vendor/leaflet.js',
  'vendor/MarkerCluster.css', 'vendor/MarkerCluster.Default.css', 'vendor/leaflet.markercluster.js',
  'vendor/images/marker-icon.png', 'vendor/images/marker-icon-2x.png', 'vendor/images/marker-shadow.png',
  'vendor/images/layers.png', 'vendor/images/layers-2x.png',
  'data/restaurants.json?v=4',
  'icons/icon-192.png', 'icons/icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;          // 外部（タイル/写真）はそのまま
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }).catch(() => caches.match('index.html')))         // オフライン時はアプリシェルを返す
  );
});

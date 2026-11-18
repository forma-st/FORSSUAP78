// Service worker : met l'application en cache pour un fonctionnement hors ligne.
const CACHE='forssuap78-66f1dc2618';
const ASSETS=['./', 'index.html', 'manifest.webmanifest', 'vendor/jspdf.umd.min.js', 'vendor/anthropic-sdk.min.js', 'vendor/elevenlabs-client.min.js', 'fonts/montserrat-latin-400-normal.woff2', 'fonts/montserrat-latin-500-normal.woff2', 'fonts/montserrat-latin-600-normal.woff2', 'fonts/montserrat-latin-700-normal.woff2', 'fonts/montserrat-latin-800-normal.woff2', 'forms/riofe-ps-attest.png', 'forms/riofe-ps-auto-28.png', 'forms/riofe-ps-auto-29.png', 'forms/riofe-ps-crit-30.png', 'forms/riofe-ps-crit-31.png', 'forms/riofe-ps-somm-33.png', 'forms/riofe-suap-attest.png', 'forms/riofe-suap-auto-28.png', 'forms/riofe-suap-auto-29.png', 'forms/riofe-suap-crit-30.png', 'forms/riofe-suap-crit-31.png', 'forms/riofe-suap-somm-34.png', 'forms/riofe-suap-somm-35.png', 'forms/riofe-suap-trans-32.png', 'forms/riofe-suap-trans-33.png', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png', 'icons/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
// Page : réseau d'abord (nouvelle version dès qu'il y a du réseau), cache sinon (terrain sans réseau).
// Autres fichiers : cache d'abord.
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const u=new URL(e.request.url);const page=e.request.mode==='navigate'||u.pathname.endsWith('/')||u.pathname.endsWith('index.html');
  if(page){e.respondWith(fetch(e.request,{cache:'no-store'}).then(r=>{const c=r.clone();caches.open(CACHE).then(ca=>ca.put('index.html',c));return r}).catch(()=>caches.match('index.html')));return}
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request).catch(()=>caches.match('index.html'))));
});

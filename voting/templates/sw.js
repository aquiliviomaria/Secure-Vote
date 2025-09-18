// Service Worker para SecureVote PWA
const CACHE_NAME = 'securevote-v1.0.0';
const STATIC_CACHE = 'securevote-static-v1.0.0';
const DYNAMIC_CACHE = 'securevote-dynamic-v1.0.0';

// Arquivos estáticos para cache
const STATIC_FILES = [
  '/',
  '/static/css/',
  '/static/js/',
  '/static/images/',
  '/static/manifest.json',
  '/voting/',
  '/administrator/',
  '/accounts/login/',
  '/accounts/register/'
];

// Instalação do Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Instalando...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Cacheando arquivos estáticos');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker: Instalação concluída');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Erro na instalação:', error);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Ativando...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Ativação concluída');
        return self.clients.claim();
      })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Estratégia para diferentes tipos de requisições
  if (request.method === 'GET') {
    // Páginas HTML - Network First
    if (request.headers.get('accept').includes('text/html')) {
      event.respondWith(networkFirstStrategy(request));
    }
    // Arquivos estáticos - Cache First
    else if (url.pathname.startsWith('/static/') || 
             url.pathname.startsWith('/media/') ||
             url.pathname.includes('.css') ||
             url.pathname.includes('.js') ||
             url.pathname.includes('.png') ||
             url.pathname.includes('.jpg') ||
             url.pathname.includes('.jpeg') ||
             url.pathname.includes('.gif') ||
             url.pathname.includes('.svg') ||
             url.pathname.includes('.ico')) {
      event.respondWith(cacheFirstStrategy(request));
    }
    // API calls - Network First
    else if (url.pathname.startsWith('/api/') || 
             url.pathname.startsWith('/voting/api/') ||
             url.pathname.startsWith('/administrator/api/')) {
      event.respondWith(networkFirstStrategy(request));
    }
    // Outras requisições - Network First
    else {
      event.respondWith(networkFirstStrategy(request));
    }
  }
});

// Estratégia Cache First
async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Cache First Strategy Error:', error);
    return new Response('Recurso não disponível offline', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Estratégia Network First
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network First: Tentando cache...', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Página offline para HTML
    if (request.headers.get('accept').includes('text/html')) {
      return caches.match('/offline.html') || new Response(`
        <!DOCTYPE html>
        <html lang="pt">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Offline - SecureVote</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              text-align: center; 
              padding: 50px; 
              background: #f5f5f5;
            }
            .offline-container {
              max-width: 400px;
              margin: 0 auto;
              background: white;
              padding: 30px;
              border-radius: 10px;
              box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .icon { font-size: 48px; color: #e74c3c; }
            h1 { color: #2c3e50; }
            p { color: #7f8c8d; }
            .retry-btn {
              background: #3498db;
              color: white;
              border: none;
              padding: 10px 20px;
              border-radius: 5px;
              cursor: pointer;
              margin-top: 20px;
            }
          </style>
        </head>
        <body>
          <div class="offline-container">
            <div class="icon">📡</div>
            <h1>Sem Conexão</h1>
            <p>Você está offline. Verifique sua conexão com a internet e tente novamente.</p>
            <button class="retry-btn" onclick="window.location.reload()">Tentar Novamente</button>
          </div>
        </body>
        </html>
      `, {
        headers: { 'Content-Type': 'text/html' }
      });
    }

    return new Response('Recurso não disponível offline', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Sincronização em background
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Sincronização em background');
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Implementar lógica de sincronização se necessário
  console.log('Executando sincronização em background...');
}

// Notificações push
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/images/icon-192x192.png',
      badge: '/static/images/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey
      },
      actions: [
        {
          action: 'explore',
          title: 'Ver Detalhes',
          icon: '/static/images/icon-96x96.png'
        },
        {
          action: 'close',
          title: 'Fechar',
          icon: '/static/images/icon-96x96.png'
        }
      ]
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Clique em notificação
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Apenas fechar a notificação
  } else {
    // Clique na notificação
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Mensagens do cliente
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
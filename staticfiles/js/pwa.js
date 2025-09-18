// PWA Registration and Management
class PWAManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.deferredPrompt = null;
    this.init();
  }

  init() {
    this.registerServiceWorker();
    this.setupInstallPrompt();
    this.setupOnlineOfflineHandlers();
    this.setupUpdateNotification();
  }

  // Registrar Service Worker
  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/static/sw.js');
        console.log('Service Worker registrado com sucesso:', registration);

        // Verificar atualizações
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });

        // Escutar mensagens do service worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          if (event.data && event.data.type === 'CACHE_UPDATED') {
            this.showCacheUpdateNotification();
          }
        });

      } catch (error) {
        console.error('Erro ao registrar Service Worker:', error);
      }
    }
  }

  // Configurar prompt de instalação
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Verificar se já está instalado
    window.addEventListener('appinstalled', () => {
      console.log('PWA instalado com sucesso!');
      this.hideInstallButton();
      this.deferredPrompt = null;
    });
  }

  // Mostrar botão de instalação
  showInstallButton() {
    const installButton = document.getElementById('install-pwa-btn');
    if (installButton) {
      installButton.style.display = 'block';
      installButton.addEventListener('click', () => this.installPWA());
    }
  }

  // Esconder botão de instalação
  hideInstallButton() {
    const installButton = document.getElementById('install-pwa-btn');
    if (installButton) {
      installButton.style.display = 'none';
    }
  }

  // Instalar PWA
  async installPWA() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('Usuário aceitou a instalação do PWA');
      } else {
        console.log('Usuário rejeitou a instalação do PWA');
      }
      
      this.deferredPrompt = null;
      this.hideInstallButton();
    }
  }

  // Configurar handlers online/offline
  setupOnlineOfflineHandlers() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.showOnlineNotification();
      this.syncOfflineData();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.showOfflineNotification();
    });
  }

  // Configurar notificação de atualização
  setupUpdateNotification() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });
    }
  }

  // Mostrar notificação de atualização
  showUpdateNotification() {
    const notification = this.createNotification(
      'Atualização Disponível',
      'Uma nova versão do SecureVote está disponível. Clique para atualizar.',
      'update'
    );
    
    notification.addEventListener('click', () => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistration().then(registration => {
          if (registration && registration.waiting) {
            registration.waiting.postMessage({ type: 'SKIP_WAITING' });
          }
        });
      }
    });
  }

  // Mostrar notificação de cache atualizado
  showCacheUpdateNotification() {
    this.createNotification(
      'Cache Atualizado',
      'Os dados foram atualizados com sucesso.',
      'success'
    );
  }

  // Mostrar notificação online
  showOnlineNotification() {
    this.createNotification(
      'Conexão Restaurada',
      'Você está online novamente.',
      'success'
    );
  }

  // Mostrar notificação offline
  showOfflineNotification() {
    this.createNotification(
      'Modo Offline',
      'Você está offline. Algumas funcionalidades podem estar limitadas.',
      'warning'
    );
  }

  // Criar notificação
  createNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `pwa-notification pwa-notification-${type}`;
    notification.innerHTML = `
      <div class="pwa-notification-content">
        <h4>${title}</h4>
        <p>${message}</p>
        <button class="pwa-notification-close">&times;</button>
      </div>
    `;

    // Adicionar estilos se não existirem
    if (!document.getElementById('pwa-notification-styles')) {
      const styles = document.createElement('style');
      styles.id = 'pwa-notification-styles';
      styles.textContent = `
        .pwa-notification {
          position: fixed;
          top: 20px;
          right: 20px;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          z-index: 10000;
          max-width: 350px;
          animation: slideIn 0.3s ease-out;
        }
        .pwa-notification-success { border-left: 4px solid #27ae60; }
        .pwa-notification-warning { border-left: 4px solid #f39c12; }
        .pwa-notification-update { border-left: 4px solid #3498db; }
        .pwa-notification-content {
          padding: 15px;
          position: relative;
        }
        .pwa-notification h4 {
          margin: 0 0 5px 0;
          color: #2c3e50;
          font-size: 14px;
        }
        .pwa-notification p {
          margin: 0;
          color: #7f8c8d;
          font-size: 12px;
          line-height: 1.4;
        }
        .pwa-notification-close {
          position: absolute;
          top: 10px;
          right: 10px;
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: #bdc3c7;
        }
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      document.head.appendChild(styles);
    }

    document.body.appendChild(notification);

    // Auto-remover após 5 segundos
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 5000);

    // Botão de fechar
    notification.querySelector('.pwa-notification-close').addEventListener('click', () => {
      notification.remove();
    });

    return notification;
  }

  // Sincronizar dados offline
  async syncOfflineData() {
    // Implementar lógica de sincronização se necessário
    console.log('Sincronizando dados offline...');
  }

  // Verificar se é PWA
  isPWA() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  // Obter informações do PWA
  getPWAInfo() {
    return {
      isPWA: this.isPWA(),
      isOnline: this.isOnline,
      hasServiceWorker: 'serviceWorker' in navigator,
      canInstall: this.deferredPrompt !== null
    };
  }
}

// Inicializar PWA Manager quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
  window.pwaManager = new PWAManager();
});

// Exportar para uso global
window.PWAManager = PWAManager;
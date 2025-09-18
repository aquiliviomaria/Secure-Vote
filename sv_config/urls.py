"""e_voting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.cache import cache_control

# PWA Manifest View
@cache_control(max_age=86400)  # Cache por 24 horas
def pwa_manifest(request):
    """Retorna o manifest.json com cache headers apropriados"""
    return JsonResponse({
        "name": "SecureVote - Sistema de Votação Segura",
        "short_name": "SecureVote",
        "description": "Sistema de votação eletrônica seguro e transparente",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#2c3e50",
        "orientation": "portrait-primary",
        "scope": "/",
        "lang": "pt",
        "dir": "ltr",
        "categories": ["government", "utilities", "productivity"],
        "icons": [
            {
                "src": "/static/images/icon-72x72.png",
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-128x128.png",
                "sizes": "128x128",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-144x144.png",
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-152x152.png",
                "sizes": "152x152",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-384x384.png",
                "sizes": "384x384",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable any"
            }
        ],
        "shortcuts": [
            {
                "name": "Votar",
                "short_name": "Votar",
                "description": "Acessar área de votação",
                "url": "/voting/",
                "icons": [
                    {
                        "src": "/static/images/icon-96x96.png",
                        "sizes": "96x96"
                    }
                ]
            },
            {
                "name": "Administração",
                "short_name": "Admin",
                "description": "Painel administrativo",
                "url": "/administrator/",
                "icons": [
                    {
                        "src": "/static/images/icon-96x96.png",
                        "sizes": "96x96"
                    }
                ]
            }
        ]
    })

urlpatterns = [
    path('', include('account.urls')),
    path('admin/', admin.site.urls),
    path('administrator/', include('administrator.urls')),
    path('voting/', include('voting.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # PWA URLs
    path('manifest.json', pwa_manifest, name='pwa_manifest'),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='pwa_sw'),
    path('offline.html', TemplateView.as_view(template_name='offline.html'), name='pwa_offline'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# URLs para PWA - adicionar ao urls.py principal
from django.urls import path
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.cache import cache_control

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

@cache_control(max_age=86400)  # Cache por 24 horas
def pwa_manifest_cached(request):
    """Versão com cache do manifest"""
    return pwa_manifest(request)

# URLs para PWA
pwa_urlpatterns = [
    path('manifest.json', pwa_manifest_cached, name='pwa_manifest'),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='pwa_sw'),
    path('offline.html', TemplateView.as_view(template_name='offline.html'), name='pwa_offline'),
]
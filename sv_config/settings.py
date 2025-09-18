from pathlib import Path
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# ----------------------------
# Build paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# Security
# ----------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'temp-key-for-local-testing-change-me-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hosts
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

# SSL / HTTPS settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ----------------------------
# Applications
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'account.apps.AccountConfig',
    'voting.apps.VotingConfig',
    'administrator.apps.AdministratorConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.AccountCheckMiddleWare',
]

ROOT_URLCONF = 'sv_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['voting/templates', 'administrator/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'voting.context_processors.election_settings_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'sv_config.wsgi.application'

# ----------------------------
# Database
# ----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite local para desenvolvimento
    }
}

# 👉 Alternativa para produção (usar pasta persistente no servidor)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': '/var/data/db_data/db.sqlite3',
#     }
# }

# ----------------------------
# Password validation
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# Internationalization
# ----------------------------
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Africa/Maputo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ----------------------------
# Static and Media files
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # destino para collectstatic
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # pastas dev

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------
# Configuração S3/Deta (produção opcional)
# ----------------------------
if not DEBUG and os.getenv('USE_S3', 'False') == 'True':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# ----------------------------
# Custom User model
# ----------------------------
AUTH_USER_MODEL = 'account.CustomUser'
AUTHENTICATION_BACKENDS = ['account.email_backend.EmailBackend']

# ----------------------------
# Election settings
# ----------------------------
ELECTION_TITLE_PATH = os.path.join(BASE_DIR, 'election_title.txt')
SEND_OTP = False
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------
# Email (console para teste)
# ----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@securevote.com'
SERVER_EMAIL = 'errors@securevote.com'

# ----------------------------
# Sites framework
# ----------------------------
SITE_ID = 1

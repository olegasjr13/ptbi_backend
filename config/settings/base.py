#########################################
# config/settings/base.py
#########################################
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default')

def _env_bool(name, default=False):
    v = os.getenv(name, None)
    if v is None:
        return default
    return str(v).lower() in ('1','true','yes','on')

DEBUG = _env_bool('DEBUG', default=False)
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS','localhost').split(',') if h.strip()]

# Apps
SHARED_APPS = [
    'django_tenants',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Libs
    'corsheaders',

    # Apps compartilhados
    'apps.tenants',
    'apps.users',
    'apps.empresa',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
]

TENANT_APPS = [
    'apps.funcionarios',
    'apps.setup'
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_tenants.middleware.main.TenantMainMiddleware',
    'apps.tenants.middleware.ValidateTenantHostMiddleware',
    'apps.tenants.middleware.TenantRequestLoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.users.middleware.TenantAccessSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'config.urls_public'
TENANT_URLCONF = 'config.urls_tenants'

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('POSTGRES_DB', ''),
        'USER': os.getenv('POSTGRES_USER', ''),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# Static/Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Segurança
SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT', default=False)
CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE', default=True)
SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', default=True)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CORS
_cors = os.getenv('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors.split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Preparação cookies JWT
JWT_ACCESS_COOKIE_NAME = os.getenv('JWT_ACCESS_COOKIE_NAME', 'access_token')
JWT_REFRESH_COOKIE_NAME = os.getenv('JWT_REFRESH_COOKIE_NAME', 'refresh_token')
JWT_COOKIE_SECURE = _env_bool('JWT_COOKIE_SECURE', default=True)
JWT_COOKIE_SAMESITE = os.getenv('JWT_COOKIE_SAMESITE', 'None')
JWT_COOKIE_PATH = '/'




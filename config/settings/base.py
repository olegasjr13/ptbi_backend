import os
from pathlib import Path
from datetime import timedelta
from apps.setup.logging_config import LOGGING as TENANT_LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

SHARED_APPS = [
    'django_tenants',  # OBRIGATÓRIO – fornece middleware e base
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Bibliotecas utilitárias compartilhadas
    'corsheaders',
    'whitenoise',

    # Apps do seu projeto compartilhados (existem em todos os schemas)
    'apps.tenants',  # Contém Cliente e ClienteDomain
    'apps.users',    # Contém CustomUser vinculado ao Cliente
    'apps.empresa',  # Contém Empresa
    # Django REST Framework + JWT também são compartilhados
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
]

TENANT_APPS = [
    'apps.funcionarios',
    'apps.setup'
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS

MIDDLEWARE = [
    # Segurança e arquivos estáticos
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # CORS (precisa vir antes das sessões)
    'corsheaders.middleware.CorsMiddleware',

    # Sessões
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Identificação do tenant (antes de qualquer lógica de sessão ou autenticação)
    'django_tenants.middleware.main.TenantMainMiddleware',

    # Middlewares customizados do tenant (após identificação)
    'apps.tenants.middleware.ValidateTenantHostMiddleware',
    'apps.tenants.middleware.TenantRequestLoggingMiddleware',

    # Middleware comum
    'django.middleware.common.CommonMiddleware',

    # CSRF e autenticação
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Segurança de acesso ao tenant (usa request.user e request.tenant)
    'apps.users.middleware.TenantAccessSecurityMiddleware',

    # Mensagens e segurança
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]






ROOT_URLCONF = 'config.urls_tenants'
WSGI_APPLICATION = 'config.wsgi.application'

LOGGING = TENANT_LOGGING

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('POSTGRES_DB', 'paulo_tadeu_bi'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'MIRROR': 'default',  # Necessário para testes com django-tenants
        },
    }
}


TENANT_MODEL = "tenants.Cliente"
TENANT_DOMAIN_MODEL = "tenants.ClienteDomain"
PUBLIC_SCHEMA_NAME = "public"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"
TENANT_URLCONF = "config.urls_tenants"
TENANT_TEST_NAME = "test_runner"


DATABASE_ROUTERS = [
    'django_tenants.routers.TenantSyncRouter',
]

AUTH_USER_MODEL = "users.CustomUser"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', [])

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', False)
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', True)
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', True)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
print(f"🔒 Configurações de segurança: SSL={SECURE_SSL_REDIRECT}, HSTS={SECURE_HSTS_SECONDS}s")
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

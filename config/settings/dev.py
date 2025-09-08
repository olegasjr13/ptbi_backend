#########################################
# config/settings/dev.py
#########################################
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOW_ALL_ORIGINS = True

# Cookies dev (para testes locais)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
JWT_COOKIE_SECURE = False
JWT_COOKIE_SAMESITE = 'Lax'
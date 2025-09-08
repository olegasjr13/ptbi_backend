# apps/core/logging_config.py
import logging

class TenantRequestFilter(logging.Filter):
    def filter(self, record):
        from django.db import connection
        record.tenant = getattr(connection, 'schema_name', 'unknown')
        return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'tenant_filter': {
            '()': 'apps.setup.logging_config.TenantRequestFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] [{tenant}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['tenant_filter'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'apps': {  # nossos apps personalizados
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


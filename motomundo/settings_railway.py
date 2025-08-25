"""
Railway-specific settings for MotoMundo
"""
import os
import dj_database_url
from .settings import *

# Railway automatically sets PORT, but we can override if needed
PORT = int(os.environ.get('PORT', 8000))

# Railway-specific settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']  # Railway handles domain routing

# Database configuration for Railway PostgreSQL with PostGIS
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
    # Override engine to use PostGIS for geographic features
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
else:
    # Fallback to local PostgreSQL with PostGIS
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('DJANGO_DB_NAME', 'motomundo'),
            'USER': os.environ.get('DJANGO_DB_USER', 'motomundo'),
            'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'motomundo'),
            'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
            'PORT': os.environ.get('DJANGO_DB_PORT', '5432'),
        }
    }

# Redis configuration for Railway Redis
if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise for serving static files in production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration for Railway
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Email configuration for SendGrid (optional)
if 'SENDGRID_API_KEY' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    DEFAULT_FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@motomundo.com')
else:
    # Console backend for development/testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Frontend URL for invitation links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://motomundo-production.up.railway.app')

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# CORS settings if needed for frontend
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'https://motomundo-production.up.railway.app'),
    'http://localhost:3000',  # For local development
    'http://127.0.0.1:3000',
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
            'propagate': False,
        },
        'clubs': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'emails': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

import os
from .settings import *  # noqa
from urllib.parse import urlparse

# Production overrides
DEBUG = False

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

base_hosts = []
for var in ('DJANGO_ALLOWED_HOSTS', 'ALLOWED_HOSTS'):
    val = os.environ.get(var)
    if val:
        base_hosts.extend([h.strip() for h in val.split(',') if h.strip()])
ALLOWED_HOSTS = base_hosts or ['localhost']

# Always append Render-provided external hostname if present (per Render docs)
render_external = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_external and render_external not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_external)

# TEMP DEBUG (remove after verification)
print("[startup] ALLOWED_HOSTS:", ALLOWED_HOSTS)

# Security headers / SSL (adjust when behind a proxy / load balancer)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
REFERRER_POLICY = 'same-origin'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '3600'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files via WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Reduce REST_FRAMEWORK renderers to JSON only for performance
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']  # type: ignore

# Database (expect env vars prefixed POSTGRES_*)
def _build_db_config():
    # Priority 1: Explicit POSTGRES_* variables
    name = os.environ.get('POSTGRES_DB') or os.environ.get('DJANGO_DB_NAME')
    user = os.environ.get('POSTGRES_USER') or os.environ.get('DJANGO_DB_USER')
    password = os.environ.get('POSTGRES_PASSWORD') or os.environ.get('DJANGO_DB_PASSWORD')
    host = os.environ.get('POSTGRES_HOST') or os.environ.get('DJANGO_DB_HOST')
    port = os.environ.get('POSTGRES_PORT') or os.environ.get('DJANGO_DB_PORT') or '5432'

    # Priority 2: DATABASE_URL (Render / many platforms)
    if (not name or not user) and 'DATABASE_URL' in os.environ:
        url = urlparse(os.environ['DATABASE_URL'])
        # Example: postgres://user:pass@host:port/dbname
        if url.scheme.startswith('postgres'):
            name = url.path.lstrip('/') or name
            user = url.username or user
            password = url.password or password
            host = url.hostname or host
            port = str(url.port or port)

    missing = [k for k, v in [('DB name', name), ('DB user', user), ('DB password', password)] if not v]
    if missing:
        raise RuntimeError(
            f"Database configuration incomplete. Missing: {', '.join(missing)}. "
            "Provide POSTGRES_* vars or a DATABASE_URL."
        )

    return {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # PostGIS backend for geographic features
        'NAME': name,
        'USER': user,
        'PASSWORD': password,
        'HOST': host or 'localhost',
        'PORT': port,
    }

DATABASES = {
    'default': _build_db_config()
}

# Redis cache optional
redis_host = os.environ.get('REDIS_HOST') or os.environ.get('DJANGO_REDIS_HOST')
if redis_host:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': f"redis://{redis_host}:6379/1",
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

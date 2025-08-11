from __future__ import annotations

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
import time


def healthz(request: HttpRequest) -> HttpResponse:
    start = time.time()
    db_status = 'ok'
    cache_status = 'unknown'
    errors: list[str] = []

    # DB check (default alias)
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1;')
            cursor.fetchone()
    except OperationalError as e:
        db_status = 'error'
        errors.append(f'db: {e}')

    # Cache check (best effort)
    try:
        cache.set('_healthz', '1', 5)
        val = cache.get('_healthz')
        cache_status = 'ok' if val == '1' else 'error'
        if cache_status == 'error':
            errors.append('cache: set/get mismatch')
    except Exception as e:  # broad to capture backend issues
        cache_status = 'error'
        errors.append(f'cache: {e}')

    overall = 'ok' if db_status == 'ok' else 'degraded'
    status_code = 200 if overall == 'ok' else 503

    payload = {
        'status': overall,
        'db': db_status,
        'cache': cache_status,
        'errors': errors,
        'response_time_ms': round((time.time() - start) * 1000, 2),
    }
    return JsonResponse(payload, status=status_code)

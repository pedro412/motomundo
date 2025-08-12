#!/usr/bin/env sh
set -e

# Determine DB host/port for readiness (supports POSTGRES_*, DJANGO_DB_*, DATABASE_URL)
DB_WAIT_HOST="${POSTGRES_HOST:-$DJANGO_DB_HOST}"
DB_WAIT_PORT="${POSTGRES_PORT:-${DJANGO_DB_PORT:-5432}}"

if [ -z "$DB_WAIT_HOST" ] && [ -n "$DATABASE_URL" ]; then
  # Parse host/port from DATABASE_URL using Python
  eval $(python - <<'EOF'
import os, urllib.parse
url = os.environ.get('DATABASE_URL')
if url:
    p = urllib.parse.urlparse(url)
    if p.hostname:
        print(f"HOST_PARSED={p.hostname}")
    if p.port:
        print(f"PORT_PARSED={p.port}")
EOF
)
  DB_WAIT_HOST="${DB_WAIT_HOST:-$HOST_PARSED}"
  DB_WAIT_PORT="${DB_WAIT_PORT:-$PORT_PARSED}"
fi

if [ -n "$DB_WAIT_HOST" ]; then
  echo "Waiting for Postgres $DB_WAIT_HOST:$DB_WAIT_PORT..."
  until python -c "import socket; s=socket.create_connection(('${DB_WAIT_HOST}', int('${DB_WAIT_PORT}'))); s.close()" 2>/dev/null; do
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Determine bind port (Render often provides $PORT)
APP_PORT="${PORT:-8000}"

echo "Starting Gunicorn on :$APP_PORT..."
exec gunicorn motomundo.wsgi:application --bind 0.0.0.0:"$APP_PORT" --workers ${GUNICORN_WORKERS:-3} --timeout 60

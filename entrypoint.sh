#!/usr/bin/env sh
set -e

# Wait for Postgres
if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for Postgres $POSTGRES_HOST:$POSTGRES_PORT..."
  until python -c "import socket; s=socket.create_connection(('$POSTGRES_HOST', int('$POSTGRES_PORT'))); s.close()" 2>/dev/null; do
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn motomundo.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout 60

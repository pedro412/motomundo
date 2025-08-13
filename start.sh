#!/bin/bash

# Railway startup script for MotoMundo
set -e

echo "🏍️  Starting MotoMundo on Railway..."

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# Collect static files  
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (only in development)
if [ "$DEBUG" = "true" ]; then
    echo "👤 Creating admin user (development only)..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@motomundo.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
" || echo "⚠️  Skipping admin user creation"
fi

# Start the application
echo "🚀 Starting MotoMundo server..."
PORT=${PORT:-8000}
echo "📡 Using port: $PORT"
exec gunicorn motomundo.wsgi:application --bind 0.0.0.0:$PORT --workers 2

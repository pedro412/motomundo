#!/bin/bash

# Railway deployment script for MotoMundo
echo "🏍️  Deploying MotoMundo to Railway..."

# Install dependencies (if not done in build step)
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create admin user in development
if [ "$DEBUG" = "true" ]; then
    echo "👤 Creating admin user..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@motomundo.com', 'admin123')
    print('✅ Admin user created')
" || echo "⚠️  Admin user creation skipped"
fi

echo "✅ Deployment setup complete!"

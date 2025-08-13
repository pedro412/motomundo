#!/bin/bash

# Railway entrypoint script for MotoMundo

echo "🏍️  Starting MotoMundo deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@motomundo.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
"

# Load initial data if needed
echo "📊 Loading initial test data..."
python manage.py shell -c "
from clubs.models import Club
if Club.objects.count() == 0:
    print('Loading test data...')
    try:
        exec(open('clubs/management/commands/load_test_data.py').read())
        print('✅ Test data loaded')
    except:
        print('⚠️  Test data loading skipped (file not found)')
else:
    print('✅ Database already has data')
"

echo "🚀 MotoMundo is ready to ride!"

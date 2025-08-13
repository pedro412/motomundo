#!/usr/bin/env python
"""
Quick verification script for Railway deployment
Run this locally to verify settings work
"""
import os
import sys
import django
from pathlib import Path

# Add project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set Railway environment variables for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings_railway')
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-validation')
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')

try:
    django.setup()
    print("✅ Django settings loaded successfully")
    
    # Test imports
    from motomundo.wsgi import application
    print("✅ WSGI application imports correctly")
    
    from django.contrib.auth.models import User
    print("✅ Django models import correctly")
    
    from clubs.models import Club, Chapter, Member
    print("✅ Custom models import correctly")
    
    from emails.models import Invitation
    print("✅ Email system imports correctly")
    
    # Test health endpoint import
    from motomundo.health import healthz
    print("✅ Health check endpoint imports correctly")
    
    print("\n🎉 All imports successful!")
    print("🚂 MotoMundo is ready for Railway deployment!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔧 Check your settings and dependencies")
    sys.exit(1)

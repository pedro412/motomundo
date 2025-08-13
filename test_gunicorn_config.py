#!/usr/bin/env python
"""
Test gunicorn configuration locally
"""
import os
import subprocess
import sys

# Set test environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings_railway')
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-local-testing')
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('PORT', '8000')

try:
    print("🧪 Testing gunicorn configuration...")
    
    # Test that gunicorn can import the config
    import gunicorn.app.wsgiapp
    print("✅ Gunicorn imports successfully")
    
    # Test that our WSGI application can be imported
    from motomundo.wsgi import application
    print("✅ WSGI application imports successfully")
    
    # Test gunicorn config file
    exec(open('gunicorn.conf.py').read())
    print("✅ Gunicorn config file is valid")
    
    print(f"✅ Configuration test passed!")
    print(f"🚀 Gunicorn will bind to: 0.0.0.0:{os.environ.get('PORT', 8000)}")
    print("🔧 Ready for Railway deployment!")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    sys.exit(1)

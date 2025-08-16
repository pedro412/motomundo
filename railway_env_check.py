"""
Simple Railway environment diagnostic script
Run this directly on Railway to check environment variables
"""

import os

print("🚂 RAILWAY ENVIRONMENT DIAGNOSTIC")
print("=" * 50)

print("\n📊 CLOUDINARY VARIABLES:")
cloudinary_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
for var in cloudinary_vars:
    value = os.environ.get(var)
    if value:
        masked = value[:4] + '***' + value[-4:] if len(value) > 8 else '***'
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: NOT SET")

print("\n🗄️ STORAGE CONFIG:")
storage_backend = os.environ.get('IMAGE_STORAGE_BACKEND', 'NOT SET')
print(f"IMAGE_STORAGE_BACKEND: {storage_backend}")

print("\n🚂 RAILWAY INFO:")
railway_vars = ['RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_NAME', 'RAILWAY_SERVICE_NAME']
for var in railway_vars:
    value = os.environ.get(var, 'NOT SET')
    print(f"{var}: {value}")

print("\n🐍 DJANGO:")
django_env = os.environ.get('DJANGO_ENV', 'NOT SET')
debug = os.environ.get('DJANGO_DEBUG', 'NOT SET')
print(f"DJANGO_ENV: {django_env}")
print(f"DJANGO_DEBUG: {debug}")

print("\n📋 ALL RELEVANT ENV VARS:")
for key, value in sorted(os.environ.items()):
    if any(keyword in key.upper() for keyword in ['CLOUDINARY', 'DJANGO', 'RAILWAY', 'IMAGE']):
        if 'SECRET' in key or 'KEY' in key:
            masked_value = value[:4] + '***' + value[-4:] if len(value) > 8 else '***'
        else:
            masked_value = value
        print(f"{key}: {masked_value}")

print("\n" + "=" * 50)
all_set = all(os.environ.get(var) for var in cloudinary_vars)
if all_set:
    print("🎉 ALL CLOUDINARY VARIABLES ARE SET!")
else:
    print("❌ MISSING CLOUDINARY VARIABLES")
    print("Set them in Railway dashboard under Variables tab")

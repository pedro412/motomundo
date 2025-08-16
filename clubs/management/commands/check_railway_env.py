"""
Django management command to check Railway environment variables and Cloudinary configuration
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check Railway environment variables and Cloudinary configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Railway Environment Check'))
        self.stdout.write('=' * 60)
        
        # Check Cloudinary environment variables
        self.stdout.write('\n📊 CLOUDINARY ENVIRONMENT VARIABLES:')
        cloudinary_vars = [
            'CLOUDINARY_CLOUD_NAME',
            'CLOUDINARY_API_KEY', 
            'CLOUDINARY_API_SECRET'
        ]
        
        all_vars_present = True
        for var in cloudinary_vars:
            value = os.environ.get(var)
            if value:
                # Show partial value for security
                if 'SECRET' in var or 'KEY' in var:
                    masked_value = value[:4] + '***' + value[-4:] if len(value) > 8 else '***'
                else:
                    masked_value = value
                self.stdout.write(f'   ✅ {var}: {masked_value}')
            else:
                self.stdout.write(f'   ❌ {var}: Not set')
                all_vars_present = False
                
        # Check storage backend setting
        self.stdout.write('\n🗄️  STORAGE CONFIGURATION:')
        storage_backend = os.environ.get('IMAGE_STORAGE_BACKEND', 'not set')
        self.stdout.write(f'   IMAGE_STORAGE_BACKEND: {storage_backend}')
        
        # Check Django environment
        self.stdout.write('\n🐍 DJANGO ENVIRONMENT:')
        django_env = os.environ.get('DJANGO_ENV', 'not set')
        debug = os.environ.get('DJANGO_DEBUG', 'not set')
        self.stdout.write(f'   DJANGO_ENV: {django_env}')
        self.stdout.write(f'   DJANGO_DEBUG: {debug}')
        
        # Check Railway specific variables
        self.stdout.write('\n🚂 RAILWAY ENVIRONMENT:')
        railway_vars = [
            'RAILWAY_ENVIRONMENT',
            'RAILWAY_PROJECT_NAME',
            'RAILWAY_SERVICE_NAME'
        ]
        
        for var in railway_vars:
            value = os.environ.get(var, 'not set')
            self.stdout.write(f'   {var}: {value}')
            
        # Test Cloudinary configuration loading
        self.stdout.write('\n🔧 CLOUDINARY CONFIGURATION TEST:')
        try:
            from clubs.storage_config import CLOUDINARY_STORAGE
            self.stdout.write(f'   ✅ CLOUDINARY_STORAGE loaded successfully')
            self.stdout.write(f'   Cloud Name: {CLOUDINARY_STORAGE.get("CLOUD_NAME", "NOT SET")}')
            api_key = CLOUDINARY_STORAGE.get("API_KEY", "NOT SET")
            if api_key != "NOT SET" and len(api_key) > 8:
                api_key = api_key[:4] + '***' + api_key[-4:]
            self.stdout.write(f'   API Key: {api_key}')
            
            # Test Cloudinary storage initialization
            from clubs.storage_backends import CloudinaryImageStorage
            storage = CloudinaryImageStorage()
            self.stdout.write(f'   ✅ CloudinaryImageStorage initialized')
            
        except Exception as e:
            self.stdout.write(f'   ❌ Error loading Cloudinary configuration: {e}')
            
        # Summary and recommendations
        self.stdout.write('\n' + '=' * 60)
        if all_vars_present:
            self.stdout.write(self.style.SUCCESS('🎉 All Cloudinary variables are set!'))
            self.stdout.write('   You can now run the image migration:')
            self.stdout.write('   railway run python manage.py migrate_images_to_cloudinary --dry-run')
        else:
            self.stdout.write(self.style.ERROR('❌ Missing Cloudinary configuration'))
            self.stdout.write('   Set the missing environment variables in Railway dashboard:')
            self.stdout.write('   1. Go to your Railway project dashboard')
            self.stdout.write('   2. Click on Variables tab')
            self.stdout.write('   3. Add the missing CLOUDINARY_* variables')
            
        # Show Railway CLI commands to set variables
        self.stdout.write('\n🔧 RAILWAY CLI COMMANDS TO SET VARIABLES:')
        self.stdout.write('   railway variables set CLOUDINARY_CLOUD_NAME=your_cloud_name')
        self.stdout.write('   railway variables set CLOUDINARY_API_KEY=your_api_key')  
        self.stdout.write('   railway variables set CLOUDINARY_API_SECRET=your_api_secret')
        self.stdout.write('   railway variables set IMAGE_STORAGE_BACKEND=cloudinary')
        
        # Show all environment variables (filtered)
        self.stdout.write('\n📋 ALL ENVIRONMENT VARIABLES (filtered):')
        env_vars = []
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['CLOUDINARY', 'DJANGO', 'RAILWAY', 'IMAGE_STORAGE']):
                if 'SECRET' in key or 'KEY' in key:
                    masked_value = value[:4] + '***' + value[-4:] if len(value) > 8 else '***'
                else:
                    masked_value = value
                env_vars.append(f'   {key}: {masked_value}')
                
        for var in sorted(env_vars):
            self.stdout.write(var)

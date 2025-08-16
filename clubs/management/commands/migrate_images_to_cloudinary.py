"""
Django management command to migrate existing profile pictures from local storage to Cloudinary.

This command will:
1. Find all members with existing profile pictures
2. Upload each image to Cloudinary
3. Update the database references to point to Cloudinary URLs
4. Optionally clean up local files after successful migration

Usage:
    python manage.py migrate_images_to_cloudinary
    python manage.py migrate_images_to_cloudinary --dry-run  # Preview without changes
    python manage.py migrate_images_to_cloudinary --cleanup  # Remove local files after migration
"""

import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from clubs.models import Member, Club
from clubs.storage_backends import CloudinaryImageStorage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate existing profile pictures from local storage to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview the migration without making any changes',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove local files after successful migration to Cloudinary',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if IMAGE_STORAGE_BACKEND is not set to cloudinary',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.cleanup = options['cleanup']
        self.force = options['force']
        
        self.stdout.write(self.style.SUCCESS('🔄 Starting image migration to Cloudinary...'))
        
        # Check if Cloudinary is configured
        if not self.force and getattr(settings, 'IMAGE_STORAGE_BACKEND', 'local') != 'cloudinary':
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  IMAGE_STORAGE_BACKEND is not set to "cloudinary".\n'
                    'Set IMAGE_STORAGE_BACKEND=cloudinary in your environment or use --force flag.'
                )
            )
            return
            
        # Check Cloudinary configuration
        if not self._check_cloudinary_config():
            return
            
        # Initialize Cloudinary storage
        try:
            cloudinary_storage = CloudinaryImageStorage()
            self.stdout.write(self.style.SUCCESS('✅ Cloudinary storage initialized'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to initialize Cloudinary storage: {e}'))
            return
            
        # Migrate member profile pictures
        self._migrate_member_profiles(cloudinary_storage)
        
        # Migrate club logos
        self._migrate_club_logos(cloudinary_storage)
        
        self.stdout.write(self.style.SUCCESS('🎉 Image migration completed!'))

    def _check_cloudinary_config(self):
        """Check if Cloudinary is properly configured"""
        # Import the storage config to get the CLOUDINARY_STORAGE dict
        from clubs.storage_config import CLOUDINARY_STORAGE
        
        required_settings = ['CLOUD_NAME', 'API_KEY', 'API_SECRET']
        missing_settings = []
        
        for setting in required_settings:
            if not CLOUDINARY_STORAGE.get(setting):
                missing_settings.append(f'CLOUDINARY_{setting}')
                
        if missing_settings:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Missing Cloudinary configuration: {", ".join(missing_settings)}\n'
                    'Please set these environment variables in Railway dashboard before running the migration.'
                )
            )
            return False
            
        # Also show what we found for debugging
        self.stdout.write(f'✅ Cloudinary configured with cloud: {CLOUDINARY_STORAGE["CLOUD_NAME"]}')
        return True

    def _migrate_member_profiles(self, cloudinary_storage):
        """Migrate member profile pictures to Cloudinary"""
        self.stdout.write('\n📸 Migrating member profile pictures...')
        
        # Find members with profile pictures
        members_with_pics = Member.objects.exclude(profile_picture='').exclude(profile_picture__isnull=True)
        total_members = members_with_pics.count()
        
        if total_members == 0:
            self.stdout.write(self.style.WARNING('⚠️  No member profile pictures found to migrate'))
            return
            
        self.stdout.write(f'Found {total_members} members with profile pictures')
        
        successful_migrations = 0
        failed_migrations = 0
        
        for i, member in enumerate(members_with_pics, 1):
            self.stdout.write(f'\n[{i}/{total_members}] Processing {member.first_name} {member.last_name}...')
            
            try:
                # Get the current file path
                current_file = member.profile_picture
                local_path = current_file.path if hasattr(current_file, 'path') else None
                
                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(self.style.WARNING(f'⚠️  Local file not found: {current_file.name}'))
                    failed_migrations += 1
                    continue
                    
                if self.dry_run:
                    self.stdout.write(f'🔍 [DRY RUN] Would migrate: {local_path} -> Cloudinary')
                    successful_migrations += 1
                    continue
                    
                # Read the file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                    
                # Create a ContentFile
                content_file = ContentFile(file_content)
                
                # Upload to Cloudinary using the original filename
                original_name = os.path.basename(current_file.name)
                cloudinary_path = cloudinary_storage.save(f'members/profiles/{original_name}', content_file)
                
                # Update the member's profile picture field
                member.profile_picture.name = cloudinary_path
                member.save()
                
                self.stdout.write(self.style.SUCCESS(f'✅ Migrated: {original_name} -> {cloudinary_path}'))
                
                # Clean up local file if requested
                if self.cleanup:
                    try:
                        os.remove(local_path)
                        self.stdout.write(f'🗑️  Removed local file: {local_path}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'⚠️  Could not remove local file: {e}'))
                        
                successful_migrations += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to migrate {member.first_name} {member.last_name}: {e}'))
                failed_migrations += 1
                
        # Summary
        self.stdout.write(f'\n📊 Member Profile Pictures Migration Summary:')
        self.stdout.write(f'✅ Successful: {successful_migrations}')
        self.stdout.write(f'❌ Failed: {failed_migrations}')

    def _migrate_club_logos(self, cloudinary_storage):
        """Migrate club logos to Cloudinary"""
        self.stdout.write('\n🏛️  Migrating club logos...')
        
        # Find clubs with logos
        clubs_with_logos = Club.objects.exclude(logo='').exclude(logo__isnull=True)
        total_clubs = clubs_with_logos.count()
        
        if total_clubs == 0:
            self.stdout.write(self.style.WARNING('⚠️  No club logos found to migrate'))
            return
            
        self.stdout.write(f'Found {total_clubs} clubs with logos')
        
        successful_migrations = 0
        failed_migrations = 0
        
        for i, club in enumerate(clubs_with_logos, 1):
            self.stdout.write(f'\n[{i}/{total_clubs}] Processing {club.name}...')
            
            try:
                # Get the current file path
                current_file = club.logo
                local_path = current_file.path if hasattr(current_file, 'path') else None
                
                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(self.style.WARNING(f'⚠️  Local file not found: {current_file.name}'))
                    failed_migrations += 1
                    continue
                    
                if self.dry_run:
                    self.stdout.write(f'🔍 [DRY RUN] Would migrate: {local_path} -> Cloudinary')
                    successful_migrations += 1
                    continue
                    
                # Read the file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                    
                # Create a ContentFile
                content_file = ContentFile(file_content)
                
                # Upload to Cloudinary using the original filename
                original_name = os.path.basename(current_file.name)
                cloudinary_path = cloudinary_storage.save(f'clubs/logos/{original_name}', content_file)
                
                # Update the club's logo field
                club.logo.name = cloudinary_path
                club.save()
                
                self.stdout.write(self.style.SUCCESS(f'✅ Migrated: {original_name} -> {cloudinary_path}'))
                
                # Clean up local file if requested
                if self.cleanup:
                    try:
                        os.remove(local_path)
                        self.stdout.write(f'🗑️  Removed local file: {local_path}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'⚠️  Could not remove local file: {e}'))
                        
                successful_migrations += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to migrate {club.name}: {e}'))
                failed_migrations += 1
                
        # Summary
        self.stdout.write(f'\n📊 Club Logos Migration Summary:')
        self.stdout.write(f'✅ Successful: {successful_migrations}')
        self.stdout.write(f'❌ Failed: {failed_migrations}')

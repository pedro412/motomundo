"""
Simple script to show what images exist and would be migrated to Cloudinary
"""

from django.core.management.base import BaseCommand
from clubs.models import Member, Club
import os


class Command(BaseCommand):
    help = 'Show what images would be migrated to Cloudinary'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📸 Current Image Inventory'))
        self.stdout.write('=' * 50)
        
        # Check member profile pictures
        self.stdout.write('\n👤 MEMBER PROFILE PICTURES:')
        members_with_pics = Member.objects.exclude(profile_picture='').exclude(profile_picture__isnull=True)
        
        if members_with_pics.count() == 0:
            self.stdout.write(self.style.WARNING('   No member profile pictures found'))
        else:
            for i, member in enumerate(members_with_pics, 1):
                pic_path = member.profile_picture.name
                try:
                    full_path = member.profile_picture.path
                    file_exists = os.path.exists(full_path)
                    file_size = os.path.getsize(full_path) if file_exists else 0
                    size_kb = round(file_size / 1024, 1)
                    status = '✅' if file_exists else '❌'
                except:
                    status = '❓'
                    size_kb = 0
                    
                self.stdout.write(f'   {i}. {status} {member.first_name} {member.last_name}')
                self.stdout.write(f'      File: {pic_path}')
                self.stdout.write(f'      Size: {size_kb} KB')
                self.stdout.write('')
        
        # Check club logos
        self.stdout.write('🏛️  CLUB LOGOS:')
        clubs_with_logos = Club.objects.exclude(logo='').exclude(logo__isnull=True)
        
        if clubs_with_logos.count() == 0:
            self.stdout.write(self.style.WARNING('   No club logos found'))
        else:
            for i, club in enumerate(clubs_with_logos, 1):
                logo_path = club.logo.name
                try:
                    full_path = club.logo.path
                    file_exists = os.path.exists(full_path)
                    file_size = os.path.getsize(full_path) if file_exists else 0
                    size_kb = round(file_size / 1024, 1)
                    status = '✅' if file_exists else '❌'
                except:
                    status = '❓'
                    size_kb = 0
                    
                self.stdout.write(f'   {i}. {status} {club.name}')
                self.stdout.write(f'      File: {logo_path}')
                self.stdout.write(f'      Size: {size_kb} KB')
                self.stdout.write('')
        
        # Summary
        total_images = members_with_pics.count() + clubs_with_logos.count()
        self.stdout.write('=' * 50)
        self.stdout.write(f'📊 SUMMARY:')
        self.stdout.write(f'   Member profile pictures: {members_with_pics.count()}')
        self.stdout.write(f'   Club logos: {clubs_with_logos.count()}')
        self.stdout.write(f'   Total images to migrate: {total_images}')
        
        if total_images > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🚀 Ready for Cloudinary migration!'))
            self.stdout.write('   Next steps:')
            self.stdout.write('   1. Add Cloudinary credentials to .env file')
            self.stdout.write('   2. Run: python manage.py migrate_images_to_cloudinary --dry-run --force')
            self.stdout.write('   3. Run: python manage.py migrate_images_to_cloudinary')
        else:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('ℹ️  No images found to migrate'))

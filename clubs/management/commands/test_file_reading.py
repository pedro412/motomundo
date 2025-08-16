"""
Test migration command to verify file reading works correctly
"""

import os
from django.core.management.base import BaseCommand
from clubs.models import Member, Club


class Command(BaseCommand):
    help = 'Test file reading for migration (without Cloudinary)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testing file reading for migration...'))
        
        # Test member profile pictures
        self.stdout.write('\n📸 Testing member profile picture access...')
        members_with_pics = Member.objects.exclude(profile_picture='').exclude(profile_picture__isnull=True)
        
        for i, member in enumerate(members_with_pics[:3], 1):  # Test first 3
            self.stdout.write(f'\n[{i}] Testing {member.first_name} {member.last_name}...')
            
            try:
                current_file = member.profile_picture
                self.stdout.write(f'   File name: {current_file.name}')
                
                # Test if we can read the file
                try:
                    file_content = current_file.read()
                    current_file.seek(0)  # Reset file pointer
                    file_size = len(file_content)
                    self.stdout.write(f'   ✅ Successfully read {file_size} bytes')
                    
                    # Test file access methods
                    self.stdout.write(f'   File URL: {current_file.url}')
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ Failed to read file: {e}')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Error accessing file: {e}')
                
        # Test club logos
        self.stdout.write('\n🏛️  Testing club logo access...')
        clubs_with_logos = Club.objects.exclude(logo='').exclude(logo__isnull=True)
        
        for i, club in enumerate(clubs_with_logos[:1], 1):  # Test first club
            self.stdout.write(f'\n[{i}] Testing {club.name}...')
            
            try:
                current_file = club.logo
                self.stdout.write(f'   File name: {current_file.name}')
                
                # Test if we can read the file
                try:
                    file_content = current_file.read()
                    current_file.seek(0)  # Reset file pointer
                    file_size = len(file_content)
                    self.stdout.write(f'   ✅ Successfully read {file_size} bytes')
                    
                    # Test file access methods
                    self.stdout.write(f'   File URL: {current_file.url}')
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ Failed to read file: {e}')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Error accessing file: {e}')
        
        self.stdout.write('\n🎉 File reading test completed!')

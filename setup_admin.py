#!/usr/bin/env python
"""
Create sample admin user and test data for admin interface
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, ChapterJoinRequest

def create_admin_and_test_data():
    print("Setting up admin user and test data...")
    
    # Create admin user if it doesn't exist
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@motomundo.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✓ Created admin user: {admin_user.username} (password: admin123)")
    else:
        print(f"✓ Admin user already exists: {admin_user.username}")
    
    # Update existing clubs with discovery fields if needed
    clubs_updated = 0
    for club in Club.objects.all():
        updated = False
        if not club.country:
            club.country = "Mexico"
            updated = True
        if not club.club_type:
            club.club_type = "mc"
            updated = True
        if club.is_public is None:
            club.is_public = True
            updated = True
        if club.accepts_new_chapters is None:
            club.accepts_new_chapters = True
            updated = True
        
        if updated:
            club.save()
            club.update_stats()
            clubs_updated += 1
    
    if clubs_updated > 0:
        print(f"✓ Updated {clubs_updated} clubs with discovery fields")
    
    # Create some sample join requests if none exist
    if not ChapterJoinRequest.objects.exists():
        # Create a test user for requests
        test_user, created = User.objects.get_or_create(
            username='chapter_requester',
            defaults={
                'email': 'requester@example.com',
                'first_name': 'John',
                'last_name': 'Rider'
            }
        )
        
        club = Club.objects.filter(accepts_new_chapters=True).first()
        if club:
            ChapterJoinRequest.objects.create(
                club=club,
                requested_by=test_user,
                proposed_chapter_name="Guadalajara Chapter",
                city="Guadalajara",
                state="Jalisco",
                description="A chapter for motorcycle enthusiasts in Guadalajara metropolitan area",
                reason="We have a growing motorcycle community in Guadalajara and would love to be part of your organization.",
                estimated_members=15
            )
            
            ChapterJoinRequest.objects.create(
                club=club,
                requested_by=test_user,
                proposed_chapter_name="Monterrey Chapter",
                city="Monterrey",
                state="Nuevo León",
                description="Expanding the club presence to northern Mexico",
                reason="Strong motorcycle culture in Monterrey and surrounding areas.",
                estimated_members=20
            )
            
            print("✓ Created sample join requests")
    
    print("\n" + "="*50)
    print("ADMIN SETUP COMPLETE")
    print("="*50)
    print("You can now access the admin at: http://localhost:8000/admin/")
    print("Username: admin")
    print("Password: admin123")
    print("")
    print("New features in admin:")
    print("- Club discovery fields (type, location, visibility)")
    print("- Chapter management with ownership and contact info")
    print("- Chapter Join Requests with approval workflow")
    print("- Bulk approve/reject actions")
    print("="*50)

if __name__ == '__main__':
    create_admin_and_test_data()

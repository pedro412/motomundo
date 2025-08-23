#!/usr/bin/env python
"""
Test the new chapter creation workflow
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter

def test_chapter_independence():
    print("Testing new chapter creation capabilities...")
    
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='chapter_owner',
        defaults={
            'email': 'owner@example.com',
            'first_name': 'Chapter',
            'last_name': 'Owner'
        }
    )
    
    # Get a club
    club = Club.objects.first()
    if not club:
        print("No clubs found. Creating a test club...")
        club = Club.objects.create(
            name="Test Club",
            description="A test club for demonstration",
            club_type="mc",
            country="Mexico",
            primary_state="Mexico City",
            is_public=True,
            accepts_new_chapters=True
        )
    
    print(f"Using club: {club.name}")
    
    # Create a chapter with the new fields
    chapter_name = f"Independent Chapter {len(Chapter.objects.all()) + 1}"
    
    chapter = Chapter.objects.create(
        name=chapter_name,
        club=club,  # Still linked to club but with more independence
        city="Mexico City",
        state="Mexico City",
        description="An independent chapter with its own identity",
        owner=test_user,  # Now has an owner!
        is_public=True,
        accepts_new_members=True,
        contact_email="contact@chapter.com",
        meeting_info="Meetings every Sunday at 10 AM in Chapultepec Park"
    )
    
    print(f"✓ Created chapter: {chapter.name}")
    print(f"  Owner: {chapter.owner.get_full_name() or chapter.owner.username}")
    print(f"  Location: {chapter.city}, {chapter.state}")
    print(f"  Contact: {chapter.contact_email}")
    print(f"  Meeting info: {chapter.meeting_info}")
    print(f"  Public: {chapter.is_public}")
    print(f"  Accepts new members: {chapter.accepts_new_members}")
    
    # Update club stats
    club.update_stats()
    print(f"  Club stats - Chapters: {club.total_chapters}, Members: {club.total_members}")
    
    print("\n✅ Chapter creation successful!")
    print("📋 Now check the admin interface to see all the new fields and options!")

if __name__ == '__main__':
    test_chapter_independence()

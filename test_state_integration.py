#!/usr/bin/env python
"""
Test the new State model integration
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Country, State

def test_state_model_integration():
    print("Testing State model integration...")
    
    # Get Mexico and some states
    mexico = Country.objects.get(code='MX')
    jalisco = State.objects.get(country=mexico, name='Jalisco')
    cdmx = State.objects.get(country=mexico, name='Ciudad de México')
    
    print(f"Country: {mexico}")
    print(f"Available states: {State.objects.count()}")
    print(f"Sample states: {jalisco}, {cdmx}")
    
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='state_test_user',
        defaults={
            'email': 'statetest@example.com',
            'first_name': 'State',
            'last_name': 'Test'
        }
    )
    
    # Get a club
    club = Club.objects.first()
    if not club:
        club = Club.objects.create(
            name="State Test Club",
            description="Testing state integration",
            club_type="mc",
            country_new=mexico,
            primary_state_new=jalisco,
            is_public=True,
            accepts_new_chapters=True
        )
        print(f"Created test club: {club.name}")
    
    # Create a chapter with proper state
    chapter_name = f"Jalisco Chapter {len(Chapter.objects.all()) + 1}"
    
    chapter = Chapter.objects.create(
        name=chapter_name,
        club=club,
        city="Guadalajara",
        state_new=jalisco,  # Using the new state field
        description="A chapter in Jalisco state",
        owner=test_user,
        is_public=True,
        accepts_new_members=True,
        contact_email="jalisco@chapter.com",
        meeting_info="Meetings every Saturday at 3 PM in Chapala"
    )
    
    print(f"✓ Created chapter: {chapter.name}")
    print(f"  Location: {chapter.city}, {chapter.state_new}")
    print(f"  State ID: {chapter.state_new.id}")
    print(f"  Country: {chapter.state_new.country}")
    
    # Test chapter with different state
    chapter2 = Chapter.objects.create(
        name="CDMX Test Chapter",
        club=club,
        city="Mexico City",
        state_new=cdmx,
        description="A chapter in Mexico City",
        owner=test_user,
        is_public=True,
        accepts_new_members=True,
        contact_email="cdmx@chapter.com"
    )
    
    print(f"✓ Created chapter: {chapter2.name}")
    print(f"  Location: {chapter2.city}, {chapter2.state_new}")
    
    # Update club stats
    club.update_stats()
    print(f"  Club stats - Chapters: {club.total_chapters}, Members: {club.total_members}")
    
    # Test querying by state
    jalisco_chapters = Chapter.objects.filter(state_new=jalisco)
    cdmx_chapters = Chapter.objects.filter(state_new=cdmx)
    
    print(f"\nChapters in Jalisco: {jalisco_chapters.count()}")
    print(f"Chapters in CDMX: {cdmx_chapters.count()}")
    
    # Test state dropdown options
    all_states = State.objects.filter(country=mexico).order_by('name')
    print(f"\nAll Mexico states available for selection: {all_states.count()}")
    print(f"First 5: {[s.name for s in all_states[:5]]}")
    
    print("\n✅ State model integration successful!")
    print("📋 Now check the admin interface - you should see:")
    print("   - Country and State models in the admin")
    print("   - Dropdowns for selecting states instead of text fields")
    print("   - Proper filtering by state in club and chapter lists")

if __name__ == '__main__':
    test_state_model_integration()

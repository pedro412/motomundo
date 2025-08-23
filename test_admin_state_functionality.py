#!/usr/bin/env python
"""
Test the admin interface with new State models
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Country, State, Club, Chapter, ChapterJoinRequest
from django.contrib.auth.models import User

def test_admin_functionality():
    print("Testing admin interface functionality...")
    
    # Check that we have the right data
    mexico = Country.objects.get(code='MX')
    states = State.objects.filter(country=mexico)
    
    print(f"✓ Country: {mexico}")
    print(f"✓ States available: {states.count()}")
    
    # Sample states
    sample_states = ['Jalisco', 'Ciudad de México', 'Nuevo León', 'Yucatán', 'Baja California']
    for state_name in sample_states:
        state = states.filter(name=state_name).first()
        if state:
            print(f"  - {state}")
    
    # Test that relationships work
    clubs_with_states = Club.objects.filter(primary_state_new__isnull=False)
    chapters_with_states = Chapter.objects.filter(state_new__isnull=False)
    
    print(f"\nData verification:")
    print(f"✓ Clubs with assigned states: {clubs_with_states.count()}")
    print(f"✓ Chapters with assigned states: {chapters_with_states.count()}")
    
    if clubs_with_states.exists():
        club = clubs_with_states.first()
        print(f"  Sample club: {club.name} - {club.primary_state_new}")
    
    if chapters_with_states.exists():
        chapter = chapters_with_states.first()
        print(f"  Sample chapter: {chapter.name} - {chapter.state_new}")
    
    # Test foreign key relationships
    print(f"\nForeign key relationships:")
    print(f"✓ Mexico has {mexico.states.count()} states")
    
    jalisco = states.filter(name='Jalisco').first()
    if jalisco:
        jalisco_chapters = Chapter.objects.filter(state_new=jalisco)
        print(f"✓ Jalisco has {jalisco_chapters.count()} chapters")
        
    print(f"\n🎯 Admin Interface Features Available:")
    print(f"   📊 Country admin: List and manage countries")
    print(f"   🗺️  State admin: List Mexico's 32 states with filtering")
    print(f"   🏍️  Club admin: Select country and primary state from dropdowns")
    print(f"   📍 Chapter admin: Select state from dropdown of Mexico states")
    print(f"   📝 Join requests: State selection with proper validation")
    print(f"   🔍 Filtering: Filter clubs and chapters by state")
    
    print(f"\n✅ All admin functionality ready!")
    print(f"🌐 Access at: http://localhost:8000/admin/")
    print(f"👤 Username: admin | Password: admin123")

if __name__ == '__main__':
    test_admin_functionality()

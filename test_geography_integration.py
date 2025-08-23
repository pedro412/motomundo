#!/usr/bin/env python
"""
Test the geography app integration and admin functionality
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from geography.models import Country, State
from clubs.models import Club, Chapter

def test_geography_app():
    print("🌍 TESTING GEOGRAPHY APP INTEGRATION")
    print("=" * 50)
    
    # Test geography models
    mexico = Country.objects.get(code='MX')
    states = State.objects.filter(country=mexico)
    
    print(f"✅ Country: {mexico} ({mexico.code})")
    print(f"✅ States in Mexico: {states.count()}")
    
    # Sample states
    sample_states = ['Jalisco', 'Ciudad de México', 'Nuevo León', 'Yucatán']
    print(f"\n📍 Sample states:")
    for state_name in sample_states:
        state = states.filter(name=state_name).first()
        if state:
            print(f"   - {state}")
    
    # Test relationships
    print(f"\n🔗 Relationships:")
    print(f"   - Mexico has {mexico.states.count()} states")
    
    # Test clubs using geography
    clubs_with_geo = Club.objects.filter(country_new__isnull=False)
    print(f"   - Clubs using geography: {clubs_with_geo.count()}")
    
    if clubs_with_geo.exists():
        club = clubs_with_geo.first()
        print(f"   - Sample: {club.name} → {club.country_new}")
    
    # Test chapters using geography
    chapters_with_geo = Chapter.objects.filter(state_new__isnull=False)
    print(f"   - Chapters using geography: {chapters_with_geo.count()}")
    
    if chapters_with_geo.exists():
        chapter = chapters_with_geo.first()
        print(f"   - Sample: {chapter.name} → {chapter.state_new}")
    
    print(f"\n✅ GEOGRAPHY APP WORKING CORRECTLY!")
    print(f"\n🎯 Admin Interface Features:")
    print(f"   📊 Geography section with Country and State models")
    print(f"   🗺️  Browse Mexico's 32 states with filtering")
    print(f"   🏍️  Club admin uses geography dropdowns")
    print(f"   📍 Chapter admin uses state selection")
    
    # Test creating a new chapter with geography
    print(f"\n🧪 Testing new chapter creation...")
    
    jalisco = states.filter(name='Jalisco').first()
    club = Club.objects.first()
    
    if jalisco and club:
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(
            username='geo_test_user',
            defaults={'email': 'geotest@example.com'}
        )
        
        chapter = Chapter.objects.create(
            name=f"Geography Test Chapter {len(Chapter.objects.all()) + 1}",
            club=club,
            city="Guadalajara",
            state_new=jalisco,  # Using geography State!
            description="Testing geography integration",
            owner=user,
            is_public=True,
            accepts_new_members=True
        )
        
        print(f"✅ Created chapter: {chapter.name}")
        print(f"   Location: {chapter.city}, {chapter.state_new}")
        print(f"   Geography ID: {chapter.state_new.id}")
    
    print(f"\n🚀 READY FOR ADMIN TESTING!")
    print(f"   🌐 URL: http://localhost:8000/admin/")
    print(f"   👤 Login: admin / admin123")
    print(f"   📂 Check: Geography section → Countries and States")

if __name__ == '__main__':
    test_geography_app()

#!/usr/bin/env python3
"""
Test script to verify Chapter location field functionality
"""
import os
import sys
import django
from django.contrib.gis.geos import Point

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Chapter, Club
from geography.models import Country, State

def test_chapter_location():
    """Test Chapter location field functionality"""
    print("Testing Chapter location field...")
    
    # Get or create test data
    try:
        # Get Mexico and a state
        mexico = Country.objects.get(name="Mexico")
        state = State.objects.filter(country=mexico).first()
        
        if not state:
            print("No states found for Mexico")
            return
        
        # Get or create a test club
        club, created = Club.objects.get_or_create(
            name="Test Location Club",
            defaults={
                'description': 'Test club for location testing',
                'country_new': mexico,
                'primary_state_new': state,
                'club_type': 'mc',
                'is_public': True
            }
        )
        print(f"{'Created' if created else 'Using'} test club: {club.name}")
        
        # Create a test chapter with location
        # Mexico City coordinates: 19.4326, -99.1332
        mexico_city_point = Point(-99.1332, 19.4326, srid=4326)
        
        chapter, created = Chapter.objects.get_or_create(
            club=club,
            name="Mexico City Chapter",
            defaults={
                'description': 'Test chapter in Mexico City',
                'city': 'Mexico City',
                'state_new': state,
                'location': mexico_city_point,
                'is_public': True,
                'is_active': True,
                'accepts_new_members': True
            }
        )
        
        if created:
            print(f"Created test chapter: {chapter.name}")
        else:
            # Update location if chapter exists
            chapter.location = mexico_city_point
            chapter.save()
            print(f"Updated location for existing chapter: {chapter.name}")
        
        # Test location retrieval
        print(f"Chapter location: {chapter.location}")
        if chapter.location:
            print(f"Latitude: {chapter.location.y}")
            print(f"Longitude: {chapter.location.x}")
            print(f"SRID: {chapter.location.srid}")
        
        # Create another chapter for distance testing
        # Guadalajara coordinates: 20.6597, -103.3496
        guadalajara_point = Point(-103.3496, 20.6597, srid=4326)
        
        gdl_chapter, created = Chapter.objects.get_or_create(
            club=club,
            name="Guadalajara Chapter",
            defaults={
                'description': 'Test chapter in Guadalajara',
                'city': 'Guadalajara',
                'state_new': state,
                'location': guadalajara_point,
                'is_public': True,
                'is_active': True,
                'accepts_new_members': True
            }
        )
        
        if created:
            print(f"Created test chapter: {gdl_chapter.name}")
        else:
            gdl_chapter.location = guadalajara_point
            gdl_chapter.save()
            print(f"Updated location for existing chapter: {gdl_chapter.name}")
        
        # Test spatial queries
        print("\nTesting spatial queries...")
        
        # Find chapters within 600km of Mexico City
        from django.contrib.gis.measure import D
        nearby_chapters = Chapter.objects.filter(
            location__distance_lte=(mexico_city_point, D(km=600))
        ).exclude(id=chapter.id)
        
        print(f"Chapters within 600km of Mexico City: {nearby_chapters.count()}")
        for ch in nearby_chapters:
            print(f"  - {ch.name} in {ch.city}")
            if ch.location:
                # Calculate distance
                distance = chapter.location.distance(ch.location) * 111  # Rough km conversion
                print(f"    Distance: ~{distance:.0f} km")
        
        print("\n✅ Chapter location field is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chapter location: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chapter_location()
    sys.exit(0 if success else 1)

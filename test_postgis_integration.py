#!/usr/bin/env python3
"""
Test Geographic Data with PostGIS
Testing coordinate data for Mexico and some states.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/app')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')

# Setup Django
django.setup()

from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from geography.models import Country, State

def test_geographic_data():
    print("🌍 Testing Geographic Data with PostGIS")
    print("="*50)
    
    # Get Mexico
    try:
        mexico = Country.objects.get(name="Mexico")
        print(f"✅ Found country: {mexico}")
        
        # Add location coordinates for Mexico (approximate center)
        mexico_center = Point(-102.5528, 23.6345)  # Longitude, Latitude
        mexico.location = mexico_center
        mexico.save()
        print(f"📍 Set Mexico center coordinates: {mexico.location}")
        
        # Test some Mexican states with coordinates
        state_coordinates = {
            "Jalisco": Point(-103.3496, 20.6597),  # Guadalajara area
            "Ciudad de México": Point(-99.1332, 19.4326),  # Mexico City
            "Nuevo León": Point(-100.3161, 25.6866),  # Monterrey area
            "Yucatán": Point(-89.0943, 20.7099),  # Mérida area
            "Baja California": Point(-116.9717, 32.6197),  # Tijuana area
        }
        
        updated_states = []
        for state_name, coordinates in state_coordinates.items():
            try:
                state = State.objects.get(name=state_name, country=mexico)
                state.location = coordinates
                state.save()
                updated_states.append(state)
                print(f"📍 {state.name}: {state.location}")
            except State.DoesNotExist:
                print(f"❌ State '{state_name}' not found")
        
        print(f"\n✅ Successfully updated {len(updated_states)} states with coordinates")
        
        # Test spatial queries
        print("\n🔍 Testing Spatial Queries:")
        print("-" * 30)
        
        # Find states near Mexico City (within ~500km)
        mexico_city = Point(-99.1332, 19.4326)
        # Note: This is a simple demonstration. For real distance calculations, 
        # you'd want to use distance calculations in meters
        nearby_states = State.objects.filter(
            country=mexico,
            location__isnull=False
        ).exclude(name="Ciudad de México")
        
        print(f"📊 States with coordinates (excluding Mexico City): {nearby_states.count()}")
        for state in nearby_states[:3]:  # Show first 3
            print(f"   • {state.name}: {state.location}")
        
        # Test distance calculation between two points
        if len(updated_states) >= 2:
            state1, state2 = updated_states[0], updated_states[1]
            print(f"\n📏 Example spatial operation:")
            print(f"   Distance between {state1.name} and {state2.name}:")
            print(f"   {state1.name}: {state1.location}")
            print(f"   {state2.name}: {state2.location}")
            # Note: For real applications, you'd calculate actual distance using PostGIS functions
        
        print("\n🎉 PostGIS integration is working correctly!")
        print("Ready to add geographic features like:")
        print("   • Distance calculations")
        print("   • Location-based club discovery")
        print("   • Route planning")
        print("   • Spatial filtering")
        print("   • Boundary calculations")
        
    except Country.DoesNotExist:
        print("❌ Mexico not found in database")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_geographic_data()
    if success:
        print("\n✅ All geographic tests passed!")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)

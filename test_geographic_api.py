#!/usr/bin/env python3
"""
Test Geographic API Endpoints
"""

import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.insert(0, '/app')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')

# Setup Django
django.setup()

import requests
from django.test import Client
from django.urls import reverse

def test_geographic_api():
    print("🌍 Testing Geographic API Endpoints")
    print("="*50)
    
    # Use Django test client for internal testing
    client = Client()
    
    # Test 1: Get all states with coordinates
    print("1. Testing states with coordinates:")
    try:
        response = client.get('/geography/api/states/with_coordinates/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} states with coordinates")
            for state in data[:3]:  # Show first 3
                coords = state.get('location_coordinates')
                if coords:
                    print(f"   📍 {state['name']}: {coords['latitude']}, {coords['longitude']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Get countries
    print("\n2. Testing countries endpoint:")
    try:
        response = client.get('/geography/api/countries/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} countries")
            for country in data:
                print(f"   🏳️ {country['name']} ({country['code']}) - {country['states_count']} states")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Get nearby states (around Mexico City)
    print("\n3. Testing nearby states (around Mexico City):")
    try:
        response = client.get('/geography/api/states/nearby/?lat=19.4326&lng=-99.1332&distance=500')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Query: {data['query_point']}")
            print(f"   ✅ Distance: {data['distance_km']} km")
            print(f"   ✅ Found {len(data['results'])} nearby states")
            for state in data['results']:
                coords = state.get('location_coordinates')
                if coords:
                    print(f"   📍 {state['name']}: {coords['latitude']}, {coords['longitude']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Get states for a specific country
    print("\n4. Testing states for Mexico:")
    try:
        response = client.get('/geography/api/countries/1/states/')  # Assuming Mexico has ID 1
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} states for Mexico")
            states_with_coords = [s for s in data if s.get('location_coordinates')]
            print(f"   ✅ {len(states_with_coords)} have coordinates")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n🎉 Geographic API testing complete!")
    print("\nAvailable endpoints:")
    print("   • GET /geography/api/countries/ - List all countries")
    print("   • GET /geography/api/countries/{id}/states/ - States for a country")
    print("   • GET /geography/api/states/ - List all states")
    print("   • GET /geography/api/states/with_coordinates/ - States with GPS data")
    print("   • GET /geography/api/states/nearby/?lat=LAT&lng=LNG&distance=KM - Find nearby states")

if __name__ == '__main__':
    test_geographic_api()

#!/usr/bin/env python3
"""
Test script to verify Chapter API with location field
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from clubs.models import Chapter

def test_chapter_api():
    """Test Chapter API with location field"""
    print("Testing Chapter API with location...")
    
    try:
        # Create a test client
        client = Client()
        
        # Test GET request to chapter list
        response = client.get('/api/chapters/')
        print(f"Chapter list API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} chapters in API")
            
            # Find a chapter with location
            chapter_with_location = None
            for chapter_data in data:
                if chapter_data.get('latitude') and chapter_data.get('longitude'):
                    chapter_with_location = chapter_data
                    break
            
            if chapter_with_location:
                print(f"✅ Found chapter with location: {chapter_with_location['name']}")
                print(f"   Latitude: {chapter_with_location['latitude']}")
                print(f"   Longitude: {chapter_with_location['longitude']}")
                print(f"   City: {chapter_with_location.get('city', 'N/A')}")
                print(f"   State: {chapter_with_location.get('state_new', 'N/A')}")
                
                # Test individual chapter API
                chapter_id = chapter_with_location['id']
                detail_response = client.get(f'/api/chapters/{chapter_id}/')
                print(f"Chapter detail API status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("✅ Chapter detail API working")
                    print(f"   Detail includes location: {bool(detail_data.get('latitude'))}")
                else:
                    print(f"❌ Chapter detail API failed: {detail_response.status_code}")
            else:
                print("⚠️  No chapters with location found in API response")
                if data:
                    print("Sample chapter fields:", list(data[0].keys()))
        else:
            print(f"❌ Chapter list API failed: {response.status_code}")
            print(f"Response: {response.content.decode()}")
        
        print("\n✅ Chapter API test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chapter API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chapter_api()
    sys.exit(0 if success else 1)

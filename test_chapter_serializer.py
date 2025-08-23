#!/usr/bin/env python3
"""
Simple test of Chapter serializer with location fields
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Chapter
from clubs.serializers import ChapterSerializer

def test_chapter_serializer():
    """Test Chapter serializer with location"""
    print("Testing Chapter serializer with location...")
    
    try:
        # Get a chapter with location
        chapter = Chapter.objects.filter(location__isnull=False).first()
        
        if not chapter:
            print("No chapters with location found")
            return False
        
        print(f"Testing chapter: {chapter.name}")
        print(f"Location: {chapter.location}")
        
        # Serialize the chapter
        serializer = ChapterSerializer(chapter)
        data = serializer.data
        
        print(f"Serialized data keys: {list(data.keys())}")
        print(f"Name: {data.get('name')}")
        print(f"City: {data.get('city')}")
        print(f"Latitude: {data.get('latitude')}")
        print(f"Longitude: {data.get('longitude')}")
        print(f"Location field: {data.get('location')}")
        
        # Check if location fields are properly included
        if data.get('latitude') and data.get('longitude'):
            print("✅ Location fields properly serialized")
        else:
            print("❌ Location fields missing in serialization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chapter serializer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chapter_serializer()
    sys.exit(0 if success else 1)

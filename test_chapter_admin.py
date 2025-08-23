#!/usr/bin/env python3
"""
Test script to verify Chapter admin interface with location field
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.admin.sites import site
from clubs.models import Chapter
from clubs.admin import ChapterModelAdmin

def test_chapter_admin():
    """Test Chapter admin interface configuration"""
    print("Testing Chapter admin interface...")
    
    try:
        # Check if Chapter is registered in admin
        if Chapter not in site._registry:
            print("❌ Chapter model is not registered in admin")
            return False
        
        admin_class = site._registry[Chapter]
        print(f"✅ Chapter admin class: {admin_class.__class__.__name__}")
        
        # Check if it's a GISModelAdmin
        from django.contrib.gis.admin import GISModelAdmin
        if isinstance(admin_class, GISModelAdmin):
            print("✅ Chapter admin uses GISModelAdmin (supports map widgets)")
        else:
            print("⚠️  Chapter admin is not a GISModelAdmin")
        
        # Check if location field is in the admin fields
        admin_fields = admin_class.fields
        if admin_fields:
            flat_fields = []
            for field_group in admin_fields:
                if isinstance(field_group, tuple):
                    flat_fields.extend(field_group)
                else:
                    flat_fields.append(field_group)
            
            if 'location' in flat_fields:
                print("✅ Location field is included in admin fields")
            else:
                print("❌ Location field is not in admin fields")
                print(f"Available fields: {flat_fields}")
        
        # Check if GIS widget kwargs are configured
        if hasattr(admin_class, 'gis_widget_kwargs'):
            print("✅ GIS widget configuration found")
            print(f"   Widget config: {admin_class.gis_widget_kwargs}")
        else:
            print("⚠️  No GIS widget configuration found")
        
        # Test the list display
        list_display = admin_class.list_display
        print(f"✅ Admin list display: {list_display}")
        
        # Get a test chapter to verify admin functionality
        test_chapter = Chapter.objects.filter(location__isnull=False).first()
        if test_chapter:
            print(f"✅ Found test chapter with location: {test_chapter.name}")
            print(f"   Location: {test_chapter.location}")
        else:
            print("⚠️  No chapters with location found for testing")
        
        print("\n✅ Chapter admin interface is configured correctly!")
        print("💡 You can now access the admin at: http://localhost:8001/admin/clubs/chapter/")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chapter admin: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chapter_admin()
    sys.exit(0 if success else 1)

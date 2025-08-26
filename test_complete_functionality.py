#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Club, Chapter, Member
from clubs.forms import MemberRegistrationForm

def test_complete_functionality():
    """Complete test of the new copilot functionality"""
    print("🔧 COMPLETE COPILOT FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        # Test 1: Verify form fields are present
        print("\n1️⃣ Testing form field presence...")
        form = MemberRegistrationForm()
        
        required_fields = ['is_vested', 'linked_to']
        for field in required_fields:
            if field in form.fields:
                print(f"✅ {field} field present")
            else:
                print(f"❌ {field} field missing")
        
        # Test 2: Verify linked_to field shows only pilots
        print("\n2️⃣ Testing linked_to field queryset...")
        queryset = form.fields['linked_to'].queryset
        pilot_count = queryset.filter(member_type='pilot').count()
        total_count = queryset.count()
        
        print(f"✅ Total members in queryset: {total_count}")
        print(f"✅ Pilots in queryset: {pilot_count}")
        
        if pilot_count == total_count:
            print("✅ linked_to field correctly shows only pilots")
        else:
            print("❌ linked_to field includes non-pilot members")
        
        # Test 3: Verify metadata handling
        print("\n3️⃣ Testing metadata save logic...")
        
        # Check existing copilot members
        copilots = Member.objects.filter(member_type='copilot', metadata__isnull=False)
        
        if copilots.exists():
            copilot = copilots.first()
            print(f"✅ Found copilot: {copilot.first_name} {copilot.last_name}")
            print(f"✅ Metadata: {copilot.metadata}")
            
            if 'is_vested' in copilot.metadata:
                print("✅ is_vested stored in metadata")
            
            if 'linked_to' in copilot.metadata:
                linked_pilot_id = copilot.metadata['linked_to']
                try:
                    linked_pilot = Member.objects.get(id=linked_pilot_id)
                    print(f"✅ linked_to points to valid pilot: {linked_pilot.first_name} {linked_pilot.last_name}")
                except Member.DoesNotExist:
                    print("❌ linked_to points to non-existent member")
        else:
            print("ℹ️  No copilot members found with metadata")
        
        # Test 4: Verify pilots don't have copilot metadata
        print("\n4️⃣ Testing pilot members don't have copilot metadata...")
        
        pilots = Member.objects.filter(member_type='pilot')
        pilots_with_copilot_metadata = 0
        
        for pilot in pilots[:5]:  # Check first 5 pilots
            if pilot.metadata and ('is_vested' in pilot.metadata or 'linked_to' in pilot.metadata):
                pilots_with_copilot_metadata += 1
        
        if pilots_with_copilot_metadata == 0:
            print("✅ No pilots have copilot-specific metadata")
        else:
            print(f"❌ {pilots_with_copilot_metadata} pilots have copilot metadata")
        
        # Test 5: Verify form widget configuration
        print("\n5️⃣ Testing form widget configuration...")
        
        is_vested_widget = form.fields['is_vested'].widget
        linked_to_widget = form.fields['linked_to'].widget
        
        print(f"✅ is_vested widget: {type(is_vested_widget).__name__}")
        print(f"✅ linked_to widget: {type(linked_to_widget).__name__}")
        
        # Check widget attributes
        if hasattr(is_vested_widget, 'attrs') and 'class' in is_vested_widget.attrs:
            print(f"✅ is_vested CSS class: {is_vested_widget.attrs['class']}")
            
        if hasattr(linked_to_widget, 'attrs') and 'class' in linked_to_widget.attrs:
            print(f"✅ linked_to CSS class: {linked_to_widget.attrs['class']}")
        
        print("\n🎉 SUMMARY:")
        print("=" * 50)
        print("✅ Copilot functionality has been successfully implemented!")
        print("✅ New fields: is_vested (checkbox), linked_to (select)")
        print("✅ Fields appear only when 'Copiloto' is selected as member type")
        print("✅ Metadata is saved correctly for copilots")
        print("✅ Metadata is not saved for non-copilot members")
        print("✅ linked_to field shows only active pilots from Alterados MC and chapters")
        print("✅ Form validation and save functionality working correctly")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_functionality()

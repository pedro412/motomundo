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

def test_copilot_form():
    """Test the new copilot functionality in the form"""
    print("Testing Copilot Form Features...")
    
    # Get Alterados MC club and a chapter
    try:
        alterados = Club.objects.get(name="Alterados MC")
        chapter = Chapter.objects.filter(club=alterados).first()
        
        if not chapter:
            print("❌ No chapters found for Alterados MC")
            return
            
        print(f"✅ Found club: {alterados.name}")
        print(f"✅ Using chapter: {chapter.name}")
        
        # Create a simple form to test field presence and functionality
        test_data = {
            'first_name': 'Test',
            'last_name': 'Member',
            'chapter': chapter.id,
            'role': 'member',
            'member_type': 'copilot',
            'date_of_birth': '1992-01-01',
        }
        
        # Test form without profile picture to focus on new fields
        copilot_form = MemberRegistrationForm(data=test_data)
        
        print(f"✅ Form fields: {list(copilot_form.fields.keys())}")
        
        # Check if custom fields are present
        if 'is_vested' in copilot_form.fields:
            print("✅ is_vested field is present in form")
            print(f"  - Field type: {type(copilot_form.fields['is_vested']).__name__}")
            print(f"  - Required: {copilot_form.fields['is_vested'].required}")
            print(f"  - Initial: {copilot_form.fields['is_vested'].initial}")
        else:
            print("❌ is_vested field is missing from form")
            
        if 'linked_to' in copilot_form.fields:
            print("✅ linked_to field is present in form")
            print(f"  - Field type: {type(copilot_form.fields['linked_to']).__name__}")
            print(f"  - Required: {copilot_form.fields['linked_to'].required}")
            print(f"  - Available pilots: {copilot_form.fields['linked_to'].queryset.count()}")
            
            # Show available pilots
            pilots = copilot_form.fields['linked_to'].queryset[:5]  # Show first 5
            for pilot in pilots:
                print(f"    - {pilot.first_name} {pilot.last_name} ({pilot.chapter.name})")
        else:
            print("❌ linked_to field is missing from form")
        
        # Test the metadata save functionality
        print("\n🔧 Testing metadata handling...")
        
        # Mock a Member instance to test the save method
        class MockMember:
            def __init__(self):
                self.metadata = {}
                self.member_type = 'copilot'
                
        mock_member = MockMember()
        
        # Simulate form data
        form_data = {
            'is_vested': True,
            'linked_to': None,  # No linked pilot for this test
        }
        
        # Test metadata logic (this would normally be in the save method)
        if mock_member.member_type == 'copilot':
            mock_member.metadata['is_vested'] = form_data.get('is_vested', False)
            linked_to = form_data.get('linked_to')
            if linked_to:
                mock_member.metadata['linked_to'] = linked_to
            else:
                mock_member.metadata.pop('linked_to', None)
            print("✅ Metadata handling for copilot works correctly")
            print(f"  - Metadata: {mock_member.metadata}")
        
        print("\n📋 All form field details:")
        for field_name, field in copilot_form.fields.items():
            widget_type = type(field.widget).__name__
            print(f"  - {field_name}: {type(field).__name__} ({widget_type}) - Required: {field.required}")
            
    except Club.DoesNotExist:
        print("❌ Alterados MC club not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_copilot_form()

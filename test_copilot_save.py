#!/usr/bin/env python
import os
import sys
import django
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Add the project directory to the Python path
sys.path.append('/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Club, Chapter, Member
from clubs.forms import MemberRegistrationForm

def test_copilot_save():
    """Test saving a copilot member with the new metadata fields"""
    print("Testing Copilot Save Functionality...")
    
    try:
        alterados = Club.objects.get(name="Alterados MC")
        chapter = Chapter.objects.filter(club=alterados).first()
        
        print(f"✅ Using club: {alterados.name}")
        print(f"✅ Using chapter: {chapter.name}")
        
        # Get an existing pilot to link to
        existing_pilot = Member.objects.filter(
            chapter__club=alterados,
            member_type='pilot',
            is_active=True
        ).first()
        
        if existing_pilot:
            print(f"✅ Found existing pilot: {existing_pilot.first_name} {existing_pilot.last_name}")
        else:
            print("ℹ️  No existing pilot found, creating one first...")
            # Create a minimal test image file
            image_content = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
            test_image = SimpleUploadedFile("test_pilot.gif", image_content, content_type="image/gif")
            
            pilot_data = {
                'first_name': 'Test',
                'last_name': 'Pilot',
                'nickname': 'TestPilot',
                'chapter': chapter.id,
                'role': 'member',
                'member_type': 'pilot',
                'date_of_birth': '1990-01-01',
            }
            
            pilot_form = MemberRegistrationForm(data=pilot_data, files={'profile_picture': test_image})
            if pilot_form.is_valid():
                existing_pilot = pilot_form.save()
                print(f"✅ Created test pilot: {existing_pilot.first_name} {existing_pilot.last_name}")
            else:
                print(f"❌ Failed to create pilot: {pilot_form.errors}")
                return
        
        # Now create a copilot linked to the pilot
        print("\n🔧 Creating copilot member...")
        
        # Create another minimal test image
        image_content = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        test_image = SimpleUploadedFile("test_copilot.gif", image_content, content_type="image/gif")
        
        copilot_data = {
            'first_name': 'Test',
            'last_name': 'Copilot',
            'nickname': 'TestCopilot',
            'chapter': chapter.id,
            'role': 'member',
            'member_type': 'copilot',
            'date_of_birth': '1992-01-01',
            'is_vested': True,
            'linked_to': existing_pilot.id,
        }
        
        copilot_form = MemberRegistrationForm(data=copilot_data, files={'profile_picture': test_image})
        
        if copilot_form.is_valid():
            copilot = copilot_form.save()
            print(f"✅ Created copilot: {copilot.first_name} {copilot.last_name}")
            print(f"✅ Member type: {copilot.member_type}")
            print(f"✅ Metadata: {copilot.metadata}")
            
            # Verify the metadata was saved correctly
            if copilot.metadata.get('is_vested') == True:
                print("✅ is_vested metadata saved correctly")
            else:
                print("❌ is_vested metadata not saved correctly")
                
            if copilot.metadata.get('linked_to') == existing_pilot.id:
                print(f"✅ linked_to metadata saved correctly (linked to pilot ID: {existing_pilot.id})")
            else:
                print("❌ linked_to metadata not saved correctly")
                
            # Test creating a pilot (should not have copilot metadata)
            print("\n🔧 Testing pilot member (should not have copilot metadata)...")
            
            pilot_image = SimpleUploadedFile("test_pilot2.gif", image_content, content_type="image/gif")
            pilot_data = {
                'first_name': 'Another',
                'last_name': 'Pilot',
                'chapter': chapter.id,
                'role': 'member',
                'member_type': 'pilot',
                'date_of_birth': '1988-01-01',
                'is_vested': True,  # This should be ignored for pilots
                'linked_to': existing_pilot.id,  # This should also be ignored
            }
            
            pilot_form = MemberRegistrationForm(data=pilot_data, files={'profile_picture': pilot_image})
            
            if pilot_form.is_valid():
                pilot = pilot_form.save()
                print(f"✅ Created pilot: {pilot.first_name} {pilot.last_name}")
                print(f"✅ Metadata: {pilot.metadata}")
                
                # Verify copilot metadata was NOT saved for pilot
                if 'is_vested' not in pilot.metadata and 'linked_to' not in pilot.metadata:
                    print("✅ Copilot metadata correctly excluded for pilot members")
                else:
                    print("❌ Copilot metadata incorrectly saved for pilot member")
            else:
                print(f"❌ Failed to create pilot: {pilot_form.errors}")
                
        else:
            print(f"❌ Failed to create copilot: {copilot_form.errors}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_copilot_save()

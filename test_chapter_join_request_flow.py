#!/usr/bin/env python3
"""
Test script to verify chapter creation now goes through join request process
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
from clubs.models import Club, Chapter, ChapterJoinRequest, ClubAdmin
from geography.models import Country, State

def test_chapter_creation_flow():
    """Test that chapter creation now goes through join request process"""
    print("Testing chapter creation flow...")
    
    try:
        # Create test data
        mexico = Country.objects.get(name="Mexico")
        state = State.objects.filter(country=mexico).first()
        
        # Create a test club
        test_club, created = Club.objects.get_or_create(
            name="Test Join Request Club",
            defaults={
                'description': 'Club for testing join request flow',
                'country_new': mexico,
                'primary_state_new': state,
                'club_type': 'mc',
                'is_public': True,
                'accepts_new_chapters': True
            }
        )
        
        # Create a test user (non-superuser)
        test_user, created = User.objects.get_or_create(
            username='testchapteruser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
        
        # Create a test client and force login
        client = Client()
        client.force_login(test_user)
        print(f"User logged in: {test_user.username}")
        
        # Count initial join requests
        initial_join_requests = ChapterJoinRequest.objects.filter(club=test_club).count()
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        
        print(f"Initial join requests: {initial_join_requests}")
        print(f"Initial chapters: {initial_chapters}")
        
        # Try to create a chapter via API (should create join request instead)
        chapter_data = {
            'club': test_club.id,
            'name': 'Test Join Request Chapter',
            'description': 'This should create a join request',
            'city': 'Test City',
            'state_new': state.id if state else None,
            'is_public': True,
            'accepts_new_members': True
        }
        
        response = client.post('/api/chapters/', 
                             data=json.dumps(chapter_data),
                             content_type='application/json')
        
        print(f"Chapter creation API response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        # Check if join request was created instead of chapter
        final_join_requests = ChapterJoinRequest.objects.filter(club=test_club).count()
        final_chapters = Chapter.objects.filter(club=test_club).count()
        
        print(f"Final join requests: {final_join_requests}")
        print(f"Final chapters: {final_chapters}")
        
        # Verify join request was created
        if final_join_requests > initial_join_requests:
            print("✅ Join request created instead of direct chapter")
            
            # Get the latest join request
            latest_request = ChapterJoinRequest.objects.filter(club=test_club).order_by('-created_at').first()
            print(f"   Join request: {latest_request.proposed_chapter_name}")
            print(f"   Status: {latest_request.status}")
            print(f"   Requested by: {latest_request.requested_by.username}")
            
            # Verify chapter was NOT created directly
            if final_chapters == initial_chapters:
                print("✅ Chapter was not created directly")
                
                # Test the approval process
                print("\nTesting join request approval...")
                approved_chapter = latest_request.approve("Test approval")
                print(f"✅ Chapter created after approval: {approved_chapter.name}")
                print(f"   Chapter owner: {approved_chapter.owner.username}")
                
                return True
            else:
                print("❌ Chapter was created directly (should not happen)")
                return False
        else:
            print("❌ Join request was not created")
            return False
        
    except Exception as e:
        print(f"❌ Error testing chapter creation flow: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_superuser_direct_creation():
    """Test that superusers can still create chapters directly"""
    print("\nTesting superuser direct chapter creation...")
    
    try:
        # Create or get superuser
        superuser, created = User.objects.get_or_create(
            username='testsuperuser',
            defaults={
                'email': 'super@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        
        if created:
            superuser.set_password('superpass123')
            superuser.save()
        
        # Get test club
        test_club = Club.objects.get(name="Test Join Request Club")
        state = State.objects.first()
        
        # Force login as superuser
        client = Client()
        client.force_login(superuser)
        print(f"Superuser logged in: {superuser.username}")
        
        # Count initial chapters
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        
        # Try to create a chapter via API (should create chapter directly)
        chapter_data = {
            'club': test_club.id,
            'name': 'Superuser Direct Chapter',
            'description': 'This should create a chapter directly',
            'city': 'Super City',
            'state_new': state.id if state else None,
            'is_public': True,
            'accepts_new_members': True
        }
        
        response = client.post('/api/chapters/', 
                             data=json.dumps(chapter_data),
                             content_type='application/json')
        
        print(f"Superuser chapter creation status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Superuser can create chapters directly")
            
            # Verify chapter was created
            final_chapters = Chapter.objects.filter(club=test_club).count()
            if final_chapters > initial_chapters:
                print("✅ Chapter was created directly by superuser")
                return True
            else:
                print("❌ Chapter was not created")
                return False
        else:
            print(f"❌ Superuser chapter creation failed: {response.content.decode()}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing superuser creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_chapter_creation_flow()
    success2 = test_superuser_direct_creation()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Chapter creation now properly uses join request flow.")
    else:
        print("\n❌ Some tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)

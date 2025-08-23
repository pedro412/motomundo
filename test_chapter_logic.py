#!/usr/bin/env python3
"""
Test script to verify chapter creation logic directly (without API)
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, ChapterJoinRequest, ClubAdmin
from clubs.api import ChapterViewSet
from clubs.serializers import ChapterSerializer
from geography.models import Country, State
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError

def test_chapter_creation_logic():
    """Test the chapter creation logic directly"""
    print("Testing chapter creation logic...")
    
    try:
        # Create test data
        mexico = Country.objects.get(name="Mexico")
        state = State.objects.filter(country=mexico).first()
        
        # Create a test club
        test_club, created = Club.objects.get_or_create(
            name="Test Logic Club",
            defaults={
                'description': 'Club for testing logic',
                'country_new': mexico,
                'primary_state_new': state,
                'club_type': 'mc',
                'is_public': True,
                'accepts_new_chapters': True
            }
        )
        
        # Create a test user (non-superuser)
        test_user, created = User.objects.get_or_create(
            username='testlogicuser',
            defaults={
                'email': 'logic@example.com',
                'first_name': 'Logic',
                'last_name': 'User'
            }
        )
        
        # Count initial data
        initial_join_requests = ChapterJoinRequest.objects.filter(club=test_club).count()
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        
        print(f"Initial join requests: {initial_join_requests}")
        print(f"Initial chapters: {initial_chapters}")
        
        # Create API request factory and request
        factory = APIRequestFactory()
        request = factory.post('/api/chapters/', {
            'club': test_club.id,
            'name': 'Test Logic Chapter',
            'description': 'Test chapter',
            'city': 'Logic City',
            'state_new': state.id if state else None,
        })
        request.user = test_user
        
        # Create viewset and test perform_create
        viewset = ChapterViewSet()
        viewset.request = request
        
        # Create serializer with data
        serializer = ChapterSerializer(data={
            'club': test_club.id,
            'name': 'Test Logic Chapter',
            'description': 'Test chapter',
            'city': 'Logic City',
            'state_new': state.id if state else None,
        })
        
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return False
        
        # Test the perform_create method
        try:
            viewset.perform_create(serializer)
            print("❌ perform_create should have raised ValidationError")
            return False
        except ValidationError as e:
            print(f"✅ ValidationError raised as expected: {e}")
            
            # Check if join request was created
            final_join_requests = ChapterJoinRequest.objects.filter(club=test_club).count()
            final_chapters = Chapter.objects.filter(club=test_club).count()
            
            print(f"Final join requests: {final_join_requests}")
            print(f"Final chapters: {final_chapters}")
            
            if final_join_requests > initial_join_requests:
                print("✅ Join request created")
                
                # Get the join request
                join_request = ChapterJoinRequest.objects.filter(club=test_club).order_by('-created_at').first()
                print(f"   Proposed name: {join_request.proposed_chapter_name}")
                print(f"   Requested by: {join_request.requested_by.username}")
                print(f"   Status: {join_request.status}")
                
                if final_chapters == initial_chapters:
                    print("✅ No direct chapter created")
                    return True
                else:
                    print("❌ Chapter was created directly")
                    return False
            else:
                print("❌ Join request was not created")
                return False
        
    except Exception as e:
        print(f"❌ Error testing chapter creation logic: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_superuser_logic():
    """Test superuser can create chapters directly"""
    print("\nTesting superuser logic...")
    
    try:
        # Get test club
        test_club = Club.objects.get(name="Test Logic Club")
        state = State.objects.first()
        
        # Create or get superuser
        superuser, created = User.objects.get_or_create(
            username='testlogicsuperuser',
            defaults={
                'email': 'logicsuper@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        
        # Count initial chapters
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        
        # Create API request
        factory = APIRequestFactory()
        request = factory.post('/api/chapters/', {
            'club': test_club.id,
            'name': 'Superuser Direct Chapter',
            'description': 'Direct creation',
            'city': 'Super City',
            'state_new': state.id if state else None,
        })
        request.user = superuser
        
        # Create viewset
        viewset = ChapterViewSet()
        viewset.request = request
        
        # Create serializer
        serializer = ChapterSerializer(data={
            'club': test_club.id,
            'name': 'Superuser Direct Chapter',
            'description': 'Direct creation',
            'city': 'Super City',
            'state_new': state.id if state else None,
        })
        
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return False
        
        # Test superuser perform_create
        try:
            viewset.perform_create(serializer)
            print("✅ Superuser perform_create succeeded")
            
            # Check if chapter was created
            final_chapters = Chapter.objects.filter(club=test_club).count()
            
            if final_chapters > initial_chapters:
                print("✅ Chapter created directly by superuser")
                
                # Get the chapter
                chapter = Chapter.objects.filter(club=test_club).order_by('-created_at').first()
                print(f"   Chapter name: {chapter.name}")
                print(f"   Owner: {chapter.owner.username if chapter.owner else 'None'}")
                
                return True
            else:
                print("❌ Chapter was not created")
                return False
                
        except Exception as e:
            print(f"❌ Superuser perform_create failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing superuser logic: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_chapter_creation_logic()
    success2 = test_superuser_logic()
    
    if success1 and success2:
        print("\n🎉 All logic tests passed! Chapter creation flow working correctly.")
    else:
        print("\n❌ Some logic tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)

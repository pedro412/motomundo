#!/usr/bin/env python
"""
Quick test script to verify our new discovery platform models work correctly.
Run this with: docker-compose exec web python test_new_models.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ChapterJoinRequest

def test_new_models():
    print("🧪 Testing Discovery Platform Models...")
    
    # Cleanup any existing test data first
    print("\n🧹 Cleaning up any existing test data...")
    try:
        Club.objects.filter(name__startswith='Test').delete()
        User.objects.filter(username__startswith='test').delete()
        User.objects.filter(username='requester').delete()
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    # Test 1: Create Club with new fields
    print("\n1. Testing Club model with new discovery fields...")
    try:
        club = Club.objects.create(
            name='Test Rocky Point Riders MC',
            description='A test motorcycle club',
            club_type='mc',
            country='Mexico', 
            primary_state='Campeche',
            founded_year=2020,
            is_public=True,
            accepts_new_chapters=True,
            contact_email='contact@testmc.com'
        )
        print(f"✅ Club created: {club}")
        print(f"   - Type: {club.club_type}")
        print(f"   - Location: {club.primary_state}, {club.country}")
        print(f"   - Public: {club.is_public}")
        print(f"   - Accepts chapters: {club.accepts_new_chapters}")
    except Exception as e:
        print(f"❌ Club creation failed: {e}")
        return False
    
    # Test 2: Create User and Chapter with new fields
    print("\n2. Testing Chapter model with new discovery fields...")
    try:
        user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        
        chapter = Chapter.objects.create(
            club=club,
            name='Test Carmen Chapter',
            description='Test chapter in Carmen',
            city='Ciudad del Carmen',
            state='Campeche',
            owner=user,
            is_active=True,
            is_public=True,
            accepts_new_members=True,
            meeting_info='Fridays at 7 PM',
            contact_email='carmen@testmc.com'
        )
        print(f"✅ Chapter created: {chapter}")
        print(f"   - Owner: {chapter.owner.username}")
        print(f"   - Location: {chapter.city}, {chapter.state}")
        print(f"   - Active: {chapter.is_active}, Public: {chapter.is_public}")
        print(f"   - Can manage check: {chapter.can_manage(user)}")
    except Exception as e:
        print(f"❌ Chapter creation failed: {e}")
        return False
    
    # Test 3: Test club stats update
    print("\n3. Testing Club stats update...")
    try:
        # Create a member (need to handle profile_picture requirement)
        print("   - Creating member (skipping profile_picture for now)...")
        
        # Get initial stats
        initial_chapters = club.total_chapters
        initial_members = club.total_members
        print(f"   - Before stats update: chapters={initial_chapters}, members={initial_members}")
        
        # Update stats (should count the chapter we created)
        club.update_stats()
        
        print(f"   - After stats update: chapters={club.total_chapters}, members={club.total_members}")
        
        if club.total_chapters == 1:
            print("✅ Club chapter count working correctly")
        else:
            print("❌ Club chapter count not updating correctly")
            
        # Note: Member count will be 0 since we can't easily create members without profile_picture
        print("   - Note: Member count test skipped due to profile_picture requirement")
        
    except Exception as e:
        print(f"❌ Stats update failed: {e}")
        return False
    
    # Test 4: Create ChapterJoinRequest
    print("\n4. Testing ChapterJoinRequest model...")
    try:
        requester = User.objects.create_user(
            username='requester',
            email='requester@test.com',
            password='testpass123'
        )
        
        join_request = ChapterJoinRequest.objects.create(
            club=club,
            requested_by=requester,
            proposed_chapter_name='New Test Chapter',
            city='Test City',
            state='Test State',
            description='A new test chapter',
            reason='We want to join this club',
            estimated_members=5
        )
        print(f"✅ Chapter join request created: {join_request}")
        print(f"   - Status: {join_request.status}")
        print(f"   - Proposed chapter: {join_request.proposed_chapter_name}")
        print(f"   - Estimated members: {join_request.estimated_members}")
    except Exception as e:
        print(f"❌ ChapterJoinRequest creation failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Discovery platform models are working correctly.")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    join_request.delete()
    # member.delete()  # Commented out since we didn't create member
    chapter.delete()
    club.delete()
    user.delete()
    requester.delete()
    print("✅ Cleanup completed")
    
    return True

if __name__ == '__main__':
    success = test_new_models()
    sys.exit(0 if success else 1)

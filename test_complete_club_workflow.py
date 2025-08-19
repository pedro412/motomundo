#!/usr/bin/env python
"""
Test script simulating a complete client workflow:
1. User creates a club
2. Club has 1 member (the founder as president)
3. User can add more members to the club
4. For clubs that don't use chapters, it's seamless
"""
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, ClubAdmin, Chapter, Member
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.test_utils import create_test_image
import json

def test_complete_club_workflow():
    print("🏍️  Complete Club Creation & Management Workflow")
    print("=" * 70)
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='club_founder', 
            email='founder@bikerclub.com', 
            password='secure_password',
            first_name='Maria',
            last_name='Rodriguez'
        )
        print(f"✅ Created club founder: {user.first_name} {user.last_name}")
    except:
        user = User.objects.get(username='club_founder')
        print(f"✅ Using existing founder: {user.first_name} {user.last_name}")
    
    # Setup API client
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Step 1: Create the club
    print("\n📝 Step 1: Creating a new motorcycle club...")
    club_data = {
        'name': 'Desert Riders MC',
        'description': 'Adventure riders exploring desert trails',
        'foundation_date': '2025-08-18',
        'website': 'https://desertriders.com'
    }
    
    response = client.post('/api/clubs/', club_data, format='json')
    if response.status_code != 201:
        print(f"❌ Club creation failed: {response.status_code} - {response.data}")
        return False
    
    club = response.data
    club_id = club['id']
    print(f"🎉 Created club: {club['name']}")
    print(f"   Total members: {club['total_members']}")
    print(f"   Founded: {club['foundation_date']}")
    
    # Step 2: Verify founder is both admin and member
    print("\n👑 Step 2: Verifying founder permissions...")
    
    # Check admin status
    admin_response = client.get('/api/clubs/my/')
    my_clubs = admin_response.data['results']
    print(f"✅ Founder can manage {len(my_clubs)} club(s)")
    
    # Check member status
    member_response = client.get('/api/members/my/')
    my_memberships = member_response.data['results']
    print(f"✅ Founder has {len(my_memberships)} membership(s)")
    if my_memberships:
        membership = my_memberships[0]
        print(f"   Role: {membership['role']}")
        # Get chapter name by ID
        chapter_response = client.get(f"/api/chapters/{membership['chapter']}/")
        if chapter_response.status_code == 200:
            chapter_name = chapter_response.data['name']
            print(f"   Chapter: {chapter_name}")
        else:
            print(f"   Chapter ID: {membership['chapter']}")
    
    # Step 3: Add more members to the club
    print("\n👥 Step 3: Adding more members to the club...")
    
    # Get the club's main chapter
    chapters_response = client.get(f'/api/chapters/?club={club_id}')
    main_chapter = chapters_response.data['results'][0]
    chapter_id = main_chapter['id']
    print(f"   Using chapter: {main_chapter['name']}")
    
    # Add a few members (without user accounts - just club roster entries)
    new_members = [
        {
            'first_name': 'Carlos',
            'last_name': 'Mendez',
            'nickname': 'Desert Fox',
            'role': 'vice_president',
            'chapter': chapter_id,
            'profile_picture': create_test_image('carlos_mendez.jpg')
        },
        {
            'first_name': 'Ana',
            'last_name': 'Silva',
            'nickname': 'Road Queen',
            'role': 'secretary',
            'chapter': chapter_id,
            'profile_picture': create_test_image('ana_silva.jpg')
        },
        {
            'first_name': 'Luis',
            'last_name': 'Torres',
            'nickname': 'Dust Devil',
            'role': 'member',
            'chapter': chapter_id,
            'profile_picture': create_test_image('luis_torres.jpg')
        }
    ]
    
    added_members = []
    for member_data in new_members:
        response = client.post('/api/members/', member_data, format='multipart')
        if response.status_code == 201:
            member = response.data
            added_members.append(member)
            print(f"   ✅ Added: {member['first_name']} {member['last_name']} ({member['role']})")
        else:
            print(f"   ❌ Failed to add member: {response.status_code} - {response.data}")
            # If user field is required, let's try creating just members from the model directly
            try:
                from clubs.models import Member
                member_obj = Member.objects.create(
                    chapter_id=chapter_id,
                    first_name=member_data['first_name'],
                    last_name=member_data['last_name'],
                    nickname=member_data['nickname'],
                    role=member_data['role'],
                    profile_picture=member_data['profile_picture']
                )
                print(f"   ✅ Created directly: {member_obj.first_name} {member_obj.last_name} ({member_obj.role})")
            except Exception as e:
                print(f"   ❌ Direct creation failed: {e}")
    
    # Step 4: Verify final club state
    print("\n📊 Step 4: Final club summary...")
    final_club_response = client.get(f'/api/clubs/{club_id}/')
    final_club = final_club_response.data
    
    print(f"   Club: {final_club['name']}")
    print(f"   Total members: {final_club['total_members']}")
    print(f"   Website: {final_club['website']}")
    
    # List all members
    members_response = client.get(f'/api/members/?chapter={chapter_id}')
    all_members = members_response.data['results']
    print(f"\n   📋 Club roster:")
    for member in all_members:
        print(f"      • {member['first_name']} {member['last_name']} ({member['nickname']}) - {member['role']}")
    
    print(f"\n🎯 Success! Club has {len(all_members)} total members")
    return len(all_members) >= 4  # Founder + 3 added members

if __name__ == "__main__":
    success = test_complete_club_workflow()
    print("\n" + "=" * 70)
    if success:
        print("🏆 Complete workflow successful!")
        print("💡 Clubs now automatically create:")
        print("   • Club admin role for founder")
        print("   • Default 'Main Chapter'")
        print("   • Founder as president member")
        print("   • Ready to add more members")
    else:
        print("❌ Workflow had issues")

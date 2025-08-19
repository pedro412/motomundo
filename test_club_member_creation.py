#!/usr/bin/env python
"""
Test script to verify that club creation now creates both admin and member entries.
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
import json

def test_club_creation_with_member():
    print("🧪 Testing Club Creation with Member Auto-Creation")
    print("=" * 60)
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='founder_user', 
            email='founder@example.com', 
            password='secure_password',
            first_name='John',
            last_name='Founder'
        )
        print(f"✅ Created test user: {user.username} ({user.first_name} {user.last_name})")
    except:
        user = User.objects.get(username='founder_user')
        print(f"✅ Using existing test user: {user.username}")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"✅ Generated JWT token")
    
    # Setup API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test club creation
    club_data = {
        'name': 'Founders Motorcycle Club',
        'description': 'A club that automatically creates founder as member',
        'foundation_date': '2025-08-18',
        'website': 'https://foundersmc.example.com'
    }
    
    print("\n📤 Creating club...")
    response = client.post('/api/clubs/', club_data, format='json')
    
    if response.status_code == 201:
        club_id = response.data['id']
        club = Club.objects.get(id=club_id)
        print(f"🎉 Club created: {club.name} (ID: {club_id})")
        
        # Check if user is club admin
        is_admin = ClubAdmin.objects.filter(user=user, club=club).exists()
        print(f"✅ User is club admin: {is_admin}")
        
        # Check if default chapter was created
        chapters = Chapter.objects.filter(club=club)
        print(f"✅ Chapters created: {chapters.count()}")
        if chapters.exists():
            main_chapter = chapters.first()
            print(f"   Chapter name: {main_chapter.name}")
        
        # Check if user is a member (president)
        members = Member.objects.filter(chapter__club=club, user=user)
        print(f"✅ User is member: {members.exists()}")
        
        if members.exists():
            member = members.first()
            print(f"   Member role: {member.role}")
            print(f"   Member name: {member.first_name} {member.last_name}")
            print(f"   Member nickname: {member.nickname}")
            print(f"   Chapter: {member.chapter.name}")
        
        # Check total members count
        total_members = Member.objects.filter(chapter__club=club).count()
        print(f"✅ Total club members: {total_members}")
        
        # Test API response shows correct member count
        club_response = client.get(f'/api/clubs/{club_id}/')
        if club_response.status_code == 200:
            api_member_count = club_response.data.get('total_members', 0)
            print(f"✅ API reports total members: {api_member_count}")
        
        return True
        
    else:
        print(f"❌ FAILED! Error: {response.status_code}")
        print(f"   Response: {json.dumps(response.data, indent=2)}")
        return False

if __name__ == "__main__":
    success = test_club_creation_with_member()
    print("\n" + "=" * 60)
    if success:
        print("🎉 Club creation now creates both admin and member entries!")
    else:
        print("❌ There's still an issue with automatic member creation")

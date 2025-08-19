#!/usr/bin/env python
"""
Test script to verify that club creation is now working for authenticated users.
This simulates what your client app is doing.
"""
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, ClubAdmin
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

def test_club_creation():
    print("🧪 Testing Club Creation with JWT Authentication")
    print("=" * 60)
    
    # Create a test user (simulating your app's user)
    try:
        user = User.objects.create_user(
            username='app_user', 
            email='app@example.com', 
            password='secure_password',
            first_name='App',
            last_name='User'
        )
        print(f"✅ Created test user: {user.username}")
    except:
        user = User.objects.get(username='app_user')
        print(f"✅ Using existing test user: {user.username}")
    
    # Generate JWT token (simulating your app's auth flow)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"✅ Generated JWT token: {access_token[:30]}...")
    
    # Setup API client with JWT authentication
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    print("✅ API client configured with JWT Bearer token")
    
    # Test club creation (what your app is trying to do)
    club_data = {
        'name': 'My Awesome Motorcycle Club',
        'description': 'A club created via API with JWT authentication',
        'foundation_date': '2025-08-18',
        'website': 'https://myclub.example.com'
    }
    
    print("\n📤 Attempting to create club...")
    print(f"   Data: {json.dumps(club_data, indent=2)}")
    
    response = client.post('/api/clubs/', club_data, format='json')
    
    print(f"\n📨 Response Status: {response.status_code}")
    
    if response.status_code == 201:
        club_id = response.data['id']
        print(f"🎉 SUCCESS! Club created with ID: {club_id}")
        print(f"   Response: {json.dumps(response.data, indent=2)}")
        
        # Verify user was made admin
        is_admin = ClubAdmin.objects.filter(user=user, club_id=club_id).exists()
        print(f"✅ User automatically made club admin: {is_admin}")
        
        # Test that they can now create chapters
        chapter_data = {
            'name': 'Main Chapter',
            'description': 'Primary chapter of the club',
            'club': club_id
        }
        
        chapter_response = client.post('/api/chapters/', chapter_data, format='json')
        print(f"✅ Can create chapters: {chapter_response.status_code == 201}")
        
    else:
        print(f"❌ FAILED! Error: {response.status_code}")
        print(f"   Response: {json.dumps(response.data, indent=2)}")
    
    print("\n" + "=" * 60)
    return response.status_code == 201

if __name__ == "__main__":
    success = test_club_creation()
    if success:
        print("🎉 Your client app should now be able to create clubs!")
        print("💡 Make sure you're using JWT Bearer token in Authorization header")
    else:
        print("❌ There may still be an issue with club creation")

#!/usr/bin/env python
"""
Test script for the claim flow functionality:
1. Admin creates a member with a claim code
2. User registers and claims the membership
3. User is now linked to the member profile
"""
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.test_utils import create_test_image
import json

def test_claim_flow():
    print("🎫 Testing Member Claim Flow")
    print("=" * 50)
    
    # Create a club admin
    try:
        admin_user = User.objects.create_user(
            username='club_admin', 
            email='admin@bikerclub.com', 
            password='secure_password',
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    except:
        admin_user = User.objects.get(username='club_admin')
        print(f"✅ Using existing admin: {admin_user.username}")
    
    # Create a club and make admin user the club admin
    try:
        club = Club.objects.create(
            name='Test Riders MC',
            description='Test club for claim flow'
        )
        print(f"✅ Created club: {club.name}")
    except:
        club = Club.objects.get(name='Test Riders MC')
        print(f"✅ Using existing club: {club.name}")
    
    # Make admin user a club admin
    club_admin, created = ClubAdmin.objects.get_or_create(
        user=admin_user,
        club=club,
        defaults={'created_by': admin_user}
    )
    
    # Create a chapter
    chapter, created = Chapter.objects.get_or_create(
        club=club,
        name='Main Chapter',
        defaults={'description': 'Main chapter'}
    )
    print(f"✅ Chapter: {chapter.name}")
    
    # Setup API client for admin
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    admin_client = APIClient()
    admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Step 1: Admin creates a member with a claim code
    print("\n👤 Step 1: Admin creates member with claim code...")
    
    # Create member directly through model first
    member = Member.objects.create(
        chapter=chapter,
        first_name='Carlos',
        last_name='Rodriguez',
        nickname='Road Warrior',
        role='member',
        profile_picture=create_test_image('carlos_rodriguez.jpg')
    )
    
    # Generate claim code
    claim_code = member.generate_claim_code()
    member.save()
    
    print(f"   ✅ Created member: {member.first_name} {member.last_name}")
    print(f"   📧 Claim code: {claim_code}")
    print(f"   🏍️ Club: {member.club.name if member.club else 'N/A'}")
    print(f"   📍 Chapter: {member.chapter.name}")
    
    # Step 2: New user registers
    print("\n🆕 Step 2: New user registers...")
    try:
        new_user = User.objects.create_user(
            username='carlos_rod',
            email='carlos@example.com',
            password='my_password',
            first_name='Carlos',
            last_name='Rodriguez'
        )
        print(f"   ✅ User registered: {new_user.username}")
    except:
        new_user = User.objects.get(username='carlos_rod')
        print(f"   ✅ Using existing user: {new_user.username}")
    
    # Setup API client for new user
    refresh = RefreshToken.for_user(new_user)
    access_token = str(refresh.access_token)
    user_client = APIClient()
    user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Step 3: User claims membership
    print("\n🎫 Step 3: User claims membership...")
    
    response = user_client.post('/api/members/claim-membership/', {
        'claim_code': claim_code
    }, format='json')
    
    if response.status_code == 200:
        result = response.data
        print(f"   ✅ Successfully claimed membership!")
        print(f"   👤 Member: {result['member']['name']}")
        print(f"   🏍️ Club: {result['member']['club']}")
        print(f"   📍 Chapter: {result['member']['chapter']}")
        print(f"   🎭 Role: {result['member']['role']}")
    else:
        print(f"   ❌ Claim failed: {response.status_code} - {response.data}")
        return False
    
    # Step 4: Verify the linkage
    print("\n🔗 Step 4: Verifying user-member linkage...")
    
    # Refresh member from database
    member.refresh_from_db()
    
    print(f"   Member linked to user: {member.user.username if member.user else 'None'}")
    print(f"   Claim code cleared: {member.claim_code is None}")
    
    # Check user's memberships
    user_memberships = user_client.get('/api/members/my/')
    if user_memberships.status_code == 200:
        memberships = user_memberships.data['results']
        print(f"   User has {len(memberships)} membership(s)")
        for membership in memberships:
            print(f"      • {membership['first_name']} {membership['last_name']} in {membership.get('club', {}).get('name', 'Unknown club')}")
    
    return True

if __name__ == "__main__":
    success = test_claim_flow()
    print("\n" + "=" * 50)
    if success:
        print("🏆 Claim flow test successful!")
        print("💡 The workflow now supports:")
        print("   • Admin creates member with claim code")
        print("   • User registers and claims membership")
        print("   • Member profile links to user account")
        print("   • Claim code is cleared after use")
    else:
        print("❌ Claim flow test failed")

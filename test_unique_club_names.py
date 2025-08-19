#!/usr/bin/env python
"""
Test script to verify club name uniqueness is working
"""
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

def test_unique_club_names():
    print("🏷️  Testing Club Name Uniqueness")
    print("=" * 50)
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='test_uniqueness',
            email='test@unique.com',
            password='test_pass',
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created test user: {user.username}")
    except:
        user = User.objects.get(username='test_uniqueness')
        print(f"✅ Using existing user: {user.username}")
    
    # Setup API client
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    # Test 1: Create first club
    print("\n📝 Test 1: Creating first club...")
    response1 = client.post('/api/clubs/', {
        'name': 'Unique Riders MC',
        'description': 'First club with this name',
        'foundation_date': '2025-01-01'
    }, format='json')
    
    if response1.status_code == 201:
        club1 = response1.data
        print(f"   ✅ Created club: {club1['name']} (ID: {club1['id']})")
    else:
        print(f"   ❌ Failed to create first club: {response1.status_code} - {response1.data}")
        return False
    
    # Test 2: Try to create club with same name
    print("\n📝 Test 2: Attempting to create club with same name...")
    response2 = client.post('/api/clubs/', {
        'name': 'Unique Riders MC',  # Same name
        'description': 'Second club with same name',
        'foundation_date': '2025-02-01'
    }, format='json')
    
    if response2.status_code == 400:
        error = response2.data
        print(f"   ✅ Correctly rejected duplicate name")
        print(f"   📝 Error message: {error.get('name', ['Unknown error'])[0]}")
    else:
        print(f"   ❌ Should have rejected duplicate name but got: {response2.status_code} - {response2.data}")
        return False
    
    # Test 3: Try with different case
    print("\n📝 Test 3: Attempting to create club with same name (different case)...")
    response3 = client.post('/api/clubs/', {
        'name': 'UNIQUE RIDERS MC',  # Same name, different case
        'description': 'Same name but uppercase',
        'foundation_date': '2025-03-01'
    }, format='json')
    
    if response3.status_code == 400:
        error = response3.data
        print(f"   ✅ Correctly rejected case variation")
        print(f"   📝 Error message: {error.get('name', ['Unknown error'])[0]}")
    else:
        print(f"   ❌ Should have rejected case variation but got: {response3.status_code} - {response3.data}")
        return False
    
    # Test 4: Create club with different name
    print("\n📝 Test 4: Creating club with different name...")
    response4 = client.post('/api/clubs/', {
        'name': 'Different Riders MC',
        'description': 'Club with different name',
        'foundation_date': '2025-04-01'
    }, format='json')
    
    if response4.status_code == 201:
        club2 = response4.data
        print(f"   ✅ Created club: {club2['name']} (ID: {club2['id']})")
    else:
        print(f"   ❌ Failed to create club with different name: {response4.status_code} - {response4.data}")
        return False
    
    # Test 5: Test updating existing club name to conflict
    print("\n📝 Test 5: Attempting to update club name to conflict...")
    response5 = client.patch(f"/api/clubs/{club2['id']}/", {
        'name': 'Unique Riders MC'  # Try to change to existing name
    }, format='json')
    
    if response5.status_code == 400:
        error = response5.data
        print(f"   ✅ Correctly rejected name conflict during update")
        print(f"   📝 Error message: {error.get('name', ['Unknown error'])[0]}")
    else:
        print(f"   ❌ Should have rejected name conflict but got: {response5.status_code} - {response5.data}")
        return False
    
    # Test 6: Test updating club with same name (should be allowed)
    print("\n📝 Test 6: Updating club with same name (should work)...")
    response6 = client.patch(f"/api/clubs/{club2['id']}/", {
        'name': 'Different Riders MC',  # Same name as current
        'description': 'Updated description'
    }, format='json')
    
    if response6.status_code == 200:
        updated_club = response6.data
        print(f"   ✅ Successfully updated club: {updated_club['name']}")
        print(f"   📝 New description: {updated_club['description']}")
    else:
        print(f"   ❌ Failed to update club with same name: {response6.status_code} - {response6.data}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_unique_club_names()
    print("\n" + "=" * 50)
    if success:
        print("🏆 Club name uniqueness test successful!")
        print("💡 Features verified:")
        print("   ✅ Club names must be unique")
        print("   ✅ Case-insensitive uniqueness checking")
        print("   ✅ Clear error messages for duplicates")
        print("   ✅ Updates with same name allowed")
        print("   ✅ Updates that would create duplicates rejected")
    else:
        print("❌ Club name uniqueness test failed")

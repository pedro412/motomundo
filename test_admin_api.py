#!/usr/bin/env python
"""
Test script for the discovery API with admin authentication
"""

import os
import django
import sys

# Add project root to path
sys.path.insert(0, '/Users/pedro412/motomundo')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.test import Client
from clubs.models import Club, Chapter, ChapterJoinRequest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import json

def test_admin_join_requests():
    """Test the join request management with admin authentication"""
    print("=" * 60)
    print("TESTING ADMIN JOIN REQUEST MANAGEMENT")
    print("=" * 60)
    
    try:
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('testpass123')
            admin_user.save()
            print(f"Created admin user: {admin_user.username}")
        
        # Create or get token for authentication
        token, created = Token.objects.get_or_create(user=admin_user)
        print(f"Using auth token: {token.key[:10]}...")
        
        # Create test client with authentication
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Create some test join requests if none exist
        club = Club.objects.filter(accepts_new_chapters=True).first()
        if not club:
            club = Club.objects.create(
                name="Test Discovery Club",
                description="A club for testing discovery features",
                country="United States",
                primary_state="California",
                is_public=True,
                accepts_new_chapters=True,
                club_type="SOCIAL"
            )
        
        test_user, _ = User.objects.get_or_create(
            username='test_requester',
            defaults={'email': 'requester@example.com'}
        )
        
        # Clean up old test requests
        ChapterJoinRequest.objects.filter(proposed_chapter_name__contains="API Test").delete()
        
        # Create test request
        import time
        unique_name = f"API Test Chapter {int(time.time())}"
        test_request = ChapterJoinRequest.objects.create(
            club=club,
            requested_by=test_user,
            proposed_chapter_name=unique_name,
            city="Test City",
            state="Test State",
            description="Test description",
            reason="Testing API",
            estimated_members=10
        )
        
        print(f"\n1. Testing join request list...")
        response = client.get('/clubs/api/discovery/join-requests/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('results', data)
            print(f"Found {len(requests_list)} join requests")
            if requests_list:
                first_request = requests_list[0]
                print(f"First request: {first_request.get('proposed_chapter_name')}")
                print(f"Status: {first_request.get('status')}")
                print(f"Club: {first_request.get('club_name')}")
        else:
            print(f"Error: {response.content.decode()}")
        
        print(f"\n2. Testing approve action...")
        approve_url = f'/clubs/api/discovery/join-requests/{test_request.id}/approve/'
        response = client.post(approve_url, {'admin_notes': 'Approved via API test'})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Request approved: {data.get('status')}")
            print(f"Admin notes: {data.get('admin_notes')}")
            print(f"Chapter created: {data.get('chapter_created', False)}")
        else:
            print(f"Error: {response.content.decode()}")
        
        # Create another request to test rejection
        reject_name = f"API Reject Test {int(time.time())}"
        reject_request = ChapterJoinRequest.objects.create(
            club=club,
            requested_by=test_user,
            proposed_chapter_name=reject_name,
            city="Reject City",
            state="Reject State",
            description="Test rejection",
            reason="Testing rejection API",
            estimated_members=5
        )
        
        print(f"\n3. Testing reject action...")
        reject_url = f'/clubs/api/discovery/join-requests/{reject_request.id}/reject/'
        response = client.post(reject_url, {'admin_notes': 'Rejected via API test'})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Request rejected: {data.get('status')}")
            print(f"Admin notes: {data.get('admin_notes')}")
        else:
            print(f"Error: {response.content.decode()}")
        
        print(f"\n4. Testing filtering by status...")
        response = client.get('/clubs/api/discovery/join-requests/?status=approved')
        if response.status_code == 200:
            data = response.json()
            approved_requests = data.get('results', data)
            print(f"Approved requests: {len(approved_requests)}")
        
        response = client.get('/clubs/api/discovery/join-requests/?status=rejected')
        if response.status_code == 200:
            data = response.json()
            rejected_requests = data.get('results', data)
            print(f"Rejected requests: {len(rejected_requests)}")
            
    except Exception as e:
        print(f"Error testing admin functionality: {e}")
        import traceback
        traceback.print_exc()

def test_public_api_comprehensive():
    """More comprehensive test of public API endpoints"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE PUBLIC API TESTING")
    print("=" * 60)
    
    client = APIClient()
    
    # Test club types
    print("\n1. Testing club type filtering...")
    for club_type in ['mc', 'association', 'organization', 'riding_group']:
        response = client.get(f'/clubs/api/discovery/clubs/?club_type={club_type}')
        if response.status_code == 200:
            data = response.json()
            clubs = data.get('results', data)
            print(f"  {club_type}: {len(clubs)} clubs")
        else:
            print(f"  {club_type}: Error - {response.status_code}")
    
    # Test pagination
    print("\n2. Testing pagination...")
    response = client.get('/clubs/api/discovery/clubs/?page_size=1')
    if response.status_code == 200:
        data = response.json()
        print(f"Page size 1: {len(data.get('results', []))} results")
        print(f"Has next: {data.get('next') is not None}")
        print(f"Total count: {data.get('count', 'N/A')}")
    
    # Test search
    print("\n3. Testing search...")
    response = client.get('/clubs/api/discovery/clubs/?search=test')
    if response.status_code == 200:
        data = response.json()
        clubs = data.get('results', data)
        print(f"Search 'test': {len(clubs)} clubs")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_admin_join_requests()
    test_public_api_comprehensive()

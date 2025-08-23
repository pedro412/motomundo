#!/usr/bin/env python
"""
Test script for the discovery API endpoints
This tests the new public discovery functionality
"""

import os
import django
import sys
import requests
import json

# Add project root to path
sys.path.insert(0, '/Users/pedro412/motomundo')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.test import Client
from clubs.models import Club, Chapter, ChapterJoinRequest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse

def test_discovery_api():
    """Test the discovery API endpoints"""
    print("=" * 60)
    print("TESTING DISCOVERY API ENDPOINTS")
    print("=" * 60)
    
    # Create test client
    client = APIClient()
    
    # 1. Test club discovery list
    print("\n1. Testing club discovery list...")
    try:
        response = client.get('/clubs/api/discovery/clubs/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Clubs found: {len(data['results']) if 'results' in data else len(data)}")
            if data.get('results') or data:
                clubs = data.get('results', data)
                if clubs:
                    first_club = clubs[0]
                    print(f"First club: {first_club.get('name', 'Unknown')}")
                    print(f"Description: {first_club.get('description', 'No description')[:100]}...")
        else:
            print(f"Error: {response.content.decode()}")
    except Exception as e:
        print(f"Error testing club list: {e}")
    
    # 2. Test club discovery by location
    print("\n2. Testing club discovery by location...")
    try:
        response = client.get('/clubs/api/discovery/clubs/by_location/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Location groups: {len(data)}")
            for location, clubs in list(data.items())[:3]:  # Show first 3
                print(f"  {location}: {len(clubs)} clubs")
        else:
            print(f"Error: {response.content.decode()}")
    except Exception as e:
        print(f"Error testing by location: {e}")
    
    # 3. Test platform statistics
    print("\n3. Testing platform statistics...")
    try:
        response = client.get('/clubs/api/discovery/clubs/stats/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total clubs: {data.get('total_clubs', 0)}")
            print(f"Total chapters: {data.get('total_chapters', 0)}")
            print(f"Total members: {data.get('total_members', 0)}")
            print(f"Countries represented: {len(data.get('countries', []))}")
            print(f"States represented: {len(data.get('states', []))}")
        else:
            print(f"Error: {response.content.decode()}")
    except Exception as e:
        print(f"Error testing stats: {e}")
    
    # 4. Test filtering by state
    print("\n4. Testing state filtering...")
    try:
        response = client.get('/clubs/api/discovery/clubs/?primary_state=California')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            clubs = data.get('results', data)
            ca_clubs = len(clubs) if isinstance(clubs, list) else 0
            print(f"California clubs: {ca_clubs}")
    except Exception as e:
        print(f"Error testing state filter: {e}")
    
    # 5. Test join requests endpoint (admin-only)
    print("\n5. Testing join requests endpoint...")
    try:
        response = client.get('/clubs/api/discovery/join-requests/')
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly requires authentication")
        elif response.status_code == 200:
            data = response.json()
            requests_count = len(data.get('results', data))
            print(f"Join requests: {requests_count}")
        else:
            print(f"Unexpected response: {response.content.decode()}")
    except Exception as e:
        print(f"Error testing join requests: {e}")
    
    print("\n" + "=" * 60)
    print("DISCOVERY API TEST COMPLETE")
    print("=" * 60)

def test_join_request_creation():
    """Test creating a chapter join request"""
    print("\n" + "=" * 60)
    print("TESTING JOIN REQUEST CREATION")
    print("=" * 60)
    
    try:
        # Clean up any existing test data first
        ChapterJoinRequest.objects.filter(proposed_chapter_name__contains="Test Chapter").delete()
        Chapter.objects.filter(name__contains="Test Chapter").delete()
        
        # Find a club that accepts new chapters
        club = Club.objects.filter(accepts_new_chapters=True).first()
        if not club:
            # Create one for testing
            club = Club.objects.create(
                name="Test Discovery Club",
                description="A club for testing discovery features",
                country="United States",
                primary_state="California",
                is_public=True,
                accepts_new_chapters=True,
                club_type="SOCIAL"
            )
            print(f"Created test club: {club.name}")
        
        # Create a test user for the request
        user, created = User.objects.get_or_create(
            username='test_chapter_creator',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Creator'
            }
        )
        if created:
            print(f"Created test user: {user.username}")
        
        # Use a unique name for testing
        import time
        unique_name = f"Test Chapter {int(time.time())}"
        
        # Create join request
        join_request = ChapterJoinRequest.objects.create(
            club=club,
            requested_by=user,
            proposed_chapter_name=unique_name,
            city="San Francisco",
            state="California",
            description="A chapter for motorcycle enthusiasts in the San Francisco Bay Area",
            reason="We have a strong motorcycle community in SF and would love to be part of your organization.",
            estimated_members=25
        )
        
        print(f"✓ Created join request: {join_request.proposed_chapter_name}")
        print(f"  Club: {join_request.club.name}")
        print(f"  Status: {join_request.status}")
        print(f"  Created: {join_request.created_at}")
        
        # Test the approve action
        created_chapter = join_request.approve()
        print(f"✓ Request approved, status: {join_request.status}")
        
        # Check if chapter was created
        if created_chapter:
            print(f"✓ Chapter created: {created_chapter.name}")
            print(f"  City: {created_chapter.city}, State: {created_chapter.state}")
            print(f"  Owner: {created_chapter.owner.username}")
            print(f"  Club: {created_chapter.club.name}")
        
        # Test reject functionality with a new request
        reject_request = ChapterJoinRequest.objects.create(
            club=club,
            requested_by=user,
            proposed_chapter_name=f"Rejected Chapter {int(time.time())}",
            city="Los Angeles",
            state="California",
            description="Another test chapter",
            reason="Testing rejection workflow",
            estimated_members=15
        )
        
        reject_request.reject("This is a test rejection")
        print(f"✓ Rejection test: {reject_request.status} - {reject_request.admin_notes}")
        
    except Exception as e:
        print(f"Error testing join request creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_discovery_api()
    test_join_request_creation()

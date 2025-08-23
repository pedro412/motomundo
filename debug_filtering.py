#!/usr/bin/env python
"""
Simple test to debug the club filtering issue
"""

import os
import django
import sys

sys.path.insert(0, '/Users/pedro412/motomundo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from rest_framework.test import APIClient
from clubs.models import Club

def test_club_filtering():
    client = APIClient()
    
    # First, check what clubs exist and their types
    print("Current clubs in database:")
    for club in Club.objects.filter(is_public=True):
        print(f"  {club.name}: type={club.club_type}, public={club.is_public}")
    
    print("\nTesting basic discovery endpoint...")
    response = client.get('/clubs/api/discovery/clubs/')
    print(f"Basic request status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.content.decode()}")
    else:
        data = response.json()
        clubs = data.get('results', data)
        print(f"Found {len(clubs)} clubs")
    
    print("\nTesting club type filter...")
    response = client.get('/clubs/api/discovery/clubs/?club_type=mc')
    print(f"MC filter status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.content.decode()}")
    else:
        data = response.json()
        clubs = data.get('results', data)
        print(f"MC clubs: {len(clubs)}")
        
    print("\nTesting non-existent club type...")
    response = client.get('/clubs/api/discovery/clubs/?club_type=association')
    print(f"Association filter status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.content.decode()}")
    else:
        data = response.json()
        clubs = data.get('results', data)
        print(f"Association clubs: {len(clubs)}")

if __name__ == '__main__':
    test_club_filtering()

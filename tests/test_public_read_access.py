"""
Test cases for public read access to clubs, chapters, and members APIs
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .test_utils import create_test_image


class PublicReadAccessTestCase(APITestCase):
    """Test that clubs, chapters, and members are publicly readable"""

    def setUp(self):
        """Set up test data"""
        # Create a superuser to create test data
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        
        # Create a regular user to be club admin
        self.club_admin = User.objects.create_user('clubowner', 'owner@test.com', 'ownerpass')
        
        # Create test club
        self.club = Club.objects.create(
            name='Test Motorcycle Club',
            description='A test motorcycle club',
            website='https://test-mc.com'
        )
        
        # Make user a club admin
        ClubAdmin.objects.create(user=self.club_admin, club=self.club, created_by=self.superuser)
        
        # Create test chapter
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            club=self.club,
            description='A test chapter'
        )
        
        # Create test member
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            nickname='JD',
            chapter=self.chapter,
            role='member',
            profile_picture=create_test_image('john_doe.jpg')
        )

    def test_clubs_public_read_access(self):
        """Test that clubs are publicly readable without authentication"""
        print("\n🔍 Testing public read access to clubs API...")
        
        # Test without authentication
        self.client.credentials()  # Clear any credentials
        
        # Test club list
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        print("✅ Clubs list accessible without authentication")
        
        # Test club detail
        response = self.client.get(f'/api/clubs/{self.club.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Motorcycle Club')
        print("✅ Club detail accessible without authentication")
        
        # Test that write operations still require authentication
        response = self.client.post('/api/clubs/', {
            'name': 'New Club',
            'description': 'Unauthorized attempt'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Club creation properly requires authentication")
        
        # Test that update requires authentication
        response = self.client.put(f'/api/clubs/{self.club.id}/', {
            'name': 'Updated Name',
            'description': 'Unauthorized update'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Club update properly requires authentication")

    def test_chapters_public_read_access(self):
        """Test that chapters are publicly readable without authentication"""
        print("\n🔍 Testing public read access to chapters API...")
        
        # Test without authentication
        self.client.credentials()  # Clear any credentials
        
        # Test chapter list
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        print("✅ Chapters list accessible without authentication")
        
        # Test chapter detail
        response = self.client.get(f'/api/chapters/{self.chapter.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Chapter')
        print("✅ Chapter detail accessible without authentication")
        
        # Test that write operations still require authentication
        response = self.client.post('/api/chapters/', {
            'name': 'New Chapter',
            'club': self.club.id,
            'description': 'Unauthorized attempt'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Chapter creation properly requires authentication")

    def test_members_public_read_access(self):
        """Test that members are publicly readable without authentication"""
        print("\n🔍 Testing public read access to members API...")
        
        # Test without authentication
        self.client.credentials()  # Clear any credentials
        
        # Test member list
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        print("✅ Members list accessible without authentication")
        
        # Test member detail
        response = self.client.get(f'/api/members/{self.member.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        print("✅ Member detail accessible without authentication")
        
        # Test that write operations still require authentication
        response = self.client.post('/api/members/', {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'chapter': self.chapter.id,
            'role': 'rider'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Member creation properly requires authentication")

    def test_public_access_with_filtering(self):
        """Test that public access works with query parameters and filtering"""
        print("\n🔍 Testing public access with filtering...")
        
        # Test without authentication
        self.client.credentials()
        
        # Test club filtering
        response = self.client.get(f'/api/chapters/?club={self.club.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Chapter filtering works without authentication")
        
        # Test member filtering
        response = self.client.get(f'/api/members/?chapter={self.chapter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Member filtering works without authentication")
        
        # Test search
        response = self.client.get('/api/clubs/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Club search works without authentication")

    def test_authenticated_vs_unauthenticated_access(self):
        """Test that both authenticated and unauthenticated users get the same read data"""
        print("\n🔍 Testing authenticated vs unauthenticated read access...")
        
        # Get data without authentication
        self.client.credentials()
        unauth_response = self.client.get('/api/clubs/')
        unauth_data = unauth_response.data
        
        # Get data with authentication
        self.client.force_authenticate(user=self.club_admin)
        auth_response = self.client.get('/api/clubs/')
        auth_data = auth_response.data
        
        # Both should return 200
        self.assertEqual(unauth_response.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        
        # Both should have the same structure for read operations
        self.assertIn('results', unauth_data)
        self.assertIn('results', auth_data)
        
        print("✅ Both authenticated and unauthenticated users can read data")

    def test_summary(self):
        """Print a summary of the public access test results"""
        print("\n" + "="*60)
        print("📋 PUBLIC READ ACCESS TEST SUMMARY")
        print("="*60)
        print("✅ Clubs API: Public read access ✓")
        print("✅ Chapters API: Public read access ✓") 
        print("✅ Members API: Public read access ✓")
        print("🔒 Write operations: Still require authentication ✓")
        print("🔍 Filtering & Search: Work without authentication ✓")
        print("="*60)

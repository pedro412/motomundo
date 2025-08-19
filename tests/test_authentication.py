"""
Authentication Tests for Motomundo
Tests JWT and Token authentication endpoints and workflows
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .test_utils import create_test_image
import json


class AuthenticationTestCase(APITestCase):
    """Test authentication endpoints and workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.maxDiff = None
        
    def test_token_authentication_workflow(self):
        """Test complete Token authentication workflow"""
        print("\n=== TOKEN AUTHENTICATION WORKFLOW ===")
        
        # Register user
        registration_data = {
            'username': 'token_user',
            'email': 'token@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'Token',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/register/', registration_data, format='json')
        print(f"Registration status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        self.assertIn('token', response_data)
        token = response_data['token']
        print(f"✓ Token received: {token[:20]}...")
        
        # Test authenticated request
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✓ Authenticated request successful")
        
    def test_jwt_authentication_workflow(self):
        """Test complete JWT authentication workflow"""
        print("\n=== JWT AUTHENTICATION WORKFLOW ===")
        
        # Register user with JWT
        registration_data = {
            'username': 'jwt_user',
            'email': 'jwt@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'JWT',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/jwt/register/', registration_data, format='json')
        print(f"JWT Registration status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
        access_token = response_data['access']
        refresh_token = response_data['refresh']
        print(f"✓ JWT tokens received: {access_token[:20]}...")
        
        # Test authenticated request with JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✓ JWT authenticated request successful")
        
        # Test token refresh
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/jwt/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        new_access = response.json()['access']
        self.assertNotEqual(access_token, new_access)
        print("✓ Token refresh successful")
        
    def test_login_workflow(self):
        """Test login with existing user"""
        print("\n=== LOGIN WORKFLOW ===")
        
        # Create user first
        user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='securepass123'
        )
        
        # Test JWT login
        login_data = {
            'username': 'loginuser',
            'password': 'securepass123'
        }
        
        response = self.client.post('/api/auth/jwt/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
        print("✓ JWT login successful")
        
    def test_authentication_errors(self):
        """Test authentication error scenarios"""
        print("\n=== AUTHENTICATION ERROR SCENARIOS ===")
        
        # Test registration with mismatched passwords
        bad_registration = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password': 'pass123',
            'password_confirm': 'different123',
            'first_name': 'Bad',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/register/', bad_registration, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Password mismatch properly rejected")
        
        # Test login with wrong credentials
        wrong_login = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = self.client.post('/api/auth/jwt/login/', wrong_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✓ Wrong credentials properly rejected")
        
        # Test unauthenticated request
        self.client.credentials()  # Clear credentials
        response = self.client.post('/api/clubs/', {'name': 'Test Club'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✓ Unauthenticated request properly rejected")


class PermissionIntegrationTestCase(APITestCase):
    """Test authentication with permissions in realistic scenarios"""
    
    def setUp(self):
        """Create test data with proper permissions"""
        # Create users
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.club_admin = User.objects.create_user('clubadmin', 'clubadmin@test.com', 'pass')
        self.chapter_admin = User.objects.create_user('chapteradmin', 'chapteradmin@test.com', 'pass')
        self.regular_user = User.objects.create_user('regular', 'regular@test.com', 'pass')
        
        # Create club structure
        self.club = Club.objects.create(name='Test MC', description='Test motorcycle club')
        self.chapter = Chapter.objects.create(name='Test Chapter', club=self.club)
        
        # Assign permissions
        ClubAdmin.objects.create(user=self.club_admin, club=self.club, created_by=self.superuser)
        ChapterAdmin.objects.create(user=self.chapter_admin, chapter=self.chapter, created_by=self.club_admin)
        
    def test_permission_hierarchy_with_jwt(self):
        """Test permission hierarchy works with JWT authentication"""
        print("\n=== PERMISSION HIERARCHY WITH JWT ===")
        
        # Test club admin can create chapters
        login_data = {'username': 'clubadmin', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        chapter_data = {'name': 'New Chapter', 'club': self.club.id}
        response = self.client.post('/api/chapters/', chapter_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✓ Club admin can create chapters")
        
        # Test chapter admin can create members
        login_data = {'username': 'chapteradmin', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Create member data with file upload
        member_data = {
            'first_name': 'Test',
            'last_name': 'Member', 
            'chapter': self.chapter.id,
            'role': 'member',
            'nickname': 'TestRider',
            'user': '',
            'profile_picture': create_test_image('test_member_api.jpg')
        }
        response = self.client.post('/api/members/', member_data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Member creation failed with status {response.status_code}")
            print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✓ Chapter admin can create members")
        
        # Test regular user can now create clubs (and becomes admin automatically)
        login_data = {'username': 'regular', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        club_data = {'name': 'New User Club', 'description': 'Regular user can create clubs now'}
        response = self.client.post('/api/clubs/', club_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✓ Regular user can create clubs (becomes admin automatically)")

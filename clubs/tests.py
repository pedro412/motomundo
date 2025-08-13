from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterManager
from clubs.permissions import (
    get_user_manageable_clubs,
    get_user_manageable_chapters,
    get_user_manageable_members,
    user_can_manage_club,
    user_can_manage_chapter
)


class PermissionModelTests(TestCase):
    """Test the permission models"""
    
    def setUp(self):
        # Create test users
        self.superuser = User.objects.create_user(
            username='superuser',
            password='testpass',
            is_superuser=True
        )
        self.club_admin_user = User.objects.create_user(
            username='club_admin',
            password='testpass'
        )
        self.chapter_manager_user = User.objects.create_user(
            username='chapter_manager',
            password='testpass'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass'
        )
        
        # Create test clubs
        self.harley_club = Club.objects.create(
            name='Harley Riders United',
            description='Harley riders'
        )
        self.bmw_club = Club.objects.create(
            name='BMW Club',
            description='BMW riders'
        )
        
        # Create test chapters
        self.sf_chapter = Chapter.objects.create(
            club=self.harley_club,
            name='SF Chapter',
            description='San Francisco chapter'
        )
        self.la_chapter = Chapter.objects.create(
            club=self.harley_club,
            name='LA Chapter',
            description='Los Angeles chapter'
        )
        self.bmw_chapter = Chapter.objects.create(
            club=self.bmw_club,
            name='BMW SF Chapter',
            description='BMW San Francisco chapter'
        )
        
        # Create test members
        self.sf_member1 = Member.objects.create(
            chapter=self.sf_chapter,
            first_name='Alice',
            last_name='Johnson',
            role='president'
        )
        self.sf_member2 = Member.objects.create(
            chapter=self.sf_chapter,
            first_name='Bob',
            last_name='Wilson',
            role='rider'
        )
        self.la_member = Member.objects.create(
            chapter=self.la_chapter,
            first_name='Charlie',
            last_name='Brown',
            role='secretary'
        )
        self.bmw_member = Member.objects.create(
            chapter=self.bmw_chapter,
            first_name='Diana',
            last_name='Davis',
            role='president'
        )

    def test_club_admin_creation(self):
        """Test creating club admin"""
        club_admin = ClubAdmin.objects.create(
            user=self.club_admin_user,
            club=self.harley_club,
            created_by=self.superuser
        )
        self.assertEqual(club_admin.user, self.club_admin_user)
        self.assertEqual(club_admin.club, self.harley_club)
        self.assertEqual(club_admin.created_by, self.superuser)

    def test_club_admin_unique_constraint(self):
        """Test that user can't be admin of same club twice"""
        ClubAdmin.objects.create(
            user=self.club_admin_user,
            club=self.harley_club
        )
        with self.assertRaises(Exception):  # IntegrityError
            ClubAdmin.objects.create(
                user=self.club_admin_user,
                club=self.harley_club
            )

    def test_chapter_manager_creation(self):
        """Test creating chapter manager"""
        chapter_manager = ChapterManager.objects.create(
            user=self.chapter_manager_user,
            chapter=self.sf_chapter,
            created_by=self.superuser
        )
        self.assertEqual(chapter_manager.user, self.chapter_manager_user)
        self.assertEqual(chapter_manager.chapter, self.sf_chapter)


class PermissionLogicTests(TestCase):
    """Test the permission logic functions"""
    
    def setUp(self):
        # Create test data
        self.superuser = User.objects.create_user(
            username='superuser',
            password='testpass',
            is_superuser=True
        )
        self.club_admin_user = User.objects.create_user(
            username='club_admin',
            password='testpass'
        )
        self.chapter_manager_user = User.objects.create_user(
            username='chapter_manager',
            password='testpass'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass'
        )
        
        self.harley_club = Club.objects.create(name='Harley Club')
        self.bmw_club = Club.objects.create(name='BMW Club')
        
        self.sf_chapter = Chapter.objects.create(
            club=self.harley_club,
            name='SF Chapter'
        )
        self.la_chapter = Chapter.objects.create(
            club=self.harley_club,
            name='LA Chapter'
        )
        self.bmw_chapter = Chapter.objects.create(
            club=self.bmw_club,
            name='BMW Chapter'
        )
        
        # Create members
        self.sf_member = Member.objects.create(
            chapter=self.sf_chapter,
            first_name='Alice',
            last_name='Johnson',
            role='president'
        )
        self.la_member = Member.objects.create(
            chapter=self.la_chapter,
            first_name='Bob',
            last_name='Wilson',
            role='rider'
        )
        self.bmw_member = Member.objects.create(
            chapter=self.bmw_chapter,
            first_name='Charlie',
            last_name='Brown',
            role='president'
        )
        
        # Assign permissions
        self.club_admin = ClubAdmin.objects.create(
            user=self.club_admin_user,
            club=self.harley_club
        )
        self.chapter_manager = ChapterManager.objects.create(
            user=self.chapter_manager_user,
            chapter=self.sf_chapter
        )

    def test_superuser_permissions(self):
        """Superuser should see everything"""
        clubs = get_user_manageable_clubs(self.superuser)
        chapters = get_user_manageable_chapters(self.superuser)
        members = get_user_manageable_members(self.superuser)
        
        self.assertEqual(clubs.count(), 2)  # All clubs
        self.assertEqual(chapters.count(), 3)  # All chapters
        self.assertEqual(members.count(), 3)  # All members

    def test_club_admin_permissions(self):
        """Club admin should see only their club's data"""
        clubs = get_user_manageable_clubs(self.club_admin_user)
        chapters = get_user_manageable_chapters(self.club_admin_user)
        members = get_user_manageable_members(self.club_admin_user)
        
        self.assertEqual(clubs.count(), 1)  # Only Harley club
        self.assertEqual(clubs.first(), self.harley_club)
        
        self.assertEqual(chapters.count(), 2)  # SF and LA chapters
        chapter_names = list(chapters.values_list('name', flat=True))
        self.assertIn('SF Chapter', chapter_names)
        self.assertIn('LA Chapter', chapter_names)
        
        self.assertEqual(members.count(), 2)  # SF and LA members
        member_names = list(members.values_list('first_name', flat=True))
        self.assertIn('Alice', member_names)
        self.assertIn('Bob', member_names)
        self.assertNotIn('Charlie', member_names)  # BMW member

    def test_chapter_manager_permissions(self):
        """Chapter manager should see only their chapter's data"""
        clubs = get_user_manageable_clubs(self.chapter_manager_user)
        chapters = get_user_manageable_chapters(self.chapter_manager_user)
        members = get_user_manageable_members(self.chapter_manager_user)
        
        self.assertEqual(clubs.count(), 0)  # No clubs directly
        
        self.assertEqual(chapters.count(), 1)  # Only SF chapter
        self.assertEqual(chapters.first(), self.sf_chapter)
        
        self.assertEqual(members.count(), 1)  # Only SF member
        self.assertEqual(members.first(), self.sf_member)

    def test_regular_user_permissions(self):
        """Regular user should see no manageable data"""
        clubs = get_user_manageable_clubs(self.regular_user)
        chapters = get_user_manageable_chapters(self.regular_user)
        members = get_user_manageable_members(self.regular_user)
        
        self.assertEqual(clubs.count(), 0)
        self.assertEqual(chapters.count(), 0)
        self.assertEqual(members.count(), 0)

    def test_user_can_manage_club_function(self):
        """Test user_can_manage_club function"""
        self.assertTrue(user_can_manage_club(self.superuser, self.harley_club))
        self.assertTrue(user_can_manage_club(self.superuser, self.bmw_club))
        
        self.assertTrue(user_can_manage_club(self.club_admin_user, self.harley_club))
        self.assertFalse(user_can_manage_club(self.club_admin_user, self.bmw_club))
        
        self.assertFalse(user_can_manage_club(self.chapter_manager_user, self.harley_club))
        self.assertFalse(user_can_manage_club(self.regular_user, self.harley_club))

    def test_user_can_manage_chapter_function(self):
        """Test user_can_manage_chapter function"""
        self.assertTrue(user_can_manage_chapter(self.superuser, self.sf_chapter))
        self.assertTrue(user_can_manage_chapter(self.superuser, self.bmw_chapter))
        
        self.assertTrue(user_can_manage_chapter(self.club_admin_user, self.sf_chapter))
        self.assertTrue(user_can_manage_chapter(self.club_admin_user, self.la_chapter))
        self.assertFalse(user_can_manage_chapter(self.club_admin_user, self.bmw_chapter))
        
        self.assertTrue(user_can_manage_chapter(self.chapter_manager_user, self.sf_chapter))
        self.assertFalse(user_can_manage_chapter(self.chapter_manager_user, self.la_chapter))
        
        self.assertFalse(user_can_manage_chapter(self.regular_user, self.sf_chapter))


class PermissionAPITests(APITestCase):
    """Test API permissions"""
    
    def setUp(self):
        # Create test data using fixture
        from django.core.management import call_command
        call_command('loaddata', 'test_data.json')
        
        # Get users
        self.superuser = User.objects.get(username='admin')
        self.harley_admin = User.objects.get(username='harley_admin')
        self.sf_manager = User.objects.get(username='sf_manager')
        self.bmw_admin = User.objects.get(username='bmw_admin')
        
        # Get clubs and chapters for testing
        self.harley_club = Club.objects.get(name='Harley Riders United')
        self.bmw_club = Club.objects.get(name='BMW Motorrad Club')
        self.sf_chapter = Chapter.objects.get(name='San Francisco Chapter')

    def test_unauthenticated_access(self):
        """Unauthenticated users should not have access"""
        response = self.client.get('/api/clubs/')
        # Either 401 (Unauthorized) or 403 (Forbidden) is acceptable
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_superuser_api_access(self):
        """Superuser should see all data via API"""
        self.client.force_authenticate(user=self.superuser)
        
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All clubs
        
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # All chapters

    def test_club_admin_api_access(self):
        """Club admin should see only their club's data via API"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Harley club
        self.assertEqual(response.data['results'][0]['name'], 'Harley Riders United')
        
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only Harley chapters

    def test_chapter_manager_api_access(self):
        """Chapter manager should see only their chapter's data via API"""
        self.client.force_authenticate(user=self.sf_manager)
        
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # No clubs directly
        
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only SF chapter
        
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only SF members

    def test_club_admin_can_create_chapter(self):
        """Club admin should be able to create chapters for their club"""
        self.client.force_authenticate(user=self.harley_admin)
        
        data = {
            'club': self.harley_club.id,
            'name': 'Sacramento Chapter',
            'description': 'Sacramento area riders'
        }
        response = self.client.post('/api/chapters/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_club_admin_cannot_create_chapter_for_other_club(self):
        """Club admin should not be able to create chapters for other clubs"""
        self.client.force_authenticate(user=self.harley_admin)
        
        data = {
            'club': self.bmw_club.id,
            'name': 'Test Chapter',
            'description': 'Test'
        }
        response = self.client.post('/api/chapters/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_chapter_manager_can_create_member(self):
        """Chapter manager should be able to create members for their chapter"""
        self.client.force_authenticate(user=self.sf_manager)
        
        data = {
            'chapter': self.sf_chapter.id,
            'first_name': 'New',
            'last_name': 'Member',
            'role': 'rider'
        }
        response = self.client.post('/api/members/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_chapter_manager_cannot_create_member_for_other_chapter(self):
        """Chapter manager should not be able to create members for other chapters"""
        self.client.force_authenticate(user=self.sf_manager)
        
        bmw_chapter = Chapter.objects.get(name='Northern California Chapter')
        data = {
            'chapter': bmw_chapter.id,
            'first_name': 'New',
            'last_name': 'Member',
            'role': 'rider'
        }
        response = self.client.post('/api/members/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_management_endpoints(self):
        """Test permission management endpoints"""
        self.client.force_authenticate(user=self.superuser)
        
        # Only superuser should access club-admins endpoint
        response = self.client.get('/api/club-admins/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Club admin should access chapter-managers endpoint
        self.client.force_authenticate(user=self.harley_admin)
        response = self.client.get('/api/chapter-managers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MemberModelTests(TestCase):
    """Test member model validation"""
    
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.chapter = Chapter.objects.create(club=self.club, name='Test Chapter')

    def test_member_unique_name_in_chapter(self):
        """Test that member names must be unique within a chapter (case-insensitive)"""
        Member.objects.create(
            chapter=self.chapter,
            first_name='John',
            last_name='Doe',
            role='rider'
        )
        
        # Should not allow same name
        with self.assertRaises(ValidationError):
            member = Member(
                chapter=self.chapter,
                first_name='john',  # Different case
                last_name='doe',
                role='president'
            )
            member.full_clean()

    def test_member_same_name_different_chapters(self):
        """Test that same name is allowed in different chapters"""
        chapter2 = Chapter.objects.create(club=self.club, name='Test Chapter 2')
        
        Member.objects.create(
            chapter=self.chapter,
            first_name='John',
            last_name='Doe',
            role='rider'
        )
        
        # Should allow same name in different chapter
        member2 = Member(
            chapter=chapter2,
            first_name='John',
            last_name='Doe',
            role='rider'
        )
        member2.full_clean()  # Should not raise ValidationError
        member2.save()
        
        self.assertEqual(Member.objects.filter(first_name='John', last_name='Doe').count(), 2)


class AuthenticationTests(APITestCase):
    """Test user authentication and registration"""
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

    def test_registration_password_mismatch(self):
        """Test registration fails with password mismatch"""
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'differentpass123',
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create first user
        User.objects.create_user(username='existing', email='existing@example.com', password='pass123')
        
        url = '/api/auth/register/'
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create first user
        User.objects.create_user(username='existing', email='existing@example.com', password='pass123')
        
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login(self):
        """Test user login endpoint"""
        # Create user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        
        url = '/api/auth/login/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        url = '/api/auth/login/'
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_access(self):
        """Test authenticated user can access profile"""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        
        url = '/api/auth/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_profile_unauthenticated(self):
        """Test unauthenticated user cannot access profile"""
        url = '/api/auth/profile/'
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_permissions_endpoint(self):
        """Test user permissions endpoint"""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        
        url = '/api/auth/permissions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('roles', response.data)
        self.assertIn('permissions', response.data)
        self.assertEqual(response.data['is_superuser'], False)

    def test_change_password(self):
        """Test password change endpoint"""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='oldpass123')
        self.client.force_authenticate(user=user)
        
        url = '/api/auth/change-password/'
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        # Verify password was changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpass123'))

    def test_logout(self):
        """Test logout endpoint"""
        from rest_framework.authtoken.models import Token
        
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        token = Token.objects.create(user=user)
        self.client.force_authenticate(user=user, token=token)
        
        url = '/api/auth/logout/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify token was deleted
        self.assertFalse(Token.objects.filter(user=user).exists())

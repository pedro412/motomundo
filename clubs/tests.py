from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin, ChapterJoinRequest
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
        chapter_admin = ChapterAdmin.objects.create(
            user=self.chapter_manager_user,
            chapter=self.sf_chapter,
            created_by=self.superuser
        )
        self.assertEqual(chapter_admin.user, self.chapter_manager_user)
        self.assertEqual(chapter_admin.chapter, self.sf_chapter)


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
        self.chapter_admin = ChapterAdmin.objects.create(
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
        """Unauthenticated users should have read access but no write access"""
        # Test read access - should work
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test write access - should be denied
        response = self.client.post('/api/clubs/', {'name': 'Test Club'})
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
        """Club admin can see all clubs (public read) but write only to their clubs"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All clubs (public read)
        
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # All chapters (public read)

    def test_chapter_manager_api_access(self):
        """Chapter manager can see all data (public read) but write only to their chapters"""
        self.client.force_authenticate(user=self.sf_manager)
        
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All clubs (public read)
        
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # All chapters (public read)
        
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 2)  # All members (public read)

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
        
        # Get an existing user from the fixture
        from django.contrib.auth.models import User
        test_user = User.objects.filter(username='harley_admin').first()
        
        data = {
            'chapter': self.sf_chapter.id,
            'first_name': 'New',
            'last_name': 'Member',
            'role': 'rider',
            'user': test_user.id if test_user else None
        }
        response = self.client.post('/api/members/', data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.status_code} - {response.data}")
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
        
        # Club admin should access chapter-admins endpoint
        self.client.force_authenticate(user=self.harley_admin)
        response = self.client.get('/api/chapter-admins/')
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
        self.assertEqual(response.data['roles']['is_superuser'], False)

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


class DiscoveryPlatformModelTests(TestCase):
    """Test new discovery platform model fields and functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test club with new discovery fields
        self.club = Club.objects.create(
            name='Test Motorcycle Club',
            description='A test motorcycle club',
            club_type='mc',
            country='Mexico',
            primary_state='Campeche',
            founded_year=2020,
            is_public=True,
            accepts_new_chapters=True,
            contact_email='contact@testmc.com'
        )
        
        # Create test chapter with new discovery fields
        self.chapter = Chapter.objects.create(
            club=self.club,
            name='Test Chapter',
            description='A test chapter',
            city='Ciudad del Carmen',
            state='Campeche',
            owner=self.user,
            is_active=True,
            is_public=True,
            accepts_new_members=True,
            meeting_info='Weekly meetings on Fridays at 7 PM',
            contact_email='chapter@testmc.com'
        )

    def test_club_discovery_fields(self):
        """Test club discovery fields are properly set"""
        self.assertEqual(self.club.club_type, 'mc')
        self.assertEqual(self.club.country, 'Mexico')
        self.assertEqual(self.club.primary_state, 'Campeche')
        self.assertEqual(self.club.founded_year, 2020)
        self.assertTrue(self.club.is_public)
        self.assertTrue(self.club.accepts_new_chapters)
        self.assertEqual(self.club.contact_email, 'contact@testmc.com')

    def test_club_type_choices(self):
        """Test club type choices validation"""
        valid_types = ['mc', 'association', 'organization', 'riding_group']
        
        for club_type in valid_types:
            club = Club(
                name=f'Test {club_type} Club',
                club_type=club_type
            )
            club.full_clean()  # Should not raise ValidationError

    def test_club_stats_initialization(self):
        """Test club stats are initialized to 0"""
        new_club = Club.objects.create(name='New Club')
        self.assertEqual(new_club.total_members, 0)
        self.assertEqual(new_club.total_chapters, 0)

    def test_chapter_discovery_fields(self):
        """Test chapter discovery fields are properly set"""
        self.assertEqual(self.chapter.city, 'Ciudad del Carmen')
        self.assertEqual(self.chapter.state, 'Campeche')
        self.assertEqual(self.chapter.owner, self.user)
        self.assertTrue(self.chapter.is_active)
        self.assertTrue(self.chapter.is_public)
        self.assertTrue(self.chapter.accepts_new_members)
        self.assertEqual(self.chapter.meeting_info, 'Weekly meetings on Fridays at 7 PM')
        self.assertEqual(self.chapter.contact_email, 'chapter@testmc.com')

    def test_chapter_can_manage_method(self):
        """Test chapter can_manage method"""
        self.assertTrue(self.chapter.can_manage(self.user))
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.assertFalse(self.chapter.can_manage(other_user))

    def test_club_update_stats_method(self):
        """Test club update_stats method"""
        # Initially should be 0
        self.assertEqual(self.club.total_chapters, 0)
        self.assertEqual(self.club.total_members, 0)
        
        # Create a member
        Member.objects.create(
            chapter=self.chapter,
            first_name='Test',
            last_name='Member',
            role='member',
            is_active=True
        )
        
        # Update stats
        self.club.update_stats()
        
        self.assertEqual(self.club.total_chapters, 1)
        self.assertEqual(self.club.total_members, 1)

    def test_club_update_stats_with_inactive_chapter(self):
        """Test club stats exclude inactive chapters"""
        # Make chapter inactive
        self.chapter.is_active = False
        self.chapter.save()
        
        Member.objects.create(
            chapter=self.chapter,
            first_name='Test',
            last_name='Member',
            role='member',
            is_active=True
        )
        
        self.club.update_stats()
        
        # Should not count inactive chapters
        self.assertEqual(self.club.total_chapters, 0)
        self.assertEqual(self.club.total_members, 0)

    def test_club_update_stats_with_inactive_members(self):
        """Test club stats exclude inactive members"""
        Member.objects.create(
            chapter=self.chapter,
            first_name='Active',
            last_name='Member',
            role='member',
            is_active=True
        )
        
        Member.objects.create(
            chapter=self.chapter,
            first_name='Inactive',
            last_name='Member',
            role='member',
            is_active=False
        )
        
        self.club.update_stats()
        
        self.assertEqual(self.club.total_chapters, 1)
        self.assertEqual(self.club.total_members, 1)  # Only active member

    def test_chapter_save_updates_club_stats(self):
        """Test that saving a chapter triggers club stats update"""
        initial_chapters = self.club.total_chapters
        
        # Create new chapter
        Chapter.objects.create(
            club=self.club,
            name='Second Chapter',
            owner=self.user
        )
        
        # Refresh club from database
        self.club.refresh_from_db()
        
        # Should have updated automatically
        self.assertEqual(self.club.total_chapters, initial_chapters + 1)


class ChapterJoinRequestModelTests(TestCase):
    """Test ChapterJoinRequest model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.club = Club.objects.create(
            name='Test Club',
            accepts_new_chapters=True
        )

    def test_chapter_join_request_creation(self):
        """Test creating a chapter join request"""
        request = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.user,
            proposed_chapter_name='New Chapter',
            city='Test City',
            state='Test State',
            description='A new chapter description',
            reason='We want to join this awesome club',
            estimated_members=5
        )
        
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.club, self.club)
        self.assertEqual(request.requested_by, self.user)
        self.assertEqual(request.proposed_chapter_name, 'New Chapter')
        self.assertEqual(request.estimated_members, 5)

    def test_chapter_join_request_str_representation(self):
        """Test string representation of ChapterJoinRequest"""
        request = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.user,
            proposed_chapter_name='New Chapter',
            city='Test City',
            state='Test State',
            description='A new chapter description',
            reason='We want to join this awesome club',
            estimated_members=5
        )
        
        expected_str = 'New Chapter - Test Club (pending)'
        self.assertEqual(str(request), expected_str)

    def test_chapter_join_request_status_choices(self):
        """Test status choices validation"""
        request = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.user,
            proposed_chapter_name='New Chapter',
            city='Test City',
            state='Test State',
            description='A new chapter description',
            reason='We want to join this awesome club',
            estimated_members=5
        )
        
        # Test valid status changes
        valid_statuses = ['pending', 'approved', 'rejected']
        
        for status in valid_statuses:
            request.status = status
            request.full_clean()  # Should not raise ValidationError

    def test_chapter_join_request_ordering(self):
        """Test that requests are ordered by creation date (newest first)"""
        request1 = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.user,
            proposed_chapter_name='First Chapter',
            city='Test City',
            state='Test State',
            description='First description',
            reason='First reason',
            estimated_members=3
        )
        
        request2 = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.user,
            proposed_chapter_name='Second Chapter',
            city='Test City',
            state='Test State',
            description='Second description',
            reason='Second reason',
            estimated_members=4
        )
        
        requests = ChapterJoinRequest.objects.all()
        self.assertEqual(requests[0], request2)  # Newest first
        self.assertEqual(requests[1], request1)


class DiscoveryPlatformIntegrationTests(TestCase):
    """Test integration between discovery platform models"""
    
    def setUp(self):
        self.club_owner = User.objects.create_user(
            username='club_owner',
            email='owner@example.com',
            password='testpass123'
        )
        
        self.chapter_requester = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.club = Club.objects.create(
            name='Rocky Point Riders MC',
            club_type='mc',
            country='Mexico',
            primary_state='Sonora',
            founded_year=2010,
            is_public=True,
            accepts_new_chapters=True
        )

    def test_full_chapter_creation_workflow(self):
        """Test complete workflow from join request to chapter creation"""
        # Step 1: Create join request
        join_request = ChapterJoinRequest.objects.create(
            club=self.club,
            requested_by=self.chapter_requester,
            proposed_chapter_name='Ciudad del Carmen Chapter',
            city='Ciudad del Carmen',
            state='Campeche',
            description='Chapter for Carmen riders',
            reason='We have 8 active riders who want to join',
            estimated_members=8
        )
        
        self.assertEqual(join_request.status, 'pending')
        
        # Step 2: Approve request and create chapter
        join_request.status = 'approved'
        join_request.save()
        
        chapter = Chapter.objects.create(
            club=self.club,
            name=join_request.proposed_chapter_name,
            city=join_request.city,
            state=join_request.state,
            description=join_request.description,
            owner=join_request.requested_by,
            is_active=True,
            is_public=True
        )
        
        # Step 3: Verify chapter was created correctly
        self.assertEqual(chapter.name, 'Ciudad del Carmen Chapter')
        self.assertEqual(chapter.city, 'Ciudad del Carmen')
        self.assertEqual(chapter.state, 'Campeche')
        self.assertEqual(chapter.owner, self.chapter_requester)
        self.assertTrue(chapter.is_active)
        self.assertTrue(chapter.is_public)
        
        # Step 4: Verify club stats updated
        self.club.refresh_from_db()
        self.assertEqual(self.club.total_chapters, 1)

    def test_multi_chapter_club_stats(self):
        """Test club stats with multiple chapters and members"""
        # Create multiple chapters
        chapter1 = Chapter.objects.create(
            club=self.club,
            name='Chapter 1',
            city='City 1',
            state='State 1',
            owner=self.club_owner,
            is_active=True
        )
        
        chapter2 = Chapter.objects.create(
            club=self.club,
            name='Chapter 2',
            city='City 2',
            state='State 2',
            owner=self.club_owner,
            is_active=True
        )
        
        # Create members in each chapter
        Member.objects.create(
            chapter=chapter1,
            first_name='Member1',
            last_name='Chapter1',
            role='president',
            is_active=True
        )
        
        Member.objects.create(
            chapter=chapter1,
            first_name='Member2',
            last_name='Chapter1',
            role='member',
            is_active=True
        )
        
        Member.objects.create(
            chapter=chapter2,
            first_name='Member1',
            last_name='Chapter2',
            role='president',
            is_active=True
        )
        
        # Update and verify stats
        self.club.update_stats()
        
        self.assertEqual(self.club.total_chapters, 2)
        self.assertEqual(self.club.total_members, 3)

    def test_club_visibility_settings(self):
        """Test club visibility and chapter acceptance settings"""
        # Test public club that accepts chapters
        public_club = Club.objects.create(
            name='Public Club',
            is_public=True,
            accepts_new_chapters=True
        )
        
        self.assertTrue(public_club.is_public)
        self.assertTrue(public_club.accepts_new_chapters)
        
        # Test private club that doesn't accept chapters
        private_club = Club.objects.create(
            name='Private Club',
            is_public=False,
            accepts_new_chapters=False
        )
        
        self.assertFalse(private_club.is_public)
        self.assertFalse(private_club.accepts_new_chapters)

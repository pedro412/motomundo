from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class EnhancedPermissionTests(TestCase):
    def setUp(self):
        # Create test data
        self.harley_club = Club.objects.create(name="Harley Club", description="Test club")
        self.bmw_club = Club.objects.create(name="BMW Club", description="Another test club")
        
        self.sf_chapter = Chapter.objects.create(name="SF Chapter", club=self.harley_club)
        self.la_chapter = Chapter.objects.create(name="LA Chapter", club=self.harley_club)
        self.munich_chapter = Chapter.objects.create(name="Munich Chapter", club=self.bmw_club)
        
        # Create users
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.harley_admin = User.objects.create_user('harley_admin', 'harley@test.com', 'pass')
        self.bmw_admin = User.objects.create_user('bmw_admin', 'bmw@test.com', 'pass')
        self.regular_user = User.objects.create_user('regular', 'regular@test.com', 'pass')
        self.new_user = User.objects.create_user('newuser', 'new@test.com', 'pass')
        
        # Create club admin assignments
        ClubAdmin.objects.create(user=self.harley_admin, club=self.harley_club, created_by=self.superuser)
        ClubAdmin.objects.create(user=self.bmw_admin, club=self.bmw_club, created_by=self.superuser)
        
        self.client = APIClient()
    
    def test_club_admin_can_assign_other_club_admins_to_their_club(self):
        """Test that club admins can assign other users as club admins for their clubs"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.post('/api/club-admins/', {
            'user': self.new_user.id,
            'club': self.harley_club.id
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ClubAdmin.objects.filter(user=self.new_user, club=self.harley_club).exists())
        
        # Check that created_by is set correctly
        club_admin = ClubAdmin.objects.get(user=self.new_user, club=self.harley_club)
        self.assertEqual(club_admin.created_by, self.harley_admin)
    
    def test_club_admin_cannot_assign_club_admins_to_other_clubs(self):
        """Test that club admins cannot assign users to clubs they don't manage"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.post('/api/club-admins/', {
            'user': self.new_user.id,
            'club': self.bmw_club.id  # Harley admin trying to assign to BMW club
        })
        
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ClubAdmin.objects.filter(user=self.new_user, club=self.bmw_club).exists())
    
    def test_club_admin_can_assign_chapter_managers_to_their_chapters(self):
        """Test that club admins can assign chapter admins to chapters in their clubs"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.post('/api/chapter-admins/', {
            'user': self.new_user.id,
            'chapter': self.sf_chapter.id
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ChapterAdmin.objects.filter(user=self.new_user, chapter=self.sf_chapter).exists())
    
    def test_club_admin_cannot_assign_chapter_managers_to_other_chapters(self):
        """Test that club admins cannot assign managers to chapters in other clubs"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.post('/api/chapter-admins/', {
            'user': self.new_user.id,
            'chapter': self.munich_chapter.id  # Chapter in BMW club
        })
        
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ChapterAdmin.objects.filter(user=self.new_user, chapter=self.munich_chapter).exists())
    
    def test_club_admin_can_view_their_club_admin_assignments(self):
        """Test that club admins can view other club admin assignments for their clubs"""
        # Create another club admin for the same club
        ClubAdmin.objects.create(user=self.new_user, club=self.harley_club, created_by=self.superuser)
        
        self.client.force_authenticate(user=self.harley_admin)
        response = self.client.get('/api/club-admins/')
        
        self.assertEqual(response.status_code, 200)
        
        # Should see both assignments for Harley club (including their own)
        club_admin_users = [ca['user'] for ca in response.data['results']]
        self.assertIn(self.harley_admin.id, club_admin_users)
        self.assertIn(self.new_user.id, club_admin_users)
        
        # Should not see BMW club assignments
        bmw_assignments = [ca for ca in response.data['results'] if ca['club'] == self.bmw_club.id]
        self.assertEqual(len(bmw_assignments), 0)
    
    def test_club_admin_cannot_assign_themselves(self):
        """Test that club admins cannot assign themselves as club admin (validation)"""
        self.client.force_authenticate(user=self.harley_admin)
        
        response = self.client.post('/api/club-admins/', {
            'user': self.harley_admin.id,
            'club': self.harley_club.id
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('must make a unique set', str(response.data).lower())
    
    def test_prevent_duplicate_club_admin_assignments(self):
        """Test that duplicate club admin assignments are prevented"""
        self.client.force_authenticate(user=self.superuser)
        
        # Try to assign harley_admin again (already assigned in setUp)
        response = self.client.post('/api/club-admins/', {
            'user': self.harley_admin.id,
            'club': self.harley_club.id
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('must make a unique set', str(response.data).lower())
    
    def test_prevent_duplicate_chapter_manager_assignments(self):
        """Test that duplicate chapter admin assignments are prevented"""
        # Create initial assignment
        ChapterAdmin.objects.create(user=self.new_user, chapter=self.sf_chapter, created_by=self.superuser)
        
        self.client.force_authenticate(user=self.superuser)
        
        # Try to assign again
        response = self.client.post('/api/chapter-admins/', {
            'user': self.new_user.id,
            'chapter': self.sf_chapter.id
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('must make a unique set', str(response.data).lower())
    
    def test_enhanced_user_permissions_endpoint(self):
        """Test the enhanced user permissions endpoint with detailed role information"""
        # Create a chapter admin assignment for the harley_admin
        ChapterAdmin.objects.create(user=self.harley_admin, chapter=self.sf_chapter, created_by=self.superuser)
        
        self.client.force_authenticate(user=self.harley_admin)
        response = self.client.get('/api/auth/permissions/')
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # Check permissions
        self.assertTrue(data['permissions']['can_assign_club_admins'])
        self.assertTrue(data['permissions']['can_assign_chapter_managers'])
        self.assertFalse(data['permissions']['can_manage_all_clubs'])
        
        # Check accessible clubs
        self.assertEqual(len(data['accessible_clubs']), 1)
        self.assertEqual(data['accessible_clubs'][0]['name'], 'Harley Club')
        self.assertEqual(data['accessible_clubs'][0]['role'], 'admin')
        
        # Check accessible chapters (should include both from club admin and chapter admin roles)
        chapter_names = [ch['name'] for ch in data['accessible_chapters']]
        self.assertIn('SF Chapter', chapter_names)
        self.assertIn('LA Chapter', chapter_names)
        
        # Check statistics
        self.assertEqual(data['statistics']['clubs_count'], 1)
        self.assertEqual(data['statistics']['chapters_count'], 2)  # Both chapters in Harley club
    
    def test_regular_user_cannot_access_admin_endpoints(self):
        """Test that regular users cannot access club admin or chapter admin endpoints"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to view club admins
        response = self.client.get('/api/club-admins/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)  # Should see no results
        
        # Try to create club admin
        response = self.client.post('/api/club-admins/', {
            'user': self.new_user.id,
            'club': self.harley_club.id
        })
        self.assertEqual(response.status_code, 403)
        
        # Try to view chapter admins
        response = self.client.get('/api/chapter-admins/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)  # Should see no results
        
        # Try to create chapter admin
        response = self.client.post('/api/chapter-admins/', {
            'user': self.new_user.id,
            'chapter': self.sf_chapter.id
        })
        self.assertEqual(response.status_code, 403)
    
    def test_superuser_can_assign_to_any_club_or_chapter(self):
        """Test that superusers can assign admins/managers to any club/chapter"""
        self.client.force_authenticate(user=self.superuser)
        
        # Assign club admin to any club
        response = self.client.post('/api/club-admins/', {
            'user': self.new_user.id,
            'club': self.bmw_club.id
        })
        self.assertEqual(response.status_code, 201)
        
        # Assign chapter admin to any chapter
        response = self.client.post('/api/chapter-admins/', {
            'user': self.regular_user.id,
            'chapter': self.munich_chapter.id
        })
        self.assertEqual(response.status_code, 201)
    
    def test_club_admin_can_delete_club_admin_assignments_in_their_club(self):
        """Test that club admins can delete club admin assignments for their clubs"""
        # Create another club admin for the same club
        new_admin = ClubAdmin.objects.create(user=self.new_user, club=self.harley_club, created_by=self.superuser)
        
        self.client.force_authenticate(user=self.harley_admin)
        
        # Should be able to delete the assignment
        response = self.client.delete(f'/api/club-admins/{new_admin.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ClubAdmin.objects.filter(id=new_admin.id).exists())
    
    def test_club_admin_can_delete_chapter_manager_assignments_in_their_club(self):
        """Test that club admins can delete chapter admin assignments for chapters in their clubs"""
        # Create chapter admin for their chapter
        manager = ChapterAdmin.objects.create(user=self.new_user, chapter=self.sf_chapter, created_by=self.superuser)
        
        self.client.force_authenticate(user=self.harley_admin)
        
        # Should be able to delete the assignment
        response = self.client.delete(f'/api/chapter-admins/{manager.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ChapterAdmin.objects.filter(id=manager.id).exists())

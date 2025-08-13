"""
Test to reproduce and fix the permission edge case
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class PermissionEdgeCaseTest(APITestCase):
    """
    Test to reproduce the specific permission issue where chapter admin
    could create members in other clubs
    """
    
    def setUp(self):
        # Create users
        self.superuser = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='admin123'
        )
        
        self.club_owner = User.objects.create_user(
            username='clubowner',
            email='clubowner@test.com',
            password='test123'
        )
        
        self.chapter_admin = User.objects.create_user(
            username='chapteradmin',
            email='chapteradmin@test.com', 
            password='test123'
        )
        
        # Create clubs
        self.club_a = Club.objects.create(name='Club A')
        self.club_b = Club.objects.create(name='Club B')
        
        # Create chapters
        self.chapter_a1 = Chapter.objects.create(club=self.club_a, name='Chapter A1')
        self.chapter_a2 = Chapter.objects.create(club=self.club_a, name='Chapter A2') 
        self.chapter_b1 = Chapter.objects.create(club=self.club_b, name='Chapter B1')
        
        # Assign permissions
        ClubAdmin.objects.create(user=self.club_owner, club=self.club_a)
        ClubAdmin.objects.create(user=self.club_owner, club=self.club_b)
        ChapterAdmin.objects.create(user=self.chapter_admin, chapter=self.chapter_a1)
        
        print(f"Setup complete:")
        print(f"  Club A (id={self.club_a.id}): Chapter A1 (id={self.chapter_a1.id}), Chapter A2 (id={self.chapter_a2.id})")
        print(f"  Club B (id={self.club_b.id}): Chapter B1 (id={self.chapter_b1.id})")
        print(f"  Chapter admin has access to: Chapter A1 only")
    
    def test_chapter_admin_permission_boundaries(self):
        """
        Test that chapter admin can only create members in their assigned chapter
        """
        print("\n--- Testing Chapter Admin Permission Boundaries ---")
        
        # Authenticate as chapter admin
        self.client.force_authenticate(user=self.chapter_admin)
        
        # Test 1: Should be able to create member in assigned chapter (Chapter A1)
        print("Test 1: Creating member in assigned chapter (Chapter A1)...")
        member_data_allowed = {
            'chapter': self.chapter_a1.id,
            'first_name': 'Allowed',
            'last_name': 'Member',
            'role': 'rider',
            'user': None
        }
        response = self.client.post('/api/members/', member_data_allowed, format='json')
        print(f"  Response: {response.status_code}")
        if response.status_code != 201:
            print(f"  Error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("  ✓ Success: Can create member in assigned chapter")
        
        # Test 2: Should NOT be able to create member in other chapter of same club (Chapter A2)
        print("Test 2: Creating member in other chapter of same club (Chapter A2)...")
        member_data_same_club = {
            'chapter': self.chapter_a2.id,
            'first_name': 'SameClub',
            'last_name': 'Member',
            'role': 'rider',
            'user': None
        }
        response = self.client.post('/api/members/', member_data_same_club, format='json')
        print(f"  Response: {response.status_code}")
        if response.status_code == 201:
            print(f"  ⚠️  WARNING: Chapter admin was able to create member in other chapter of same club!")
            print(f"  Response data: {response.data}")
        else:
            print(f"  ✓ Success: Correctly denied access to other chapter in same club")
        
        # Test 3: Should NOT be able to create member in different club (Chapter B1)
        print("Test 3: Creating member in different club (Chapter B1)...")
        member_data_diff_club = {
            'chapter': self.chapter_b1.id,
            'first_name': 'DiffClub',
            'last_name': 'Member',
            'role': 'rider',
            'user': None
        }
        response = self.client.post('/api/members/', member_data_diff_club, format='json')
        print(f"  Response: {response.status_code}")
        if response.status_code == 201:
            print(f"  ⚠️  WARNING: Chapter admin was able to create member in different club!")
            print(f"  Response data: {response.data}")
        else:
            print(f"  ✓ Success: Correctly denied access to different club")
        
        # Print current state
        print(f"\nCurrent member counts:")
        for chapter in [self.chapter_a1, self.chapter_a2, self.chapter_b1]:
            count = Member.objects.filter(chapter=chapter).count()
            print(f"  {chapter.name}: {count} members")
    
    def test_club_admin_has_full_access(self):
        """
        Test that club admin can create members in any chapter of their clubs
        """
        print("\n--- Testing Club Admin Full Access ---")
        
        # Authenticate as club owner (who is admin of both clubs)
        self.client.force_authenticate(user=self.club_owner)
        
        # Should be able to create members in any chapter
        chapters_to_test = [self.chapter_a1, self.chapter_a2, self.chapter_b1]
        
        for i, chapter in enumerate(chapters_to_test):
            member_data = {
                'chapter': chapter.id,
                'first_name': f'ClubAdmin{i}',
                'last_name': 'Member',
                'role': 'rider',
                'user': None
            }
            response = self.client.post('/api/members/', member_data, format='json')
            print(f"Creating member in {chapter.name}: {response.status_code}")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        print("✓ Club admin has full access to all chapters in managed clubs")


if __name__ == '__main__':
    import django
    import os
    import sys
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
    sys.path.append('/Users/pedro412/motomundo')
    django.setup()
    
    # Run tests
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    result = runner.run_tests(['test_permission_edge_case'])
    sys.exit(result)

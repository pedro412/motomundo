"""
Test for Club Admin who is also a Member scenario
Demonstrates the Alterados MC President who is also a member of Nuevo Laredo chapter
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class ClubAdminAsMemberTest(APITestCase):
    """
    Test the realistic scenario where a club admin is also a member of a chapter
    Example: President of Alterados MC is also a member of Nuevo Laredo chapter
    """
    
    def test_club_admin_as_member_workflow(self):
        """
        Test the complete workflow of a club admin who is also a chapter member
        """
        print("\n" + "="*80)
        print("TESTING: CLUB ADMIN WHO IS ALSO A MEMBER")
        print("Scenario: President of Alterados MC is member of Nuevo Laredo chapter")
        print("="*80)
        
        # ================================================================
        # PHASE 1: SETUP BASIC STRUCTURE
        # ================================================================
        print("\n--- Phase 1: Setup Club Structure ---")
        
        # Create superuser for initial setup
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@alterados.mx',
            password='admin123'
        )
        
        # Create the club president user
        club_president = User.objects.create_user(
            username='presidente',
            email='presidente@alterados.mx',
            password='presidente123',
            first_name='Carlos',
            last_name='Rodriguez'
        )
        print(f"✓ Club president user created: {club_president.get_full_name()}")
        
        # Create Alterados MC club
        self.client.force_authenticate(user=superuser)
        club_data = {
            'name': 'Alterados MC',
            'description': 'Motorcycle Club Alterados',
            'foundation_date': '2010-03-15',
            'website': 'https://alterados.mx'
        }
        response = self.client.post('/api/clubs/', club_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alterados_club = Club.objects.get(id=response.data['id'])
        print(f"✓ Club created: {alterados_club.name}")
        
        # Create chapters
        nuevo_laredo_data = {
            'club': alterados_club.id,
            'name': 'Nuevo Laredo',
            'description': 'Capítulo Nuevo Laredo',
            'foundation_date': '2010-04-01'
        }
        response = self.client.post('/api/chapters/', nuevo_laredo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        nuevo_laredo_chapter = Chapter.objects.get(id=response.data['id'])
        print(f"✓ Chapter created: {nuevo_laredo_chapter.name}")
        
        monterrey_data = {
            'club': alterados_club.id,
            'name': 'Monterrey',
            'description': 'Capítulo Monterrey',
            'foundation_date': '2011-01-15'
        }
        response = self.client.post('/api/chapters/', monterrey_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        monterrey_chapter = Chapter.objects.get(id=response.data['id'])
        print(f"✓ Chapter created: {monterrey_chapter.name}")
        
        # ================================================================
        # PHASE 2: ASSIGN CLUB ADMIN ROLE
        # ================================================================
        print("\n--- Phase 2: Assign Club Admin Role ---")
        
        # Make Carlos the club admin
        club_admin_data = {
            'user': club_president.id,
            'club': alterados_club.id
        }
        response = self.client.post('/api/club-admins/', club_admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(f"✓ {club_president.get_full_name()} assigned as Club Admin of {alterados_club.name}")
        
        # ================================================================
        # PHASE 3: CREATE MEMBER IDENTITY
        # ================================================================
        print("\n--- Phase 3: Create Member Identity ---")
        
        # Now Carlos can act as club admin and create his own member record
        self.client.force_authenticate(user=club_president)
        
        # Carlos creates his member identity in Nuevo Laredo chapter
        member_data = {
            'chapter': nuevo_laredo_chapter.id,
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'nickname': 'El Presidente',
            'date_of_birth': '1975-07-12',
            'role': 'president',
            'joined_at': '2010-04-01',
            'user': club_president.id  # Link to his user account
        }
        response = self.client.post('/api/members/', member_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        carlos_member = Member.objects.get(id=response.data['id'])
        print(f"✓ Member identity created: {carlos_member} linked to user {carlos_member.user.username}")
        
        # ================================================================
        # PHASE 4: DEMONSTRATE DUAL ROLES
        # ================================================================
        print("\n--- Phase 4: Demonstrate Dual Roles ---")
        
        # Carlos can create other members (using club admin powers)
        print("4.1 Carlos exercises Club Admin powers...")
        
        # Create member in Nuevo Laredo (his own chapter)
        member_nl_data = {
            'chapter': nuevo_laredo_chapter.id,
            'first_name': 'Miguel',
            'last_name': 'Santos',
            'nickname': 'Lobo',
            'role': 'vice_president',
            'joined_at': '2010-05-15',
            'user': None
        }
        response = self.client.post('/api/members/', member_nl_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(f"  ✓ Created member in Nuevo Laredo: {response.data['first_name']} {response.data['last_name']}")
        
        # Create member in Monterrey (different chapter, using club admin powers)
        member_mty_data = {
            'chapter': monterrey_chapter.id,
            'first_name': 'Roberto',
            'last_name': 'Morales',
            'nickname': 'Rayo',
            'role': 'president',
            'joined_at': '2011-02-01',
            'user': None
        }
        response = self.client.post('/api/members/', member_mty_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(f"  ✓ Created member in Monterrey: {response.data['first_name']} {response.data['last_name']}")
        
        # ================================================================
        # PHASE 5: VERIFY USER ROLES AND PERMISSIONS
        # ================================================================
        print("\n--- Phase 5: Verify User Roles and Permissions ---")
        
        # Check Carlos's permissions
        response = self.client.get('/api/auth/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permissions = response.data
        
        print(f"Carlos's system roles:")
        print(f"  - Is Club Admin: {permissions['roles']['is_club_admin']}")
        print(f"  - Is Chapter Admin: {permissions['roles']['is_chapter_admin']}")
        print(f"  - Is Superuser: {permissions['roles']['is_superuser']}")
        
        # Verify Carlos's memberships
        carlos_memberships = Member.objects.filter(user=club_president)
        print(f"\nCarlos's memberships:")
        for membership in carlos_memberships:
            print(f"  - {membership.chapter.club.name} -> {membership.chapter.name} as {membership.role}")
            print(f"    Nickname: {membership.nickname}")
        
        # ================================================================
        # PHASE 6: MULTI-CLUB SCENARIO
        # ================================================================
        print("\n--- Phase 6: Multi-Club Scenario ---")
        
        # Create a second club where Carlos might be a regular member
        hermanos_data = {
            'name': 'Hermanos MC',
            'description': 'Another motorcycle club',
            'foundation_date': '2015-08-20'
        }
        # Switch to superuser to create the club
        self.client.force_authenticate(user=superuser)
        response = self.client.post('/api/clubs/', hermanos_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        hermanos_club = Club.objects.get(id=response.data['id'])
        
        # Create chapter in Hermanos MC
        hermanos_chapter_data = {
            'club': hermanos_club.id,
            'name': 'Capítulo Central',
            'description': 'Capítulo principal'
        }
        response = self.client.post('/api/chapters/', hermanos_chapter_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        hermanos_chapter = Chapter.objects.get(id=response.data['id'])
        
        # Someone else creates Carlos as a regular member in Hermanos MC
        # (showing he can be admin in one club and regular member in another)
        carlos_hermanos_member = Member.objects.create(
            chapter=hermanos_chapter,
            first_name='Carlos',
            last_name='Rodriguez',
            nickname='Visitante',
            role='rider',  # Just a regular rider, not president
            user=club_president  # Same user, different role
        )
        print(f"✓ Carlos added as regular member in {hermanos_club.name}")
        
        # ================================================================
        # PHASE 7: FINAL VERIFICATION
        # ================================================================
        print("\n--- Phase 7: Final System State ---")
        
        # Switch back to Carlos's authentication
        self.client.force_authenticate(user=club_president)
        
        # Carlos should see members from Alterados MC (his club admin role)
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        visible_members = response.data['results']
        alterados_members = [m for m in visible_members if m['chapter'] in [nuevo_laredo_chapter.id, monterrey_chapter.id]]
        print(f"Carlos can see {len(alterados_members)} members from Alterados MC (club admin access)")
        
        # Verify all Carlos's identities
        all_carlos_memberships = Member.objects.filter(user=club_president)
        print(f"\nCarlos's complete identity:")
        print(f"  System User: {club_president.username} ({club_president.get_full_name()})")
        print(f"  Administrative Role: Club Admin of {alterados_club.name}")
        print(f"  Member Identities:")
        for membership in all_carlos_memberships:
            print(f"    - {membership.chapter.club.name} / {membership.chapter.name}: {membership.role} ('{membership.nickname}')")
        
        # ================================================================
        # ASSERTIONS
        # ================================================================
        print("\n--- Final Assertions ---")
        
        # Verify Carlos is both club admin and member
        self.assertTrue(ClubAdmin.objects.filter(user=club_president, club=alterados_club).exists())
        self.assertTrue(Member.objects.filter(user=club_president, chapter=nuevo_laredo_chapter, role='president').exists())
        print("✓ Carlos is confirmed as both Club Admin and Chapter Member")
        
        # Verify multi-club membership with different roles
        carlos_alterados = Member.objects.get(user=club_president, chapter__club=alterados_club)
        carlos_hermanos = Member.objects.get(user=club_president, chapter__club=hermanos_club)
        self.assertEqual(carlos_alterados.role, 'president')
        self.assertEqual(carlos_hermanos.role, 'rider')
        print("✓ Carlos has different roles in different clubs: president vs rider")
        
        # Verify administrative access
        self.assertTrue(len(alterados_members) >= 3)  # Carlos + Miguel + Roberto
        print("✓ Carlos retains club admin access to manage all Alterados MC members")
        
        print("\n" + "="*80)
        print("SUCCESS: Club Admin as Member scenario fully validated!")
        print("="*80)
        
        return {
            'club_president': club_president,
            'alterados_club': alterados_club,
            'nuevo_laredo_chapter': nuevo_laredo_chapter,
            'carlos_memberships': list(all_carlos_memberships),
            'total_alterados_members': len(alterados_members)
        }


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
    result = runner.run_tests(['test_club_admin_member'])
    sys.exit(result)

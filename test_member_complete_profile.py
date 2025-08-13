"""
Test for the Complete Member Profile Feature
Demonstrates the cross-club profile view when clicking on a member
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
import json


class MemberCompleteProfileTest(APITestCase):
    """
    Test the complete member profile feature that shows all club memberships
    and administrative roles when clicking on a member
    """
    
    def test_complete_member_profile_feature(self):
        """
        Test the complete workflow of the member profile feature
        """
        print("\n" + "="*80)
        print("TESTING: COMPLETE MEMBER PROFILE FEATURE")
        print("Scenario: Click on member to see all their club memberships and roles")
        print("="*80)
        
        # ================================================================
        # PHASE 1: CREATE REALISTIC MULTI-CLUB SCENARIO
        # ================================================================
        print("\n--- Phase 1: Setup Multi-Club Scenario ---")
        
        # Create superuser
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@motomundo.com',
            password='admin123'
        )
        
        # Create the multi-club user (Carlos)
        carlos = User.objects.create_user(
            username='carlos_president',
            email='carlos@alterados.mx',
            password='carlos123',
            first_name='Carlos',
            last_name='Rodriguez'
        )
        
        # Create another user for comparison
        miguel = User.objects.create_user(
            username='miguel_member',
            email='miguel@alterados.mx',
            password='miguel123',
            first_name='Miguel',
            last_name='Santos'
        )
        
        print(f"✓ Users created: {carlos.get_full_name()}, {miguel.get_full_name()}")
        
        # Create clubs
        self.client.force_authenticate(user=superuser)
        
        # Alterados MC
        alterados_data = {
            'name': 'Alterados MC',
            'description': 'Motorcycle Club Alterados',
            'foundation_date': '2010-03-15'
        }
        response = self.client.post('/api/clubs/', alterados_data, format='json')
        alterados_club = Club.objects.get(id=response.data['id'])
        
        # Hermanos MC
        hermanos_data = {
            'name': 'Hermanos MC',
            'description': 'Hermanos Motorcycle Club',
            'foundation_date': '2015-08-20'
        }
        response = self.client.post('/api/clubs/', hermanos_data, format='json')
        hermanos_club = Club.objects.get(id=response.data['id'])
        
        # Riders United MC
        riders_data = {
            'name': 'Riders United MC',
            'description': 'United Riders Motorcycle Club',
            'foundation_date': '2018-05-10'
        }
        response = self.client.post('/api/clubs/', riders_data, format='json')
        riders_club = Club.objects.get(id=response.data['id'])
        
        print(f"✓ Clubs created: {alterados_club.name}, {hermanos_club.name}, {riders_club.name}")
        
        # Create chapters
        chapters_data = [
            {'club': alterados_club.id, 'name': 'Nuevo Laredo', 'description': 'Capítulo Nuevo Laredo'},
            {'club': alterados_club.id, 'name': 'Monterrey', 'description': 'Capítulo Monterrey'},
            {'club': hermanos_club.id, 'name': 'Central', 'description': 'Capítulo Central'},
            {'club': riders_club.id, 'name': 'Highway Chapter', 'description': 'Highway Riders Chapter'},
        ]
        
        chapters = {}
        for chapter_data in chapters_data:
            response = self.client.post('/api/chapters/', chapter_data, format='json')
            chapter = Chapter.objects.get(id=response.data['id'])
            chapters[f"{chapter.club.name}_{chapter.name}"] = chapter
            print(f"  ✓ Chapter created: {chapter.club.name} -> {chapter.name}")
        
        # ================================================================
        # PHASE 2: ASSIGN ADMINISTRATIVE ROLES TO CARLOS
        # ================================================================
        print("\n--- Phase 2: Assign Administrative Roles ---")
        
        # Make Carlos club admin of Alterados MC
        club_admin_data = {
            'user': carlos.id,
            'club': alterados_club.id
        }
        response = self.client.post('/api/club-admins/', club_admin_data, format='json')
        print(f"✓ Carlos assigned as Club Admin of {alterados_club.name}")
        
        # Make Carlos chapter admin of Highway Chapter in Riders United
        chapter_admin_data = {
            'user': carlos.id,
            'chapter': chapters['Riders United MC_Highway Chapter'].id
        }
        response = self.client.post('/api/chapter-admins/', chapter_admin_data, format='json')
        print(f"✓ Carlos assigned as Chapter Admin of Highway Chapter")
        
        # ================================================================
        # PHASE 3: CREATE MEMBER IDENTITIES FOR CARLOS
        # ================================================================
        print("\n--- Phase 3: Create Member Identities ---")
        
        # Switch to Carlos's authentication
        self.client.force_authenticate(user=carlos)
        
        # Carlos as President of Nuevo Laredo (Alterados MC)
        member_1_data = {
            'chapter': chapters['Alterados MC_Nuevo Laredo'].id,
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'nickname': 'El Presidente',
            'role': 'president',
            'joined_at': '2010-04-01',
            'user': carlos.id
        }
        response = self.client.post('/api/members/', member_1_data, format='json')
        carlos_alterados = Member.objects.get(id=response.data['id'])
        print(f"  ✓ Carlos created as: {carlos_alterados.role} in {carlos_alterados.chapter}")
        
        # Carlos as Secretary in Central (Hermanos MC) - created by someone else
        self.client.force_authenticate(user=superuser)
        member_2_data = {
            'chapter': chapters['Hermanos MC_Central'].id,
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'nickname': 'Hermano Carlos',
            'role': 'secretary',
            'joined_at': '2016-02-15',
            'user': carlos.id
        }
        response = self.client.post('/api/members/', member_2_data, format='json')
        carlos_hermanos = Member.objects.get(id=response.data['id'])
        print(f"  ✓ Carlos added as: {carlos_hermanos.role} in {carlos_hermanos.chapter}")
        
        # Carlos as Rider in Highway Chapter (Riders United MC)
        member_3_data = {
            'chapter': chapters['Riders United MC_Highway Chapter'].id,
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'nickname': 'Road Captain',
            'role': 'rider',
            'joined_at': '2019-03-10',
            'user': carlos.id
        }
        response = self.client.post('/api/members/', member_3_data, format='json')
        carlos_riders = Member.objects.get(id=response.data['id'])
        print(f"  ✓ Carlos added as: {carlos_riders.role} in {carlos_riders.chapter}")
        
        # Create Miguel as regular member (for comparison)
        miguel_member_data = {
            'chapter': chapters['Alterados MC_Nuevo Laredo'].id,
            'first_name': 'Miguel',
            'last_name': 'Santos',
            'nickname': 'Lobo',
            'role': 'vice_president',
            'joined_at': '2010-05-15',
            'user': miguel.id
        }
        response = self.client.post('/api/members/', miguel_member_data, format='json')
        miguel_member = Member.objects.get(id=response.data['id'])
        print(f"  ✓ Miguel created as: {miguel_member.role} in {miguel_member.chapter}")
        
        # ================================================================
        # PHASE 4: TEST COMPLETE PROFILE FEATURE
        # ================================================================
        print("\n--- Phase 4: Test Complete Profile Feature ---")
        
        # Test 1: Click on Carlos (multi-club member with admin roles)
        print("4.1 Testing Carlos's complete profile...")
        self.client.force_authenticate(user=carlos)  # Carlos can view profiles
        
        response = self.client.get(f'/api/members/{carlos_alterados.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        carlos_profile = response.data
        
        print(f"  ✓ Profile retrieved for: {carlos_profile['user']['full_name']}")
        print(f"  ✓ Total clubs: {carlos_profile['statistics']['total_clubs']}")
        print(f"  ✓ Total chapters: {carlos_profile['statistics']['total_chapters']}")
        print(f"  ✓ Total admin roles: {carlos_profile['statistics']['total_admin_roles']}")
        
        # Verify memberships
        memberships = carlos_profile['all_memberships']
        self.assertEqual(len(memberships), 3)  # Three clubs
        print(f"  ✓ All memberships found:")
        for membership in memberships:
            context_marker = " ← CLICKED" if membership['is_current_context'] else ""
            print(f"    - {membership['club_name']} / {membership['chapter_name']}: {membership['role']} ('{membership['nickname']}'){context_marker}")
        
        # Verify administrative roles
        admin_roles = carlos_profile['administrative_roles']
        self.assertEqual(len(admin_roles), 2)  # Club admin + Chapter admin
        print(f"  ✓ Administrative roles:")
        for role in admin_roles:
            if role['type'] == 'club_admin':
                print(f"    - Club Administrator of {role['club_name']}")
            else:
                print(f"    - Chapter Administrator of {role['club_name']} / {role['chapter_name']}")
        
        # Test 2: Click on Miguel (single club member, no admin roles)
        print("\n4.2 Testing Miguel's profile...")
        response = self.client.get(f'/api/members/{miguel_member.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        miguel_profile = response.data
        
        print(f"  ✓ Profile retrieved for: {miguel_profile['user']['full_name']}")
        print(f"  ✓ Total clubs: {miguel_profile['statistics']['total_clubs']}")
        print(f"  ✓ Total chapters: {miguel_profile['statistics']['total_chapters']}")
        print(f"  ✓ Total admin roles: {miguel_profile['statistics']['total_admin_roles']}")
        
        self.assertEqual(miguel_profile['statistics']['total_clubs'], 1)
        self.assertEqual(miguel_profile['statistics']['total_chapters'], 1)
        self.assertEqual(miguel_profile['statistics']['total_admin_roles'], 0)
        
        # Test 3: Create member without user account
        print("\n4.3 Testing member without user account...")
        unlinked_member_data = {
            'chapter': chapters['Alterados MC_Monterrey'].id,
            'first_name': 'Roberto',
            'last_name': 'Morales',
            'nickname': 'Rayo',
            'role': 'rider',
            'user': None
        }
        response = self.client.post('/api/members/', unlinked_member_data, format='json')
        unlinked_member = Member.objects.get(id=response.data['id'])
        
        response = self.client.get(f'/api/members/{unlinked_member.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('error', response.data)
        self.assertFalse(response.data['member_info']['has_user_account'])
        print(f"  ✓ Correctly handled member without user account: {response.data['member_info']['name']}")
        
        # ================================================================
        # PHASE 5: DETAILED VERIFICATION
        # ================================================================
        print("\n--- Phase 5: Detailed Feature Verification ---")
        
        # Verify clicked member context
        clicked_context = carlos_profile['clicked_member_context']
        self.assertEqual(clicked_context['member_id'], carlos_alterados.id)
        self.assertEqual(clicked_context['club_name'], 'Alterados MC')
        self.assertEqual(clicked_context['chapter_name'], 'Nuevo Laredo')
        self.assertEqual(clicked_context['member_role'], 'president')
        print(f"✓ Clicked member context: {clicked_context['club_name']} / {clicked_context['chapter_name']}")
        
        # Verify current context marking
        current_membership = next(m for m in memberships if m['is_current_context'])
        self.assertEqual(current_membership['member_id'], carlos_alterados.id)
        print(f"✓ Current context correctly marked: {current_membership['club_name']} / {current_membership['chapter_name']}")
        
        # Verify different roles in different clubs
        alterados_membership = next(m for m in memberships if m['club_name'] == 'Alterados MC')
        hermanos_membership = next(m for m in memberships if m['club_name'] == 'Hermanos MC')
        riders_membership = next(m for m in memberships if m['club_name'] == 'Riders United MC')
        
        self.assertEqual(alterados_membership['role'], 'president')
        self.assertEqual(hermanos_membership['role'], 'secretary')
        self.assertEqual(riders_membership['role'], 'rider')
        print(f"✓ Different roles verified: president, secretary, rider")
        
        # ================================================================
        # PHASE 6: FRONTEND USAGE SIMULATION
        # ================================================================
        print("\n--- Phase 6: Frontend Usage Simulation ---")
        
        print("Frontend workflow simulation:")
        print("1. User views Nuevo Laredo chapter member list")
        print("2. User sees 'Carlos Rodriguez (El Presidente)' - President")
        print("3. User clicks on Carlos's name")
        print("4. System calls: GET /api/members/{carlos_id}/complete-profile/")
        print("5. Frontend displays complete profile modal/page showing:")
        
        profile_summary = {
            'user_info': carlos_profile['user'],
            'current_context': carlos_profile['clicked_member_context'],
            'summary': carlos_profile['statistics'],
            'all_identities': carlos_profile['all_memberships'],
            'admin_roles': carlos_profile['administrative_roles']
        }
        
        print("\n   Profile Modal Content:")
        print(f"   User: {profile_summary['user_info']['full_name']} (@{profile_summary['user_info']['username']})")
        print(f"   Email: {profile_summary['user_info']['email']}")
        print(f"   Member since: {str(profile_summary['user_info']['date_joined'])[:10]}")
        print(f"   ")
        print(f"   Currently viewing: {profile_summary['current_context']['member_role']} of {profile_summary['current_context']['chapter_name']}")
        print(f"   ")
        print(f"   Summary: {profile_summary['summary']['total_clubs']} clubs, {profile_summary['summary']['total_chapters']} chapters, {profile_summary['summary']['total_admin_roles']} admin roles")
        print(f"   ")
        print("   All Memberships:")
        for membership in profile_summary['all_identities']:
            marker = " ← Current" if membership['is_current_context'] else ""
            print(f"     • {membership['club_name']} / {membership['chapter_name']}: {membership['role']} ('{membership['nickname']}'){marker}")
        print("   ")
        print("   Administrative Roles:")
        for role in profile_summary['admin_roles']:
            if role['type'] == 'club_admin':
                print(f"     • Club Admin: {role['club_name']} (since {role['since']})")
            else:
                print(f"     • Chapter Admin: {role['club_name']} / {role['chapter_name']} (since {role['since']})")
        
        print("\n" + "="*80)
        print("SUCCESS: Complete Member Profile Feature Fully Implemented!")
        print("="*80)
        
        return {
            'carlos_profile': carlos_profile,
            'miguel_profile': miguel_profile,
            'feature_working': True
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
    result = runner.run_tests(['test_member_complete_profile'])
    sys.exit(result)

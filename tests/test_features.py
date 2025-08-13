"""
Feature Tests for Motomundo
Tests for specific features like member profiles, club management, etc.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
import json


class MemberProfileFeatureTestCase(APITestCase):
    """
    Test the complete member profile feature that shows all club memberships
    and administrative roles when clicking on a member
    """
    
    def test_complete_member_profile_feature(self):
        """
        Test the complete workflow of the member profile feature
        Demonstrates cross-club profile view when clicking on a member
        """
        print("\n" + "="*80)
        print("TESTING: COMPLETE MEMBER PROFILE FEATURE")
        print("Scenario: Click on member to see all their club memberships and roles")
        print("="*80)
        
        # ================================================================
        # PHASE 1: CREATE REALISTIC MULTI-CLUB SCENARIO
        # ================================================================
        print("\n--- Phase 1: Setup Multi-Club Scenario ---")
        
        # Create users
        carlos = User.objects.create_user(
            username='carlos_president',
            email='carlos@alterados.mx',
            password='pass',
            first_name='Carlos',
            last_name='Rodriguez'
        )
        
        miguel = User.objects.create_user(
            username='miguel_vp',
            email='miguel@alterados.mx', 
            password='pass',
            first_name='Miguel',
            last_name='Santos'
        )
        
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        print("✓ Users created: Carlos Rodriguez, Miguel Santos")
        
        # Create multiple clubs (realistic Mexican MC scenario)
        alterados = Club.objects.create(
            name='Alterados MC',
            description='Motorcycle club from Nuevo Laredo'
        )
        
        hermanos = Club.objects.create(
            name='Hermanos MC',
            description='Brotherhood motorcycle club'
        )
        
        riders_united = Club.objects.create(
            name='Riders United MC',
            description='International motorcycle riders'
        )
        print("✓ Clubs created: Alterados MC, Hermanos MC, Riders United MC")
        
        # Create chapters
        nuevo_laredo = Chapter.objects.create(name='Nuevo Laredo', club=alterados)
        monterrey_alterados = Chapter.objects.create(name='Monterrey', club=alterados)
        monterrey_hermanos = Chapter.objects.create(name='Central', club=hermanos)
        highway_chapter = Chapter.objects.create(name='Highway Chapter', club=riders_united)
        
        print("  ✓ Chapter created: Alterados MC -> Nuevo Laredo")
        print("  ✓ Chapter created: Alterados MC -> Monterrey")
        print("  ✓ Chapter created: Hermanos MC -> Central")
        print("  ✓ Chapter created: Riders United MC -> Highway Chapter")
        
        # ================================================================
        # PHASE 2: ASSIGN ADMINISTRATIVE ROLES
        # ================================================================
        print("\n--- Phase 2: Assign Administrative Roles ---")
        
        # Carlos is Club Admin of Alterados MC
        ClubAdmin.objects.create(user=carlos, club=alterados, created_by=superuser)
        print("✓ Carlos assigned as Club Admin of Alterados MC")
        
        # Carlos is also Chapter Admin of Highway Chapter (cross-club admin)
        ChapterAdmin.objects.create(user=carlos, chapter=highway_chapter, created_by=superuser)
        print("✓ Carlos assigned as Chapter Admin of Highway Chapter")
        
        # ================================================================
        # PHASE 3: CREATE MEMBER IDENTITIES
        # ================================================================
        print("\n--- Phase 3: Create Member Identities ---")
        
        # Carlos as member in Alterados MC (his main club where he's president)
        carlos_alterados = Member.objects.create(
            user=carlos,
            first_name='Carlos',
            last_name='Rodriguez',
            nickname='El Presidente',
            chapter=nuevo_laredo,
            role='president'
        )
        print("  ✓ Carlos created as: president in Nuevo Laredo (Alterados MC)")
        
        # Carlos as member in Hermanos MC (cross-club membership)
        carlos_hermanos = Member.objects.create(
            user=carlos,
            first_name='Carlos',
            last_name='Rodriguez',
            nickname='Hermano Carlos',
            chapter=monterrey_hermanos,
            role='secretary'
        )
        print("  ✓ Carlos added as: secretary in Central (Hermanos MC)")
        
        # Carlos as member in Riders United MC (where he's also chapter admin)
        carlos_riders = Member.objects.create(
            user=carlos,
            first_name='Carlos',
            last_name='Rodriguez',
            nickname='Road Captain',
            chapter=highway_chapter,
            role='rider'
        )
        print("  ✓ Carlos added as: rider in Highway Chapter (Riders United MC)")
        
        # Miguel as regular member
        miguel_member = Member.objects.create(
            user=miguel,
            first_name='Miguel',
            last_name='Santos',
            nickname='El Guerrero',
            chapter=nuevo_laredo,
            role='vice_president'
        )
        print("  ✓ Miguel created as: vice_president in Nuevo Laredo (Alterados MC)")
        
        # Create a member without user account (for testing edge case)
        roberto_member = Member.objects.create(
            first_name='Roberto',
            last_name='Morales',
            nickname='Ghost Rider',
            chapter=nuevo_laredo,
            role='rider'
        )
        
        # ================================================================
        # PHASE 4: TEST COMPLETE PROFILE FEATURE
        # ================================================================
        print("\n--- Phase 4: Test Complete Profile Feature ---")
        
        # Authenticate as superuser to access the API
        login_data = {'username': 'admin', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # 4.1 Test Carlos's complete profile (complex scenario)
        print("4.1 Testing Carlos's complete profile...")
        response = self.client.get(f'/api/members/{carlos_alterados.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        profile_data = response.json()
        print(f"  ✓ Profile retrieved for: {profile_data['user']['full_name']}")
        
        # Verify profile structure and data
        self.assertEqual(profile_data['user']['username'], 'carlos_president')
        self.assertEqual(profile_data['user']['full_name'], 'Carlos Rodriguez')
        self.assertEqual(len(profile_data['all_memberships']), 3)
        self.assertEqual(len(profile_data['administrative_roles']), 2)
        
        print(f"  ✓ Total clubs: {profile_data['statistics']['total_clubs']}")
        print(f"  ✓ Total chapters: {profile_data['statistics']['total_chapters']}")
        print(f"  ✓ Total admin roles: {profile_data['statistics']['total_admin_roles']}")
        
        # Verify comprehensive data structure
        expected_clubs = ['Alterados MC', 'Hermanos MC', 'Riders United MC']
        actual_clubs = [m['club_name'] for m in profile_data['all_memberships']]
        for club in expected_clubs:
            self.assertIn(club, actual_clubs, f"Carlos should be a member of {club}")
        
        # Verify administrative roles
        self.assertEqual(len(profile_data['administrative_roles']), 2)
        admin_types = [role['type'] for role in profile_data['administrative_roles']]
        self.assertIn('club_admin', admin_types)
        self.assertIn('chapter_admin', admin_types)
        
        print("✓ Complete profile feature validates all membership and administrative data")
        
        # 4.2 Test Miguel's simpler profile (single club member)
        print("4.2 Testing Miguel's profile (single club member)...")
        response = self.client.get(f'/api/members/{miguel_member.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        miguel_data = response.json()
        
        print(f"  ✓ Miguel's profile: {miguel_data['user']['full_name']}")
        print(f"  ✓ Miguel's clubs: {miguel_data['statistics']['total_clubs']}")
        self.assertEqual(miguel_data['statistics']['total_clubs'], 1)
        self.assertEqual(len(miguel_data['administrative_roles']), 0)
        
        print("✓ Single club member profile works correctly")
        
        print("\n================================================================================")
        print("MEMBER PROFILE FEATURE TEST COMPLETE ✓")
        print("================================================================================")
        
        print("  ✓ All memberships found:")
        for membership in profile_data['all_memberships']:
            current_marker = " ← CLICKED" if membership['is_current_context'] else ""
            print(f"    - {membership['club_name']} / {membership['chapter_name']}: {membership['role']} ('{membership['nickname']}'){current_marker}")
        
        print("  ✓ Administrative roles:")
        for role in profile_data['administrative_roles']:
            print(f"    - {role}")
        
        # 4.2 Test Miguel's profile (simpler scenario)
        print("\n4.2 Testing Miguel's profile...")
        response = self.client.get(f'/api/members/{miguel_member.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        miguel_profile = response.json()
        print(f"  ✓ Profile retrieved for: {miguel_profile['user']['full_name']}")
        self.assertEqual(len(miguel_profile['all_memberships']), 1)
        self.assertEqual(len(miguel_profile['administrative_roles']), 0)
        print(f"  ✓ Total clubs: {miguel_profile['statistics']['total_clubs']}")
        print(f"  ✓ Total chapters: {miguel_profile['statistics']['total_chapters']}")
        print(f"  ✓ Total admin roles: {miguel_profile['statistics']['total_admin_roles']}")
        
        # 4.3 Test member without user account
        print("\n4.3 Testing member without user account...")
        response = self.client.get(f'/api/members/{roberto_member.id}/complete-profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        roberto_profile = response.json()
        self.assertIn('error', roberto_profile)
        self.assertFalse(roberto_profile['member_info']['has_user_account'])
        print(f"  ✓ Correctly handled member without user account: {roberto_profile['member_info']['name']}")
        
        # ================================================================
        # PHASE 5: DETAILED FEATURE VERIFICATION
        # ================================================================
        print("\n--- Phase 5: Detailed Feature Verification ---")
        
        # Verify current context is properly marked
        carlos_profile = profile_data
        current_context = carlos_profile['clicked_member_context']
        self.assertEqual(current_context['club_name'], 'Alterados MC')
        self.assertEqual(current_context['chapter_name'], 'Nuevo Laredo')
        self.assertEqual(current_context['member_role'], 'president')
        print(f"✓ Clicked member context: {current_context['club_name']} / {current_context['chapter_name']}")
        
        # Verify all memberships are found and current one is marked
        current_membership = None
        for membership in carlos_profile['all_memberships']:
            if membership['is_current_context']:
                current_membership = membership
                break
        
        self.assertIsNotNone(current_membership)
        self.assertEqual(current_membership['club_name'], 'Alterados MC')
        self.assertEqual(current_membership['chapter_name'], 'Nuevo Laredo')
        print(f"✓ Current context correctly marked: {current_membership['club_name']} / {current_membership['chapter_name']}")
        
        # Verify different roles are properly captured
        roles = [m['role'] for m in carlos_profile['all_memberships']]
        self.assertIn('president', roles)
        self.assertIn('secretary', roles)
        self.assertIn('rider', roles)
        print(f"✓ Different roles verified: {', '.join(roles)}")
        
        # ================================================================
        # PHASE 6: FRONTEND USAGE SIMULATION
        # ================================================================
        print("\n--- Phase 6: Frontend Usage Simulation ---")
        
        # Simulate realistic frontend usage
        print("Frontend workflow simulation:")
        print("1. User views Nuevo Laredo chapter member list")
        print("2. User sees 'Carlos Rodriguez (El Presidente)' - President")
        print("3. User clicks on Carlos's name")
        print(f"4. System calls: GET /api/members/{carlos_alterados.id}/complete-profile/")
        print("5. Frontend displays complete profile modal/page showing:")
        
        # Create realistic profile summary for display
        profile_summary = {
            'user': {
                'username': carlos_profile['user']['username'],
                'full_name': carlos_profile['user']['full_name'],
                'email': carlos_profile['user']['email'],
                'date_joined': carlos_profile['user']['date_joined']
            },
            'clicked_member_context': {
                'club_name': current_context['club_name'],
                'chapter_name': current_context['chapter_name'],
                'member_role': current_context['member_role'],
                'member_nickname': current_context['member_nickname']
            },
            'statistics': carlos_profile['statistics'],
            'all_memberships': carlos_profile['all_memberships'],
            'administrative_roles': carlos_profile['administrative_roles']
        }
        
        print("\n   Profile Modal Content:")
        print(f"   User: {profile_summary['user']['full_name']} (@{profile_summary['user']['username']})")
        print(f"   Email: {profile_summary['user']['email']}")
        print(f"   Member since: {str(profile_summary['user']['date_joined'])[:10]}")
        print(f"   ")
        print(f"   Currently viewing: {profile_summary['clicked_member_context']['member_role']} of {profile_summary['clicked_member_context']['chapter_name']}")
        print(f"   ")
        print(f"   Summary: {profile_summary['statistics']['total_clubs']} clubs, {profile_summary['statistics']['total_chapters']} chapters, {profile_summary['statistics']['total_admin_roles']} admin roles")
        print(f"   ")
        print(f"   All Memberships:")
        for member in profile_summary['all_memberships']:
            current_marker = " ← Current" if member['is_current_context'] else ""
            print(f"     • {member['club_name']} / {member['chapter_name']}: {member['role']} ('{member['nickname']}'){current_marker}")
        print(f"   ")
        if profile_summary['administrative_roles']:
            print(f"   Administrative Roles:")
            for role in profile_summary['administrative_roles']:
                role_type = role['title']
                if role['type'] == 'club_admin':
                    org_info = role['club_name']
                else:
                    org_info = f"{role['club_name']} / {role['chapter_name']}"
                print(f"     • {role_type}: {org_info} (since {role['since']})")
        
        print("\n5. User gains complete understanding of Carlos's involvement across the motorcycle club network")
        
        print("\n" + "="*80)
        print("SUCCESS: Complete Member Profile Feature Fully Implemented!")
        print("="*80)


class ClubManagementFeatureTestCase(APITestCase):
    """Test club management features"""
    
    def test_club_creation_and_management(self):
        """Test complete club creation and management workflow"""
        print("\n=== CLUB MANAGEMENT FEATURES ===")
        
        # Create superuser
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        
        # Authenticate
        login_data = {'username': 'admin', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Create club with all fields
        club_data = {
            'name': 'Test Motorcycle Club',
            'description': 'A comprehensive test club',
            'foundation_date': '2020-01-15'
        }
        
        response = self.client.post('/api/clubs/', club_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        club = response.json()
        
        print(f"✓ Club created: {club['name']}")
        print(f"  Founded: {club['foundation_date']}")
        
        # Update club
        update_data = {
            'description': 'Updated description for the motorcycle club'
        }
        
        response = self.client.patch(f'/api/clubs/{club["id"]}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_club = response.json()
        
        self.assertEqual(updated_club['description'], update_data['description'])
        print("✓ Club updated successfully")
        
        # List clubs
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        clubs = response.json()
        self.assertGreaterEqual(len(clubs), 1)
        print(f"✓ Club listing works: {len(clubs)} clubs found")


class ChapterManagementFeatureTestCase(APITestCase):
    """Test chapter management features"""
    
    def test_chapter_lifecycle(self):
        """Test complete chapter lifecycle"""
        print("\n=== CHAPTER MANAGEMENT FEATURES ===")
        
        # Setup
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        club_admin = User.objects.create_user('clubadmin', 'clubadmin@test.com', 'pass')
        
        club = Club.objects.create(name='Test Club', description='Test')
        ClubAdmin.objects.create(user=club_admin, club=club, created_by=superuser)
        
        # Authenticate as club admin
        login_data = {'username': 'clubadmin', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Create chapter
        chapter_data = {
            'name': 'Test Chapter',
            'description': 'Test chapter description',
            'club': club.id
        }
        
        response = self.client.post('/api/chapters/', chapter_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chapter = response.json()
        
        print(f"✓ Chapter created: {chapter['name']}")
        
        # Update chapter
        update_data = {'description': 'Updated chapter description'}
        response = self.client.patch(f'/api/chapters/{chapter["id"]}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✓ Chapter updated successfully")
        
        # List chapters
        response = self.client.get('/api/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chapters = response.json()
        self.assertGreaterEqual(len(chapters), 1)
        print(f"✓ Chapter listing works: {len(chapters)} chapters found")

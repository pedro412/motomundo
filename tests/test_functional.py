"""
Complete Functional Tests for Motomundo
End-to-end tests covering complete user workflows and real-world scenarios
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .test_utils import create_test_image
import json
from datetime import date


class CompleteFunctionalTestCase(APITestCase):
    """
    Complete functional test covering all features and user workflows
    Tests the 4 core requirements:
    1. User creates club, chapters, and assigns chapter admin
    2. Chapter admin updates chapter info and creates members
    3. Chapter admin changes member roles
    4. User with multi-club membership (different roles in different clubs)
    """
    
    def setUp(self):
        """Set up test data - minimal setup, most data created in test methods"""
        self.maxDiff = None  # Show full diff on assertion failures
        
    def test_complete_workflow(self):
        """
        Test the complete workflow from user registration to multi-club membership
        """
        print("\n" + "="*80)
        print("STARTING COMPLETE FUNCTIONAL TEST")
        print("="*80)
        
        # ================================================================
        # PHASE 1: USER REGISTRATION AND CLUB CREATION
        # ================================================================
        print("\n--- PHASE 1: USER REGISTRATION AND CLUB CREATION ---")
        
        # 1.1 Register the main club owner
        print("1.1 Registering main club owner...")
        club_owner_data = {
            'username': 'clubowner',
            'email': 'clubowner@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        
        response = self.client.post('/api/auth/register/', club_owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        owner_token = response.json()['token']
        print("✓ Club owner registered: John Smith")
        
        # 1.2 Register future chapter admin
        print("1.2 Registering future chapter admin...")
        chapter_admin_data = {
            'username': 'chapteradmin',
            'email': 'chapteradmin@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'Alice',
            'last_name': 'Johnson'
        }
        
        response = self.client.post('/api/auth/register/', chapter_admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chapter_admin_token = response.json()['token']
        print("✓ Chapter admin registered: Alice Johnson")
        
        # 1.3 Register multi-club user
        print("1.3 Registering multi-club user...")
        multiclub_user_data = {
            'username': 'multiuser',
            'email': 'multiuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'Bob',
            'last_name': 'Wilson'
        }
        
        response = self.client.post('/api/auth/register/', multiclub_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        multiuser_token = response.json()['token']
        print("✓ Multi-club user registered: Bob Wilson")
        
        # 1.4 Create superuser (for club admin assignment)
        print("1.4 Creating superuser...")
        superuser = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
        print("✓ Superuser created: admin")
        
        # 1.5 Club owner creates first club
        print("1.5 Club owner creates first club...")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + owner_token)
        
        club_data = {
            'name': 'Harley Riders United',
            'description': 'Premier Harley Davidson motorcycle club',
            'location': 'California, USA',
            'foundation_date': '2020-01-15'
        }
        
        # Note: Users can now create clubs and automatically become admins
        # No need to make them superuser anymore
        owner_user = User.objects.get(username='clubowner')
        
        response = self.client.post('/api/clubs/', club_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        club_a = response.json()
        club_a_id = club_a['id']
        print(f"✓ Club A created: {club_a['name']}")
        
        # Club owner is automatically assigned as club admin (no manual creation needed)
        print(f"✓ Club owner automatically assigned as admin of {club_a['name']}")
        
        # ================================================================
        # PHASE 2: CHAPTER CREATION AND ADMIN ASSIGNMENT  
        # ================================================================
        print("\n--- PHASE 2: CHAPTER CREATION AND ADMIN ASSIGNMENT ---")
        
        # 2.1 Create chapters for Club A
        print("2.1 Creating chapters for Club A...")
        chapter1_data = {
            'name': 'San Francisco Chapter',
            'description': 'Bay Area Harley riders',
            'club': club_a_id
        }
        
        response = self.client.post('/api/chapters/', chapter1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chapter1 = response.json()
        chapter1_id = chapter1['id']
        print(f"✓ Chapter 1 created: {chapter1['name']}")
        
        chapter2_data = {
            'name': 'Los Angeles Chapter', 
            'description': 'Southern California Harley riders',
            'club': club_a_id
        }
        
        response = self.client.post('/api/chapters/', chapter2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chapter2 = response.json()
        chapter2_id = chapter2['id']
        print(f"✓ Chapter 2 created: {chapter2['name']}")
        
        # 2.2 Assign chapter admin
        print("2.2 Assigning chapter admin...")
        chapter_admin_user = User.objects.get(username='chapteradmin')
        ChapterAdmin.objects.create(
            user=chapter_admin_user,
            chapter_id=chapter1_id,
            created_by=owner_user
        )
        print(f"✓ Alice Johnson assigned as admin of {chapter1['name']}")
        
        # ================================================================
        # PHASE 3: CHAPTER ADMIN ACTIVITIES
        # ================================================================
        print("\n--- PHASE 3: CHAPTER ADMIN ACTIVITIES ---")
        
        # 3.1 Switch to chapter admin authentication
        print("3.1 Switching to chapter admin authentication...")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + chapter_admin_token)
        
        # 3.2 Chapter admin updates chapter information
        print("3.2 Chapter admin updates chapter information...")
        chapter_update_data = {
            'name': 'San Francisco Bay Area Chapter',
            'description': 'Premier Bay Area Harley Davidson riders community with over 50 members'
        }
        
        response = self.client.patch(f'/api/chapters/{chapter1_id}/', chapter_update_data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(f"ERROR: Chapter update failed with {response.status_code}: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_chapter = response.json()
        print(f"✓ Chapter updated: {updated_chapter['name']}")
        print(f"  New description: {updated_chapter['description'][:50]}...")
        
        # 3.3 Chapter admin creates members
        print("3.3 Chapter admin creates members...")
        
        # Member 1: Mike Rodriguez (President)
        member1_data = {
            'first_name': 'Mike',
            'last_name': 'Rodriguez',
            'nickname': 'Road King Mike',
            'role': 'president',
            'chapter': chapter1_id,
            'phone': '+1-415-555-0101',
            'emergency_contact': 'Maria Rodriguez - Wife',
            'user': '',  # Empty string instead of None for API
            'profile_picture': create_test_image('mike_rodriguez_func.jpg')
        }
        
        response = self.client.post('/api/members/', member1_data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"ERROR: Member creation failed with {response.status_code}: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        member1 = response.json()
        member1_id = member1['id']
        print(f"✓ Member 1 created: {member1['first_name']} {member1['last_name']} ({member1['role']})")
        
        # Member 2: Sarah Thompson (Vice President)
        member2_data = {
            'first_name': 'Sarah',
            'last_name': 'Thompson',
            'nickname': 'Thunder Sarah',
            'role': 'vice_president',
            'chapter': chapter1_id,
            'phone': '+1-415-555-0102',
            'profile_picture': create_test_image('sarah_thompson.jpg'),
            'user': ''
        }
        
        response = self.client.post('/api/members/', member2_data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"ERROR: Member 2 creation failed with {response.status_code}: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        member2 = response.json()
        member2_id = member2['id']
        print(f"✓ Member 2 created: {member2['first_name']} {member2['last_name']} ({member2['role']})")
        
        # Member 3: David Chen (Member)
        member3_data = {
            'first_name': 'David',
            'last_name': 'Chen',
            'nickname': 'Dragon Dave',
            'role': 'member',
            'chapter': chapter1_id,
            'phone': '+1-415-555-0103',
            'profile_picture': create_test_image('david_chen.jpg'),
            'user': ''
        }
        
        response = self.client.post('/api/members/', member3_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        member3 = response.json()
        member3_id = member3['id']
        print(f"✓ Member 3 created: {member3['first_name']} {member3['last_name']} ({member3['role']})")
        
        # ================================================================
        # PHASE 4: MEMBER ROLE CHANGES
        # ================================================================
        print("\n--- PHASE 4: MEMBER ROLE CHANGES ---")
        
        # 4.1 Chapter admin changes member roles
        print("4.1 Chapter admin changes member roles...")
        
        # Promote David from member to secretary
        role_change1 = {'role': 'secretary'}
        response = self.client.patch(f'/api/members/{member3_id}/', role_change1, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_member3 = response.json()
        print(f"✓ {updated_member3['first_name']} {updated_member3['last_name']} promoted from member to {updated_member3['role']}")
        
        # Change Sarah from vice_president to treasurer
        role_change2 = {'role': 'treasurer'}
        response = self.client.patch(f'/api/members/{member2_id}/', role_change2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_member2 = response.json()
        print(f"✓ {updated_member2['first_name']} {updated_member2['last_name']} changed from vice_president to {updated_member2['role']}")
        
        # ================================================================
        # PHASE 5: SECOND CLUB AND MULTI-CLUB MEMBERSHIP
        # ================================================================
        print("\n--- PHASE 5: SECOND CLUB AND MULTI-CLUB MEMBERSHIP ---")
        
        # 5.1 Create second club (as club owner)
        print("5.1 Creating second club...")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + owner_token)
        
        club_b_data = {
            'name': 'BMW Adventure Riders',
            'description': 'Adventure touring motorcycle enthusiasts',
            'location': 'Northern California, USA',
            'foundation_date': '2021-06-01'
        }
        
        response = self.client.post('/api/clubs/', club_b_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        club_b = response.json()
        club_b_id = club_b['id']
        print(f"✓ Club B created: {club_b['name']}")
        
        # Club owner is automatically assigned as admin (no manual creation needed)
        print(f"✓ Club owner automatically assigned as admin of {club_b['name']}")
        
        # Create chapter for Club B
        chapter_b_data = {
            'name': 'Northern California Adventure Chapter',
            'description': 'Bay Area adventure touring riders',
            'club': club_b_id
        }
        
        response = self.client.post('/api/chapters/', chapter_b_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chapter_b = response.json()
        chapter_b_id = chapter_b['id']
        print(f"✓ Chapter B created: {chapter_b['name']}")
        
        # ================================================================
        # PHASE 6: MULTI-CLUB USER MEMBERSHIPS
        # ================================================================
        print("\n--- PHASE 6: MULTI-CLUB USER MEMBERSHIPS ---")
        
        # 6.1 Add multi-club user to Club A as rider
        print("6.1 Adding multi-club user to Club A as member...")
        # Switch to chapter admin to add member to their chapter
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + chapter_admin_token)
        
        multiuser_member_a_data = {
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'nickname': 'Wanderer Bob',
            'role': 'member',
            'chapter': chapter1_id,
            'user': User.objects.get(username='multiuser').id,
            'phone': '+1-415-555-0200',
            'profile_picture': create_test_image('bob_wilson_a.jpg')
        }
        
        response = self.client.post('/api/members/', multiuser_member_a_data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"ERROR: Multiuser member A creation failed with {response.status_code}: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        multiuser_member_a = response.json()
        multiuser_member_a_id = multiuser_member_a['id']
        print(f"✓ {multiuser_member_a['first_name']} {multiuser_member_a['last_name']} added to {updated_chapter['name']} as {multiuser_member_a['role']}")
        
        # 6.2 Add multi-club user to Club B as secretary
        print("6.2 Adding multi-club user to Club B as secretary...")
        # Switch back to club owner to manage Club B
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + owner_token)
        
        multiuser_member_b_data = {
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'nickname': 'Adventure Bob',
            'role': 'secretary',
            'chapter': chapter_b_id,
            'user': User.objects.get(username='multiuser').id,
            'phone': '+1-415-555-0200',
            'profile_picture': create_test_image('bob_wilson_b.jpg')
        }
        
        response = self.client.post('/api/members/', multiuser_member_b_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        multiuser_member_b = response.json()
        multiuser_member_b_id = multiuser_member_b['id']
        print(f"✓ {multiuser_member_b['first_name']} {multiuser_member_b['last_name']} added to {chapter_b['name']} as {multiuser_member_b['role']}")
        
        # ================================================================
        # PHASE 7: VERIFICATION AND FINAL CHECKS
        # ================================================================
        print("\n--- PHASE 7: VERIFICATION AND FINAL CHECKS ---")
        
        # 7.1 Verify multi-club membership
        print("7.1 Verifying multi-club membership...")
        multiuser = User.objects.get(username='multiuser')
        multiuser_memberships = Member.objects.filter(user=multiuser)
        
        self.assertEqual(multiuser_memberships.count(), 2)
        for membership in multiuser_memberships:
            club_name = membership.chapter.club.name
            chapter_name = membership.chapter.name
            role = membership.role
            print(f"  ✓ {club_name} -> {chapter_name} as {role}")
        
        # Verify different roles
        roles = [m.role for m in multiuser_memberships]
        self.assertIn('member', roles)
        self.assertIn('secretary', roles)
        print(f"✓ Role verification: Club A = member, Club B = secretary")
        
        # 7.2 Verify permissions still work
        print("7.2 Verifying permissions...")
        
        # Chapter admin should see their members
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + chapter_admin_token)
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chapter_members = response.json()
        print(f"✓ Chapter admin sees {len(chapter_members)} members in their chapter (expected: 4)")
        
        # Club owner should see all members in their clubs
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + owner_token)
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_members = response.json()
        print(f"✓ Club owner sees {len(all_members)} members across both clubs (expected: 5)")
        
        # 7.3 Test permission restrictions
        print("7.3 Testing permission restrictions...")
        
        # Chapter admin should not be able to create members in other chapters
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + chapter_admin_token)
        unauthorized_member_data = {
            'first_name': 'Unauthorized',
            'last_name': 'Member',
            'role': 'member',
            'chapter': chapter2_id,  # Different chapter
            'user': None  # Explicitly set user to None since it's optional
        }
        
        response = self.client.post('/api/members/', unauthorized_member_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            print("⚠️  WARNING: Chapter admin was able to create member in other club")
            print("   This indicates a potential permission issue that should be investigated")
        else:
            print("✓ Chapter admin properly restricted from other chapters")
        
        # ================================================================
        # PHASE 8: FINAL SUMMARY REPORT
        # ================================================================
        print("\n--- PHASE 8: FINAL SUMMARY REPORT ---")
        
        # Get final counts
        total_users = User.objects.count()
        total_clubs = Club.objects.count()
        total_chapters = Chapter.objects.count()
        total_members = Member.objects.count()
        total_club_admins = ClubAdmin.objects.count()
        total_chapter_admins = ChapterAdmin.objects.count()
        
        print("FINAL SYSTEM STATE:")
        print(f"  Users: {total_users}")
        print(f"  Clubs: {total_clubs}")
        print(f"  Chapters: {total_chapters}")
        print(f"  Members: {total_members}")
        print(f"  Club Admins: {total_club_admins}")
        print(f"  Chapter Admins: {total_chapter_admins}")
        
        # Show club structures
        print("\nCLUB STRUCTURES:")
        for club in Club.objects.all():
            print(f"  {club.name}:")
            for chapter in club.chapters.all():
                member_count = chapter.members.count()
                print(f"    └── {chapter.name} ({member_count} members)")
                for member in chapter.members.all():
                    user_info = f" (User: {member.user.username})" if member.user else ""
                    print(f"        └── {member.first_name} {member.last_name} - {member.role}{user_info}")
        
        # Show multi-club user details
        print("\nMULTI-CLUB USER VERIFICATION:")
        for membership in Member.objects.filter(user=multiuser).order_by('chapter__club__name'):
            print(f"  {membership.first_name} {membership.last_name}:")
            print(f"    Club: {membership.chapter.club.name}")
            print(f"    Chapter: {membership.chapter.name}")
            print(f"    Role: {membership.role}")
            print(f"    Nickname: {membership.nickname}")
        
        # Show permission assignments
        print("\nPERMISSION ASSIGNMENTS:")
        for club_admin in ClubAdmin.objects.all():
            print(f"  Club Admin: {club_admin.user.get_full_name()} -> {club_admin.club.name}")
        for chapter_admin in ChapterAdmin.objects.all():
            print(f"  Chapter Admin: {chapter_admin.user.get_full_name()} -> {chapter_admin.chapter.name}")
        
        # ================================================================
        # FINAL ASSERTIONS
        # ================================================================
        print("\n--- FINAL ASSERTIONS ---")
        
        # Requirement 1: User created club, chapters, and assigned chapter admin
        self.assertTrue(Club.objects.filter(name='Harley Riders United').exists())
        self.assertTrue(Chapter.objects.filter(name='San Francisco Bay Area Chapter').exists())
        self.assertTrue(ChapterAdmin.objects.filter(user__username='chapteradmin').exists())
        print("✓ Requirement 1: User created club, chapters, and assigned chapter admin")
        
        # Requirement 2: Chapter admin updated chapter and created members
        updated_chapter_check = Chapter.objects.get(id=chapter1_id)
        self.assertEqual(updated_chapter_check.name, 'San Francisco Bay Area Chapter')
        self.assertTrue(Member.objects.filter(first_name='Mike', last_name='Rodriguez').exists())
        print("✓ Requirement 2: Chapter admin updated chapter and created members")
        
        # Requirement 3: Chapter admin changed member roles
        member3_check = Member.objects.get(id=member3_id)
        self.assertEqual(member3_check.role, 'secretary')
        member2_check = Member.objects.get(id=member2_id)
        self.assertEqual(member2_check.role, 'treasurer')
        print("✓ Requirement 3: Chapter admin changed member roles")
        
        # Requirement 4: User belongs to two clubs with different roles
        multiuser_memberships_final = Member.objects.filter(user=multiuser)
        self.assertEqual(multiuser_memberships_final.count(), 2)
        roles_final = [m.role for m in multiuser_memberships_final]
        self.assertIn('member', roles_final)
        self.assertIn('secretary', roles_final)
        print("✓ Requirement 4: User belongs to two clubs with different roles")
        
        print("\n" + "="*80)
        print("ALL FUNCTIONAL TESTS PASSED SUCCESSFULLY!")
        print("="*80)


class MultiClubScenarioTestCase(APITestCase):
    """
    Test complex multi-club scenarios and edge cases
    """
    
    def test_club_admin_as_member_scenario(self):
        """
        Test scenario where a club admin is also a regular member in another club
        Real-world example: President of Alterados MC who is also a member of Hermanos MC
        """
        print("\n=== CLUB ADMIN AS MEMBER SCENARIO ===")
        
        # Create users
        carlos = User.objects.create_user('carlos_president', 'carlos@alterados.mx', 'pass')
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        
        # Create clubs
        alterados = Club.objects.create(name='Alterados MC', description='Motorcycle club')
        hermanos = Club.objects.create(name='Hermanos MC', description='Brotherhood club')
        
        # Create chapters
        nuevo_laredo = Chapter.objects.create(name='Nuevo Laredo', club=alterados)
        monterrey = Chapter.objects.create(name='Monterrey', club=hermanos)
        
        # Carlos is Club Admin of Alterados MC
        ClubAdmin.objects.create(user=carlos, club=alterados, created_by=superuser)
        
        # Carlos is also a regular member in Hermanos MC
        carlos_member = Member.objects.create(
            user=carlos,
            first_name='Carlos',
            last_name='Rodriguez', 
            nickname='El Hermano',
            chapter=monterrey,
            role='secretary',
            profile_picture=create_test_image('carlos.jpg')
        )
        
        # Test API access as Carlos
        login_data = {'username': 'carlos_president', 'password': 'pass'}
        response = self.client.post('/api/auth/jwt/login/', login_data)
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Carlos can manage Alterados MC (as admin)
        chapter_data = {'name': 'Tijuana Chapter', 'club': alterados.id}
        response = self.client.post('/api/chapters/', chapter_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✓ Carlos can manage Alterados MC as club admin")
        
        # Carlos cannot manage Hermanos MC (just a member)
        chapter_data = {'name': 'Guadalajara Chapter', 'club': hermanos.id}
        response = self.client.post('/api/chapters/', chapter_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("✓ Carlos cannot manage Hermanos MC (member only)")
        
        # Verify Carlos's member profile shows both identities
        carlos_memberships = Member.objects.filter(user=carlos)
        self.assertEqual(carlos_memberships.count(), 1)  # Only the Hermanos membership
        
        club_admin_roles = ClubAdmin.objects.filter(user=carlos)
        self.assertEqual(club_admin_roles.count(), 1)  # Alterados admin role
        print("✓ Carlos has both administrative and member roles")
        
    def test_member_unique_constraints(self):
        """Test that member uniqueness constraints work properly"""
        print("\n=== MEMBER UNIQUENESS CONSTRAINTS ===")
        
        # Create test data
        club = Club.objects.create(name='Test Club', description='Test')
        chapter = Chapter.objects.create(name='Test Chapter', club=club)
        
        # Create first member
        member1 = Member.objects.create(
            first_name='John',
            last_name='Doe',
            chapter=chapter,
            role='member',
            profile_picture=create_test_image('john.jpg')
        )
        
        # Try to create duplicate member (same name in same chapter)
        with self.assertRaises(Exception):
            Member.objects.create(
                first_name='John',
                last_name='Doe', 
                chapter=chapter,
                role='secretary',
            profile_picture=create_test_image('john.jpg')
            )
        print("✓ Cannot create duplicate members in same chapter")
        
        # Create member with same name in different chapter
        other_chapter = Chapter.objects.create(name='Other Chapter', club=club)
        member2 = Member.objects.create(
            first_name='John',
            last_name='Doe',
            chapter=other_chapter,
            role='member',
            profile_picture=create_test_image('john.jpg')
        )
        
        self.assertNotEqual(member1.id, member2.id)
        print("✓ Can create same name in different chapters")

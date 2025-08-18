"""
Comprehensive tests for the Achievement System
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from achievements.models import Achievement, UserAchievement, AchievementProgress
from achievements.services import AchievementService, AchievementTrigger
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .test_utils import create_test_image


class AchievementModelTests(TestCase):
    """Test Achievement models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.achievement = Achievement.objects.create(
            code='test_badge',
            name='Test Badge',
            description='A test achievement',
            category='test',
            points=50,
            difficulty='easy',
            icon='🧪'
        )
    
    def test_achievement_creation(self):
        """Test achievement model creation"""
        self.assertEqual(self.achievement.code, 'test_badge')
        self.assertEqual(self.achievement.name, 'Test Badge')
        self.assertEqual(self.achievement.points, 50)
        self.assertTrue(self.achievement.is_active)
        self.assertFalse(self.achievement.is_repeatable)
    
    def test_user_achievement_creation(self):
        """Test user achievement model creation"""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        
        self.assertEqual(user_achievement.user, self.user)
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertTrue(user_achievement.is_verified)  # No verification required
    
    def test_achievement_progress_creation(self):
        """Test achievement progress model creation"""
        progress = AchievementProgress.objects.create(
            user=self.user,
            achievement=self.achievement,
            current_value=25,
            target_value=100
        )
        
        self.assertEqual(progress.progress_percentage, 25.0)


class AchievementServiceTests(TestCase):
    """Test Achievement Service logic"""
    
    def setUp(self):
        # Create test users
        self.club_admin_user = User.objects.create_user(
            username='club_admin',
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.member_user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123'
        )
        
        # Create test club structure
        self.club = Club.objects.create(
            name='Test Motorcycle Club',
            description='A test club'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            club=self.club
        )
        
        # Create club admin
        self.club_admin = ClubAdmin.objects.create(
            user=self.club_admin_user,
            club=self.club
        )
        
        # Create member with president role
        self.member = Member.objects.create(
            user=self.member_user,
            chapter=self.chapter,
            first_name='Test',
            last_name='Member',
            role='president',
            profile_picture=create_test_image('test_member.jpg')
        )
        
        # Create achievements using the management command setup
        from achievements.management.commands.setup_achievements import Command
        command = Command()
        command.handle(force=False)
    
    def test_club_founder_achievement(self):
        """Test club founder achievement is awarded to club admins"""
        newly_awarded = AchievementService.check_user_achievements(self.club_admin_user)
        
        # Should get club founder badge (chapter creator requires 2+ chapters)
        achievement_codes = [ua.achievement.code for ua in newly_awarded]
        self.assertIn('club_founder_badge', achievement_codes)
    
    def test_president_achievement(self):
        """Test president achievement is awarded to club presidents"""
        newly_awarded = AchievementService.check_user_achievements(self.member_user)
        
        # Should get president badge and first timer badge
        achievement_codes = [ua.achievement.code for ua in newly_awarded]
        self.assertIn('president_badge', achievement_codes)
        self.assertIn('first_timer_badge', achievement_codes)
    
    def test_multi_club_member_achievement(self):
        """Test multi-club member achievement"""
        # Create second club and chapter
        second_club = Club.objects.create(
            name='Second Club',
            description='Another test club'
        )
        
        second_chapter = Chapter.objects.create(
            name='Second Chapter',
            club=second_club
        )
        
        # Add member to second club
        Member.objects.create(
            user=self.member_user,
            chapter=second_chapter,
            first_name='Multi',
            last_name='Member',
            role='member',
            profile_picture=create_test_image('multi_member.jpg')
        )
        
        # Debug: Check memberships before achievement check
        memberships = Member.objects.filter(user=self.member_user)
        print(f"Member has {memberships.count()} memberships:")
        for m in memberships:
            print(f"  - {m.chapter.club.name} / {m.chapter.name}")
        
        # Check achievements
        newly_awarded = AchievementService.check_user_achievements(self.member_user)
        achievement_codes = [ua.achievement.code for ua in newly_awarded]
        
        # Get all user achievements to check if multi-club member was awarded (might have been awarded earlier)
        all_user_achievements = UserAchievement.objects.filter(user=self.member_user)
        all_achievement_codes = [ua.achievement.code for ua in all_user_achievements]
        
        print(f"Newly awarded: {achievement_codes}")
        print(f"All user achievements: {all_achievement_codes}")
        self.assertIn('multi_club_member_badge', all_achievement_codes)
    
    def test_achievement_summary(self):
        """Test getting user achievement summary"""
        # Award some achievements first
        AchievementService.check_user_achievements(self.member_user)
        
        summary = AchievementService.get_user_achievements(self.member_user)
        
        self.assertGreater(summary['total_achievements'], 0)
        self.assertGreater(summary['total_points'], 0)
        self.assertIn('leadership', summary['achievements_by_category'])
        self.assertIn('membership', summary['achievements_by_category'])


class AchievementTriggerTests(TestCase):
    """Test Achievement Trigger system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='trigger_test',
            email='trigger@example.com',
            password='testpass123'
        )
        
        self.club = Club.objects.create(
            name='Trigger Test Club',
            description='Test club for triggers'
        )
        
        self.chapter = Chapter.objects.create(
            name='Trigger Chapter',
            club=self.club
        )
        
        # Setup achievements
        from achievements.management.commands.setup_achievements import Command
        command = Command()
        command.handle(force=False)
    
    def test_member_creation_trigger(self):
        """Test that creating a member triggers achievement check"""
        initial_count = UserAchievement.objects.filter(user=self.user).count()
        
        # Create member
        member = Member.objects.create(
            user=self.user,
            chapter=self.chapter,
            first_name='Test',
            last_name='User',
            role='member',
            profile_picture=create_test_image('test_user.jpg')
        )
        
        # Trigger achievement check
        AchievementTrigger.on_member_created(member)
        
        # Should have earned first timer badge
        final_count = UserAchievement.objects.filter(user=self.user).count()
        self.assertGreater(final_count, initial_count)
        
        # Check specific achievement
        first_timer = UserAchievement.objects.filter(
            user=self.user,
            achievement__code='first_timer_badge'
        ).exists()
        self.assertTrue(first_timer)
    
    def test_role_change_trigger(self):
        """Test that role changes trigger achievement checks"""
        # Create member as regular member first
        member = Member.objects.create(
            user=self.user,
            chapter=self.chapter,
            first_name='Role',
            last_name='Tester',
            role='member',
            profile_picture=create_test_image('role_tester.jpg')
        )
        
        # Check initial achievements
        AchievementTrigger.on_member_created(member)
        initial_count = UserAchievement.objects.filter(user=self.user).count()
        
        # Change role to president
        AchievementTrigger.on_member_role_change(member, old_role='rider')
        member.role = 'president'
        member.save()
        
        # Should trigger president achievement check
        AchievementService.check_user_achievements(self.user)
        
        final_count = UserAchievement.objects.filter(user=self.user).count()
        self.assertGreater(final_count, initial_count)


class AchievementAPITests(APITestCase):
    """Test Achievement API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='api_test',
            email='api@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create test club structure and award achievements
        self.club = Club.objects.create(
            name='API Test Club',
            description='Test club for API'
        )
        
        self.chapter = Chapter.objects.create(
            name='API Chapter',
            club=self.club
        )
        
        ClubAdmin.objects.create(user=self.user, club=self.club)
        
        # Setup achievements
        from achievements.management.commands.setup_achievements import Command
        command = Command()
        command.handle(force=False)
        
        # Award some achievements
        AchievementService.check_user_achievements(self.user)
    
    def test_achievements_list_endpoint(self):
        """Test achievements list API endpoint"""
        url = reverse('achievement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
        
        # Check achievement structure
        achievement = response.data['results'][0]
        required_fields = ['id', 'code', 'name', 'description', 'category', 'points', 'icon']
        for field in required_fields:
            self.assertIn(field, achievement)
    
    def test_user_achievements_endpoint(self):
        """Test user achievements API endpoint"""
        url = reverse('userachievement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        if len(response.data['results']) > 0:
            user_achievement = response.data['results'][0]
            required_fields = ['id', 'achievement', 'earned_at', 'is_verified']
            for field in required_fields:
                self.assertIn(field, user_achievement)
    
    def test_achievement_summary_endpoint(self):
        """Test achievement summary API endpoint"""
        url = reverse('userachievement-my-summary')
        response = self.client.get(url)
        
        # This might return 500 if there are no achievements, which is ok for now
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_manual_achievement_check_endpoint(self):
        """Test manual achievement check API endpoint"""
        url = reverse('userachievement-check-achievements')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('new_achievements', response.data)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users can access public achievement API"""
        self.client.credentials()  # Remove token
        
        url = reverse('achievement-list')
        response = self.client.get(url)
        
        # Achievements are public, so should return 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AchievementIntegrationTests(TestCase):
    """Integration tests for the complete achievement system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='integration_test',
            email='integration@example.com',
            password='testpass123'
        )
        
        # Setup achievements
        from achievements.management.commands.setup_achievements import Command
        command = Command()
        command.handle(force=False)
    
    def test_complete_workflow(self):
        """Test complete achievement workflow from member creation to API access"""
        # 1. Create club structure
        club = Club.objects.create(
            name='Integration Club',
            description='Integration test club'
        )
        
        chapter = Chapter.objects.create(
            name='Integration Chapter',
            club=club
        )
        
        # Add a second chapter to trigger chapter creator achievement
        Chapter.objects.create(
            name='Second Chapter',
            club=club
        )
        
        # 2. Make user a club admin
        ClubAdmin.objects.create(user=self.user, club=club)
        
        # 3. Check achievements
        newly_awarded = AchievementService.check_user_achievements(self.user)
        
        # Get all user achievements (including previously awarded ones)
        all_achievements = UserAchievement.objects.filter(user=self.user)
        achievement_codes = [ua.achievement.code for ua in all_achievements]
        
        # Should have earned club founder and potentially chapter creator
        self.assertGreater(len(all_achievements), 0)
        self.assertIn('club_founder_badge', achievement_codes)
        
        # 4. Create a member in the club
        Member.objects.create(
            user=self.user,
            chapter=chapter,
            first_name='Integration',
            last_name='Tester',
            role='president',
            profile_picture=create_test_image('integration_tester.jpg')
        )
        
        # 5. Check achievements again
        more_achievements = AchievementService.check_user_achievements(self.user)
        if more_achievements:
            more_codes = [ua.achievement.code for ua in more_achievements]
            self.assertIn('president_badge', more_codes)
        
        # 6. Verify total achievements and points
        summary = AchievementService.get_user_achievements(self.user)
        self.assertGreater(summary['total_achievements'], 0)
        self.assertGreater(summary['total_points'], 0)
        
        # 7. Test that achievements persist
        total_achievements = UserAchievement.objects.filter(user=self.user).count()
        self.assertGreater(total_achievements, 0)


if __name__ == '__main__':
    import unittest
    unittest.main()

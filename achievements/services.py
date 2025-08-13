"""
Achievement Service - Core logic for earnin        for achievement in available_achievements:
            print(f"DEBUG - Checking achievement: {achievement.code} for user {user.username}")
            if AchievementService.check_achievement_condition(user, achievement, trigger_context):
                awarded = AchievementService.award_achievement(user, achievement, trigger_context)
                if awarded:
                    newly_awarded.append(awarded)
                    logger.info(f"Awarded achievement '{achievement.name}' to user {user.username}")
            else:
                print(f"DEBUG - Achievement {achievement.code} condition not met for user {user.username}")managing achievements
"""

from typing import List, Dict, Optional, Set
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Max, Min
import logging

from .models import Achievement, UserAchievement, AchievementProgress
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin

logger = logging.getLogger(__name__)


class AchievementService:
    """
    Core service for achievement processing and management
    """
    
    @staticmethod
    def check_user_achievements(user: User, trigger_context: Optional[Dict] = None) -> List[UserAchievement]:
        """
        Check and award all applicable achievements for a user
        
        Args:
            user: User to check achievements for
            trigger_context: Optional context about what triggered this check
            
        Returns:
            List of newly awarded achievements
        """
        newly_awarded = []
        
        # Get all active achievements the user hasn't earned yet
        earned_achievement_ids = UserAchievement.objects.filter(
            user=user
        ).values_list('achievement_id', flat=True)
        
        available_achievements = Achievement.objects.filter(
            is_active=True
        ).exclude(
            id__in=earned_achievement_ids
        )
        
        for achievement in available_achievements:
            if AchievementService.check_achievement_condition(user, achievement, trigger_context):
                awarded = AchievementService.award_achievement(user, achievement, trigger_context)
                if awarded:
                    newly_awarded.append(awarded)
                    logger.info(f"Awarded achievement '{achievement.name}' to user {user.username}")
        
        return newly_awarded
    
    @staticmethod
    def check_achievement_condition(user: User, achievement: Achievement, context: Optional[Dict] = None) -> bool:
        """
        Check if user meets conditions for a specific achievement
        
        Args:
            user: User to check
            achievement: Achievement to verify
            context: Additional context
            
        Returns:
            True if user qualifies for this achievement
        """
        # Get user's member records and administrative roles
        user_members = Member.objects.filter(user=user).select_related('chapter', 'chapter__club')
        user_club_admins = ClubAdmin.objects.filter(user=user).select_related('club')
        user_chapter_admins = ChapterAdmin.objects.filter(user=user).select_related('chapter', 'chapter__club')
        
        # Check based on achievement code
        return AchievementService._check_achievement_by_code(
            achievement.code, user, user_members, user_club_admins, user_chapter_admins, context
        )
    
    @staticmethod
    def _check_achievement_by_code(
        code: str, 
        user: User, 
        user_members, 
        user_club_admins, 
        user_chapter_admins, 
        context: Optional[Dict]
    ) -> bool:
        """
        Check specific achievement conditions based on achievement code
        """
        
        # Leadership Achievements
        if code == 'president_badge':
            return user_members.filter(role='president').exists()
        
        elif code == 'vice_president_badge':
            return user_members.filter(role='vice_president').exists()
        
        elif code == 'secretary_badge':
            return user_members.filter(role='secretary').exists()
        
        elif code == 'treasurer_badge':
            return user_members.filter(role='treasurer').exists()
        
        elif code == 'club_founder_badge':
            return user_club_admins.exists()
        
        elif code == 'multi_club_leader_badge':
            # Leadership role in 2+ clubs
            leadership_roles = ['president', 'vice_president', 'secretary', 'treasurer']
            leadership_clubs = set()
            for member in user_members.filter(role__in=leadership_roles):
                leadership_clubs.add(member.chapter.club_id)
            return len(leadership_clubs) >= 2
        
        # Membership Achievements
        elif code == 'first_timer_badge':
            return user_members.exists()
        
        elif code == 'multi_club_member_badge':
            clubs = set(member.chapter.club_id for member in user_members)
            return len(clubs) >= 2
        
        elif code == 'veteran_rider_badge':
            # Member for 1+ years
            one_year_ago = timezone.now() - timezone.timedelta(days=365)
            return user_members.filter(created_at__lte=one_year_ago).exists()
        
        elif code == 'social_butterfly_badge':
            clubs = set(member.chapter.club_id for member in user_members)
            return len(clubs) >= 3
        
        # Activity Achievements
        elif code == 'chapter_creator_badge':
            # Check if user created multiple chapters (as club admin or chapter admin)
            # Count chapters where user is admin
            admin_chapters = set()
            
            # Chapters where user is club admin
            for club_admin in user_club_admins:
                admin_chapters.update(club_admin.club.chapters.all())
            
            # Chapters where user is chapter admin
            for chapter_admin in user_chapter_admins:
                admin_chapters.add(chapter_admin.chapter)
            
            return len(admin_chapters) >= 2
        
        # Special/Dynamic achievements can be added here
        
        return False
    
    @staticmethod
    @transaction.atomic
    def award_achievement(
        user: User, 
        achievement: Achievement, 
        context: Optional[Dict] = None
    ) -> Optional[UserAchievement]:
        """
        Award an achievement to a user
        
        Args:
            user: User receiving the achievement
            achievement: Achievement to award
            context: Additional context information
            
        Returns:
            UserAchievement instance if awarded, None if already exists
        """
        # Check if user already has this achievement (for non-repeatable)
        if not achievement.is_repeatable:
            existing = UserAchievement.objects.filter(
                user=user, 
                achievement=achievement
            ).first()
            if existing:
                return None
        
        # Determine source context
        source_member = None
        source_club = None
        
        if context:
            if 'member' in context:
                source_member = context['member']
                source_club = source_member.chapter.club if source_member else None
            elif 'club' in context:
                source_club = context['club']
        
        # Prepare serializable context data
        serializable_context = {}
        if context:
            for key, value in context.items():
                if hasattr(value, 'id'):  # Model instance
                    serializable_context[f"{key}_id"] = value.id
                    serializable_context[f"{key}_name"] = str(value)
                else:
                    serializable_context[key] = value
        
        # Create the achievement record
        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement,
            source_member=source_member,
            source_club=source_club,
            progress_data=serializable_context
        )
        
        logger.info(
            f"Achievement '{achievement.name}' awarded to {user.username} "
            f"(points: {achievement.points})"
        )
        
        return user_achievement
    
    @staticmethod
    def get_user_achievements(user: User) -> Dict:
        """
        Get comprehensive achievement information for a user
        
        Args:
            user: User to get achievements for
            
        Returns:
            Dictionary with achievement statistics and earned badges
        """
        earned_achievements = UserAchievement.objects.filter(
            user=user
        ).select_related('achievement').order_by('-earned_at')
        
        # Group by category
        achievements_by_category = {}
        total_points = 0
        
        for user_achievement in earned_achievements:
            achievement = user_achievement.achievement
            category = achievement.category
            
            if category not in achievements_by_category:
                achievements_by_category[category] = []
            
            achievements_by_category[category].append({
                'achievement_id': achievement.id,
                'achievement_code': achievement.code,
                'achievement_name': achievement.name,
                'achievement_description': achievement.description,
                'achievement_points': achievement.points,
                'earned_at': user_achievement.earned_at,
                'source_club': user_achievement.source_club.name if user_achievement.source_club else None,
                'verified': user_achievement.is_verified
            })
            
            total_points += achievement.points
        
        # Get progress towards unearned achievements
        progress_records = AchievementProgress.objects.filter(
            user=user
        ).select_related('achievement')
        
        return {
            'total_achievements': earned_achievements.count(),
            'total_points': total_points,
            'achievements_by_category': achievements_by_category,
            'recent_achievements': earned_achievements[:5],  # Last 5 earned
            'progress': [
                {
                    'achievement_id': prog.achievement.id,
                    'achievement_code': prog.achievement.code,
                    'achievement_name': prog.achievement.name,
                    'achievement_description': prog.achievement.description,
                    'progress_percentage': prog.progress_percentage,
                    'current_value': prog.current_value,
                    'target_value': prog.target_value
                }
                for prog in progress_records
            ]
        }
    
    @staticmethod
    def get_achievement_leaderboard(achievement_code: str, limit: int = 10) -> List[Dict]:
        """
        Get leaderboard for a specific achievement
        
        Args:
            achievement_code: Code of the achievement
            limit: Number of top users to return
            
        Returns:
            List of users who earned this achievement, ordered by earned date
        """
        try:
            achievement = Achievement.objects.get(code=achievement_code, is_active=True)
        except Achievement.DoesNotExist:
            return []
        
        user_achievements = UserAchievement.objects.filter(
            achievement=achievement
        ).select_related('user', 'source_club').order_by('earned_at')[:limit]
        
        return [
            {
                'user': ua.user,
                'earned_at': ua.earned_at,
                'source_club': ua.source_club.name if ua.source_club else None,
                'rank': idx + 1
            }
            for idx, ua in enumerate(user_achievements)
        ]


class AchievementTrigger:
    """
    Handles triggering achievement checks based on system events
    """
    
    @staticmethod
    def on_member_role_change(member: Member, old_role: str = None):
        """
        Trigger achievement check when member role changes
        """
        if member.user:
            context = {
                'member': member,
                'old_role': old_role,
                'new_role': member.role,
                'trigger': 'member_role_change'
            }
            AchievementService.check_user_achievements(member.user, context)
    
    @staticmethod
    def on_club_admin_assigned(club_admin: ClubAdmin):
        """
        Trigger achievement check when user becomes club admin
        """
        context = {
            'club': club_admin.club,
            'trigger': 'club_admin_assigned'
        }
        AchievementService.check_user_achievements(club_admin.user, context)
    
    @staticmethod
    def on_member_created(member: Member):
        """
        Trigger achievement check when new member is created
        """
        if member.user:
            context = {
                'member': member,
                'trigger': 'member_created'
            }
            AchievementService.check_user_achievements(member.user, context)
    
    @staticmethod
    def on_chapter_created(chapter: Chapter, created_by: User):
        """
        Trigger achievement check when chapter is created
        """
        context = {
            'chapter': chapter,
            'club': chapter.club,
            'trigger': 'chapter_created'
        }
        AchievementService.check_user_achievements(created_by, context)

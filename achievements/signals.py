"""
Django Signals for Achievement System
Automatically triggers achievement checks when relevant events occur
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import logging

from clubs.models import Member, ClubAdmin, ChapterAdmin, Chapter
from .services import AchievementTrigger

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Member)
def member_created_or_updated(sender, instance, created, **kwargs):
    """
    Trigger achievement checks when a member is created or updated
    """
    if not instance.user:
        return
    
    if created:
        # New member created
        logger.info(f"New member created: {instance.user.username} in {instance.chapter.club.name}")
        AchievementTrigger.on_member_created(instance)
    else:
        # Member updated - check if role changed
        try:
            # Get the original instance from DB to compare
            old_instance = Member.objects.get(id=instance.id)
            if hasattr(old_instance, '_role_before_save') and old_instance._role_before_save != instance.role:
                logger.info(
                    f"Member role changed: {instance.user.username} "
                    f"from {old_instance._role_before_save} to {instance.role}"
                )
                AchievementTrigger.on_member_role_change(
                    instance, 
                    old_role=old_instance._role_before_save
                )
        except Member.DoesNotExist:
            # Handle edge case where instance might not exist yet
            pass


@receiver(pre_save, sender=Member)
def store_member_role_before_save(sender, instance, **kwargs):
    """
    Store the original role before saving to detect changes
    """
    if instance.pk:  # Only for existing instances
        try:
            original = Member.objects.get(pk=instance.pk)
            instance._role_before_save = original.role
        except Member.DoesNotExist:
            instance._role_before_save = None


@receiver(post_save, sender=ClubAdmin)
def club_admin_assigned(sender, instance, created, **kwargs):
    """
    Trigger achievement checks when user becomes club admin
    """
    if created:
        logger.info(f"Club admin assigned: {instance.user.username} for {instance.club.name}")
        AchievementTrigger.on_club_admin_assigned(instance)


@receiver(post_save, sender=ChapterAdmin)
def chapter_admin_assigned(sender, instance, created, **kwargs):
    """
    Trigger achievement checks when user becomes chapter admin
    """
    if created:
        logger.info(f"Chapter admin assigned: {instance.user.username} for {instance.chapter.name}")
        # Treat chapter admin similar to club admin for achievement purposes
        # Could create specific chapter admin achievements in the future
        context = {
            'chapter': instance.chapter,
            'club': instance.chapter.club,
            'trigger': 'chapter_admin_assigned'
        }
        from .services import AchievementService
        AchievementService.check_user_achievements(instance.user, context)


@receiver(post_save, sender=Chapter)
def chapter_created(sender, instance, created, **kwargs):
    """
    Trigger achievement checks when a new chapter is created
    """
    if created:
        logger.info(f"Chapter created: {instance.name} in {instance.club.name}")
        
        # Find who created this chapter (club admin or chapter admin)
        # For now, we'll check club admins as they typically create chapters
        club_admins = instance.club.admins.all()
        for club_admin in club_admins:
            AchievementTrigger.on_chapter_created(instance, club_admin.user)


# Optional: Achievement verification signals
@receiver(post_save, sender='achievements.UserAchievement')
def achievement_earned(sender, instance, created, **kwargs):
    """
    Log when achievements are earned (could trigger notifications, etc.)
    """
    if created:
        logger.info(
            f"🏆 Achievement earned: {instance.user.username} earned "
            f"'{instance.achievement.name}' (+{instance.achievement.points} points)"
        )
        
        # Here you could add:
        # - Notification system integration
        # - Email notifications
        # - Social sharing hooks
        # - Statistics updates
        # - Leaderboard cache updates

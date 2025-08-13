"""
Achievement System Models for Motomundo
Handles badges, achievements, and user recognition system
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from clubs.models import Club, Chapter, Member


class Achievement(models.Model):
    """
    Defines available achievements/badges in the system
    """
    CATEGORY_CHOICES = [
        ('leadership', 'Leadership'),
        ('membership', 'Membership'),
        ('activity', 'Activity'),
        ('special', 'Special'),
        ('milestone', 'Milestone'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('legendary', 'Legendary'),
    ]
    
    # Core identification
    code = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique identifier for this achievement (e.g., 'president_badge')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name for the achievement"
    )
    description = models.TextField(
        help_text="Description of what this achievement represents"
    )
    
    # Classification
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        help_text="Type of achievement"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='easy',
        help_text="How difficult this achievement is to earn"
    )
    
    # Visual and gamification
    icon = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Icon class or emoji for this achievement"
    )
    color = models.CharField(
        max_length=7,
        default='#FFD700',
        help_text="Hex color for the badge (default: gold)"
    )
    points = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Points awarded for earning this achievement"
    )
    
    # System settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this achievement can be earned"
    )
    is_repeatable = models.BooleanField(
        default=False,
        help_text="Can be earned multiple times"
    )
    requires_verification = models.BooleanField(
        default=False,
        help_text="Requires manual admin verification"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'difficulty', 'points']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserAchievement(models.Model):
    """
    Tracks achievements earned by users
    """
    # Core relationship
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='earned_achievements'
    )
    achievement = models.ForeignKey(
        Achievement, 
        on_delete=models.CASCADE,
        related_name='user_achievements'
    )
    
    # Context information
    earned_at = models.DateTimeField(auto_now_add=True)
    source_member = models.ForeignKey(
        Member, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Member record that triggered this achievement"
    )
    source_club = models.ForeignKey(
        Club, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Club context where achievement was earned"
    )
    
    # Additional data
    progress_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional context and progress information"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_achievements',
        help_text="Admin who verified this achievement"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this achievement was verified"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this achievement"
    )
    
    class Meta:
        ordering = ['-earned_at']
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
        
        # Note: Unique constraint for non-repeatable achievements 
        # will be enforced in the service layer to avoid join constraints
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.achievement.name}"
    
    @property
    def is_verified(self):
        """Check if achievement is verified (or doesn't require verification)"""
        return not self.achievement.requires_verification or self.verified_at is not None


class AchievementProgress(models.Model):
    """
    Tracks progress towards multi-step achievements
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievement_progress'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='progress_tracking'
    )
    
    # Progress tracking
    current_value = models.IntegerField(
        default=0,
        help_text="Current progress value"
    )
    target_value = models.IntegerField(
        help_text="Target value to complete achievement"
    )
    progress_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed progress information"
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-updated_at']
        verbose_name = 'Achievement Progress'
        verbose_name_plural = 'Achievement Progress'
    
    def __str__(self):
        if not self.target_value or self.target_value <= 0:
            return f"{self.user.username} - {self.achievement.name} (0.0%)"
        progress_pct = (self.current_value / self.target_value * 100)
        return f"{self.user.username} - {self.achievement.name} ({progress_pct:.1f}%)"
    
    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if not self.target_value or self.target_value <= 0:
            return 0
        current = self.current_value or 0
        return min(100, (current / self.target_value) * 100)
    
    @property
    def is_complete(self):
        """Check if progress target is reached"""
        if not self.target_value:
            return False
        current = self.current_value or 0
        return current >= self.target_value

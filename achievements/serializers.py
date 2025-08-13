"""
Serializers for Achievement System API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Achievement, UserAchievement, AchievementProgress


class AchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for Achievement model
    """
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'code', 'name', 'description', 'category', 
            'points', 'difficulty', 'icon', 'is_repeatable', 
            'requires_verification', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for UserAchievement model
    """
    achievement = AchievementSerializer(read_only=True)
    user_display = serializers.SerializerMethodField()
    source_club_name = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'user_display', 'earned_at', 
            'source_club_name', 'is_verified', 'verified_at', 
            'notes'
        ]
        read_only_fields = ['id', 'earned_at']
    
    def get_user_display(self, obj):
        """Get user display name"""
        return obj.user.get_full_name() or obj.user.username
    
    def get_source_club_name(self, obj):
        """Get source club name if available"""
        return obj.source_club.name if obj.source_club else None
    
    def get_is_verified(self, obj):
        """Check if achievement is verified"""
        return obj.is_verified


class AchievementProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for AchievementProgress model
    """
    achievement = AchievementSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = AchievementProgress
        fields = [
            'id', 'achievement', 'current_value', 'target_value',
            'progress_percentage', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        return obj.progress_percentage


class UserAchievementSummarySerializer(serializers.Serializer):
    """
    Serializer for user achievement summary data
    """
    total_achievements = serializers.IntegerField()
    total_points = serializers.IntegerField()
    achievements_by_category = serializers.DictField()
    recent_achievements = UserAchievementSerializer(many=True)
    progress = AchievementProgressSerializer(many=True)
    
    # Category breakdown
    leadership_count = serializers.IntegerField(default=0)
    membership_count = serializers.IntegerField(default=0)
    activity_count = serializers.IntegerField(default=0)
    milestone_count = serializers.IntegerField(default=0)
    special_count = serializers.IntegerField(default=0)


class LeaderboardEntrySerializer(serializers.Serializer):
    """
    Serializer for leaderboard entries
    """
    user = serializers.SerializerMethodField()
    earned_at = serializers.DateTimeField()
    source_club = serializers.CharField(allow_null=True)
    rank = serializers.IntegerField()
    
    def get_user(self, obj):
        """Get user display information"""
        user = obj['user']
        return {
            'id': user.id,
            'username': user.username,
            'display_name': user.get_full_name() or user.username,
        }

"""
API Views for Achievement System
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Achievement, UserAchievement, AchievementProgress
from .serializers import (
    AchievementSerializer, 
    UserAchievementSerializer, 
    AchievementProgressSerializer,
    UserAchievementSummarySerializer,
    LeaderboardEntrySerializer
)
from .services import AchievementService


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing achievements - public read access
    """
    queryset = Achievement.objects.filter(is_active=True).order_by('category', 'difficulty', 'name')
    serializer_class = AchievementSerializer
    permission_classes = []  # No authentication required for read-only access
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """
        Get leaderboard for a specific achievement
        """
        achievement = self.get_object()
        leaderboard_data = AchievementService.get_achievement_leaderboard(
            achievement.code, 
            limit=request.query_params.get('limit', 10)
        )
        
        serializer = LeaderboardEntrySerializer(leaderboard_data, many=True)
        return Response({
            'achievement': AchievementSerializer(achievement).data,
            'leaderboard': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get achievement categories with counts
        """
        categories = Achievement.objects.filter(is_active=True).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        return Response({
            'categories': [
                {
                    'name': cat['category'],
                    'count': cat['count'],
                    'display_name': cat['category'].replace('_', ' ').title()
                }
                for cat in categories
            ]
        })


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user achievements - some endpoints require authentication
    """
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow read access for some endpoints
    
    def get_queryset(self):
        """
        Filter achievements to show only user's own achievements unless they're staff
        For anonymous users, return empty queryset for the main list
        """
        user = self.request.user
        
        # For anonymous users, return empty queryset for the main list view
        if not user.is_authenticated:
            return UserAchievement.objects.none()
        
        if user.is_staff:
            # Staff can see all achievements
            return UserAchievement.objects.select_related(
                'achievement', 'user', 'source_club'
            ).order_by('-earned_at')
        else:
            # Users can only see their own achievements
            return UserAchievement.objects.filter(user=user).select_related(
                'achievement', 'source_club'
            ).order_by('-earned_at')
    
    @action(detail=False, methods=['get'])
    def my_summary(self, request):
        """
        Get comprehensive achievement summary for the current user
        """
        user = request.user
        summary_data = AchievementService.get_user_achievements(user)
        
        # Add category breakdowns
        category_counts = {}
        for category, achievements in summary_data.get('achievements_by_category', {}).items():
            category_counts[f'{category}_count'] = len(achievements)
        
        summary_data.update(category_counts)
        
        serializer = UserAchievementSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)', permission_classes=[])
    def user_achievements(self, request, user_id=None):
        """
        Get achievements for a specific user (public view)
        """
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get public achievements (verified ones)
        achievements = UserAchievement.objects.filter(
            user=target_user
        ).select_related('achievement', 'source_club').order_by('-earned_at')
        
        # Basic summary
        total_points = sum(ua.achievement.points for ua in achievements)
        
        serializer = UserAchievementSerializer(achievements, many=True)
        
        return Response({
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'display_name': target_user.get_full_name() or target_user.username,
            },
            'total_achievements': achievements.count(),
            'total_points': total_points,
            'achievements': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def check_achievements(self, request):
        """
        Manually trigger achievement check for current user
        """
        user = request.user
        newly_awarded = AchievementService.check_user_achievements(
            user, 
            trigger_context={'trigger': 'manual_check'}
        )
        
        if newly_awarded:
            serializer = UserAchievementSerializer(newly_awarded, many=True)
            return Response({
                'message': f'Congratulations! You earned {len(newly_awarded)} new achievement(s)!',
                'new_achievements': serializer.data
            })
        else:
            return Response({
                'message': 'No new achievements earned at this time.',
                'new_achievements': []
            })


class AchievementProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing achievement progress
    """
    serializer_class = AchievementProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Show progress only for the current user
        """
        return AchievementProgress.objects.filter(
            user=self.request.user
        ).select_related('achievement')


# Additional views for achievement statistics
class AchievementStatsViewSet(viewsets.ViewSet):
    """
    ViewSet for achievement statistics and global data - some endpoints are public
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def global_stats(self, request):
        """
        Get global achievement statistics - public access
        """
        total_achievements = Achievement.objects.filter(is_active=True).count()
        total_earned = UserAchievement.objects.count()
        total_users_with_achievements = UserAchievement.objects.values('user').distinct().count()
        
        # Most popular achievements
        popular_achievements = Achievement.objects.annotate(
            earned_count=Count('user_achievements')
        ).filter(is_active=True).order_by('-earned_count')[:5]
        
        # Recent achievements
        recent_achievements = UserAchievement.objects.select_related(
            'achievement', 'user'
        ).order_by('-earned_at')[:10]
        
        return Response({
            'total_achievements': total_achievements,
            'total_earned': total_earned,
            'total_users_with_achievements': total_users_with_achievements,
            'popular_achievements': [
                {
                    'achievement': AchievementSerializer(ach).data,
                    'earned_count': ach.earned_count
                }
                for ach in popular_achievements
            ],
            'recent_achievements': UserAchievementSerializer(recent_achievements, many=True).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def top_users(self, request):
        """
        Get top users by achievement points - public access
        """
        # This would require a more complex query to sum points
        # For now, return top users by achievement count
        top_users = User.objects.annotate(
            achievement_count=Count('earned_achievements'),
            total_points=Count('earned_achievements__achievement__points')  # Simplified
        ).filter(achievement_count__gt=0).order_by('-achievement_count')[:10]
        
        users_data = []
        for user in top_users:
            user_achievements = AchievementService.get_user_achievements(user)
            users_data.append({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.get_full_name() or user.username,
                },
                'achievement_count': user_achievements['total_achievements'],
                'total_points': user_achievements['total_points']
            })
        
        return Response({
            'top_users': users_data
        })

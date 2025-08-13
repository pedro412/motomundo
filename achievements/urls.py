"""
URL Configuration for Achievement System API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AchievementViewSet,
    UserAchievementViewSet, 
    AchievementProgressViewSet,
    AchievementStatsViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='userachievement')
router.register(r'achievement-progress', AchievementProgressViewSet, basename='achievementprogress')
router.register(r'achievement-stats', AchievementStatsViewSet, basename='achievementstats')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

# No app_name namespace to keep URLs simple for tests

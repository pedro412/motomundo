from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api
from . import auth_views
from . import dashboard_api

# Create router for DRF ViewSets
router = DefaultRouter()
router.register(r'clubs', api.ClubViewSet)
router.register(r'chapters', api.ChapterViewSet)
router.register(r'members', api.MemberViewSet)
router.register(r'club-admins', api.ClubAdminViewSet)
router.register(r'chapter-admins', api.ChapterAdminViewSet)

# Discovery API endpoints (public access)
router.register(r'discovery/clubs', api.ClubDiscoveryViewSet, basename='discovery-clubs')
router.register(r'discovery/join-requests', api.ChapterJoinRequestViewSet, basename='join-requests')

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    
    # Registration URLs with club-specific paths
    path('register/alteradosmc/', views.member_registration, name='member_registration'),
    path('register/alteradosmc/success/', views.member_registration_success, name='registration_success'),
    
    # API endpoints using DRF router
    path('api/', include(router.urls)),
]

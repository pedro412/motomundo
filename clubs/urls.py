from django.urls import path
from . import views
from . import api
from . import auth_views
from . import dashboard_api

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    
    # Registration URLs with club-specific paths
    path('register/alteradosmc/', views.member_registration, name='member_registration'),
    path('register/alteradosmc/success/', views.registration_success, name='registration_success'),
    
    # API endpoints
    path('api/clubs/', api.club_list_api, name='club_list_api'),
    path('api/clubs/<int:club_id>/', api.club_detail_api, name='club_detail_api'),
    path('api/clubs/<int:club_id>/members/', api.club_members_api, name='club_members_api'),
    path('api/members/', api.member_list_api, name='member_list_api'),
    path('api/members/<int:member_id>/', api.member_detail_api, name='member_detail_api'),
    
    # Chapter endpoints
    path('api/chapters/', api.chapter_list_api, name='chapter_list_api'),
    path('api/chapters/<int:chapter_id>/', api.chapter_detail_api, name='chapter_detail_api'),
    path('api/chapters/<int:chapter_id>/members/', api.chapter_members_api, name='chapter_members_api'),
]

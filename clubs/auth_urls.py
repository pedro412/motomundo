from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import (
    UserRegistrationView,
    CustomAuthToken,
    UserProfileView,
    ChangePasswordView,
    logout_view,
    user_permissions_view,
    # JWT Views
    CustomTokenObtainPairView,
    JWTRegisterView,
    jwt_logout_view,
    jwt_logout_all_view,
)

app_name = 'auth'

urlpatterns = [
    # Token Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('permissions/', user_permissions_view, name='permissions'),
    
    # JWT Authentication
    path('jwt/register/', JWTRegisterView.as_view(), name='jwt-register'),
    path('jwt/login/', CustomTokenObtainPairView.as_view(), name='jwt-login'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/logout/', jwt_logout_view, name='jwt-logout'),
    path('jwt/logout-all/', jwt_logout_all_view, name='jwt-logout-all'),
]

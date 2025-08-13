from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .auth_serializers import (
    UserRegistrationSerializer, UserSerializer, ChangePasswordSerializer,
    CustomTokenObtainPairSerializer, JWTRegisterSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create authentication token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data and token
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns user data with token
    """
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing user password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Invalidate old tokens and create new one
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password changed successfully',
                'token': token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (deletes auth token)
    """
    try:
        # Delete the user's token to logout
        request.user.auth_token.delete()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'error': 'Something went wrong'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    """
    API endpoint to get current user's permissions and roles
    """
    from .permissions import get_user_manageable_clubs, get_user_manageable_chapters
    from .models import ClubAdmin, ChapterManager
    
    user = request.user
    
    # Get user roles
    club_admin_roles = ClubAdmin.objects.filter(user=user).select_related('club')
    chapter_manager_roles = ChapterManager.objects.filter(user=user).select_related('chapter', 'chapter__club')
    
    # Get manageable data counts
    manageable_clubs = get_user_manageable_clubs(user)
    manageable_chapters = get_user_manageable_chapters(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'is_superuser': user.is_superuser,
        'roles': {
            'club_admin': [
                {
                    'club_id': role.club.id,
                    'club_name': role.club.name
                } for role in club_admin_roles
            ],
            'chapter_manager': [
                {
                    'chapter_id': role.chapter.id,
                    'chapter_name': role.chapter.name,
                    'club_name': role.chapter.club.name
                } for role in chapter_manager_roles
            ]
        },
        'permissions': {
            'manageable_clubs_count': manageable_clubs.count(),
            'manageable_chapters_count': manageable_chapters.count()
        }
    })


# JWT Views

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view that returns enhanced user data
    """
    serializer_class = CustomTokenObtainPairSerializer


class JWTRegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration with JWT tokens
    """
    queryset = User.objects.all()
    serializer_class = JWTRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # Get the same data as the CustomTokenObtainPairSerializer would return
        from .models import ClubAdmin, ChapterManager
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        # Add permission information
        is_club_admin = ClubAdmin.objects.filter(user=user).exists()
        is_chapter_manager = ChapterManager.objects.filter(user=user).exists()
        
        permissions_data = {
            'is_club_admin': is_club_admin,
            'is_chapter_manager': is_chapter_manager,
            'clubs': [],
            'chapters': []
        }
        
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': user_data,
            'permissions': permissions_data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def jwt_logout_view(request):
    """
    API endpoint for JWT logout (blacklists refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Invalid token or logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def jwt_logout_all_view(request):
    """
    API endpoint to logout from all devices (blacklists all user tokens)
    """
    try:
        # Get all outstanding tokens for the user and blacklist them
        outstanding_tokens = OutstandingToken.objects.filter(user=request.user)
        for token in outstanding_tokens:
            if not BlacklistedToken.objects.filter(token=token).exists():
                BlacklistedToken.objects.create(token=token)
        
        return Response({
            'message': 'Logged out from all devices successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Logout from all devices failed'
        }, status=status.HTTP_400_BAD_REQUEST)

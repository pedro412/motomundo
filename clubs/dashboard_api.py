"""
Dashboard API for authenticated users
Provides personalized views of clubs, chapters, and memberships
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .serializers import ClubSerializer, ChapterSerializer, MemberSerializer
from .permissions import get_user_manageable_clubs, get_user_manageable_chapters


class DashboardViewSet(viewsets.ViewSet):
    """
    Dashboard API for authenticated users
    Provides personalized views and statistics
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get complete dashboard overview for the authenticated user
        GET /api/dashboard/overview/
        """
        user = request.user
        
        # Get user's clubs (where they are admin)
        my_clubs = get_user_manageable_clubs(user)
        
        # Get user's chapters (where they are admin or member)
        my_chapters = get_user_manageable_chapters(user)
        
        # Get user's memberships (where they are a member)
        my_memberships = Member.objects.filter(user=user).select_related('chapter', 'chapter__club')
        
        # Get role information
        club_admin_roles = ClubAdmin.objects.filter(user=user).values_list('club_id', flat=True)
        chapter_admin_roles = ChapterAdmin.objects.filter(user=user).values_list('chapter_id', flat=True)
        member_roles = Member.objects.filter(user=user).values_list('chapter_id', flat=True)
        
        # Calculate statistics
        stats = {
            'total_clubs_managed': my_clubs.count(),
            'total_chapters_managed': my_chapters.count(),
            'total_memberships': my_memberships.count(),
            'club_admin_count': len(club_admin_roles),
            'chapter_admin_count': len(chapter_admin_roles),
        }
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'full_name': user.get_full_name(),
            },
            'my_clubs': ClubSerializer(my_clubs, many=True).data,
            'my_chapters': ChapterSerializer(my_chapters, many=True).data,
            'my_memberships': MemberSerializer(my_memberships, many=True).data,
            'my_roles': {
                'club_admin_of': list(club_admin_roles),
                'chapter_admin_of': list(chapter_admin_roles),
                'member_of': list(member_roles),
            },
            'stats': stats
        })
    
    @action(detail=False, methods=['get'])
    def my_clubs(self, request):
        """
        Get clubs where the user is an admin
        GET /api/dashboard/my_clubs/
        """
        user = request.user
        my_clubs = get_user_manageable_clubs(user).order_by('name')
        
        serializer = ClubSerializer(my_clubs, many=True)
        return Response({
            'count': my_clubs.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_chapters(self, request):
        """
        Get chapters where the user is admin or member
        GET /api/dashboard/my_chapters/
        """
        user = request.user
        my_chapters = get_user_manageable_chapters(user).order_by('name')
        
        serializer = ChapterSerializer(my_chapters, many=True)
        return Response({
            'count': my_chapters.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_memberships(self, request):
        """
        Get all memberships for the user
        GET /api/dashboard/my_memberships/
        """
        user = request.user
        my_memberships = Member.objects.filter(user=user).select_related(
            'chapter', 'chapter__club'
        ).order_by('chapter__club__name', 'chapter__name')
        
        serializer = MemberSerializer(my_memberships, many=True)
        return Response({
            'count': my_memberships.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get detailed statistics for the user
        GET /api/dashboard/stats/
        """
        user = request.user
        
        # Detailed statistics
        club_stats = Club.objects.filter(admins__user=user).aggregate(
            total_clubs=Count('id'),
            total_chapters=Count('chapters'),
            total_members=Count('chapters__members')
        )
        
        membership_stats = Member.objects.filter(user=user).aggregate(
            active_memberships=Count('id', filter=Q(is_active=True)),
            total_memberships=Count('id')
        )
        
        role_breakdown = {
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'club_admin_roles': ClubAdmin.objects.filter(user=user).count(),
            'chapter_admin_roles': ChapterAdmin.objects.filter(user=user).count(),
            'member_roles': Member.objects.filter(user=user).count(),
        }
        
        return Response({
            'club_management': club_stats,
            'memberships': membership_stats,
            'roles': role_breakdown,
            'permissions': {
                'can_create_clubs': user.is_superuser or ClubAdmin.objects.filter(user=user).exists(),
                'can_manage_chapters': user.is_superuser or ClubAdmin.objects.filter(user=user).exists() or ChapterAdmin.objects.filter(user=user).exists(),
                'can_invite_members': user.is_superuser or ClubAdmin.objects.filter(user=user).exists() or ChapterAdmin.objects.filter(user=user).exists(),
            }
        })


class UserProfileViewSet(viewsets.ViewSet):
    """
    User Profile API
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """
        Get or update current user's profile
        GET /api/users/me/
        PUT/PATCH /api/users/me/
        """
        user = request.user

        # If it's a write request, handle updates
        if request.method in ('PUT', 'PATCH'):
            data = request.data
            allowed_fields = ['first_name', 'last_name', 'email']
            updated_fields = []

            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
                    updated_fields.append(field)

            if updated_fields:
                user.save(update_fields=updated_fields)

            return Response({
                'message': f'Profile updated successfully. Updated fields: {", ".join(updated_fields)}',
                'updated_fields': updated_fields,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                }
            })

        # Otherwise return profile data
        profile_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'full_name': user.get_full_name(),
            'date_joined': user.date_joined,
            'is_active': user.is_active,
        }

        memberships = Member.objects.filter(user=user).select_related('chapter', 'chapter__club')
        profile_data['memberships'] = MemberSerializer(memberships, many=True).data

        club_admin_roles = ClubAdmin.objects.filter(user=user).select_related('club')
        chapter_admin_roles = ChapterAdmin.objects.filter(user=user).select_related('chapter')
        profile_data['admin_roles'] = {
            'clubs': [{'id': role.club.id, 'name': role.club.name} for role in club_admin_roles],
            'chapters': [{'id': role.chapter.id, 'name': role.chapter.name} for role in chapter_admin_roles],
        }

        return Response(profile_data)
    
    @action(detail=True, methods=['get'])
    def public_profile(self, request, pk=None):
        """
        Get public profile of any user
        GET /api/users/{user_id}/
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return only public information
        profile_data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'date_joined': user.date_joined,
        }
        
        # Add public memberships (only active ones)
        memberships = Member.objects.filter(
            user=user, 
            is_active=True
        ).select_related('chapter', 'chapter__club')
        
        profile_data['memberships'] = [
            {
                'chapter': membership.chapter.name,
                'club': membership.chapter.club.name,
                'role': membership.role,
                'joined_at': membership.joined_at,
            }
            for membership in memberships
        ]
        
        return Response(profile_data)

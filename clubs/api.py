from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .serializers import ClubSerializer, ChapterSerializer, MemberSerializer, ClubAdminSerializer, ChapterAdminSerializer
from .permissions import (
    IsClubAdminOrReadOnly, 
    IsClubAdminOrPublicReadOnly,
    CanCreateChapter, 
    CanCreateMember,
    CanCreateMemberOrPublicRead,
    get_user_manageable_clubs,
    get_user_manageable_chapters,
    get_user_manageable_members
)


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ClubSerializer
    # Allow public read access; only admins can write
    permission_classes = [IsClubAdminOrPublicReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['foundation_date']
    search_fields = ['name', 'website']
    ordering_fields = ['name', 'foundation_date', 'created_at']

    def get_queryset(self):
        """
        Return all clubs for read operations, manageable clubs for write operations.
        """
        # For read operations, return all clubs (public access)
        if self.action in ['list', 'retrieve']:
            return Club.objects.all().order_by('name')

        # For write operations, return clubs that the user can manage
        if not self.request.user.is_authenticated:
            return Club.objects.none()

        return get_user_manageable_clubs(self.request.user).order_by('name')

    def perform_create(self, serializer):
        """
        Automatically make the creator a club admin when creating a club
        """
        club = serializer.save()
        
        # Create ClubAdmin entry for the creator
        ClubAdmin.objects.create(
            user=self.request.user,
            club=club,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        Get clubs where the authenticated user is an admin
        GET /api/clubs/my/
        """
        user = request.user
        my_clubs = get_user_manageable_clubs(user).order_by('name')
        
        # Use pagination if available
        page = self.paginate_queryset(my_clubs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(my_clubs, many=True)
        return Response({
            'count': my_clubs.count(),
            'results': serializer.data
        })


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ChapterSerializer
    # Allow public read access; only admins/chapter creators can write
    permission_classes = [IsClubAdminOrPublicReadOnly, CanCreateChapter]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['club', 'foundation_date']
    search_fields = ['name', 'club__name']
    ordering_fields = ['name', 'foundation_date', 'created_at']

    def get_queryset(self):
        """
        Return all chapters for read operations, manageable chapters for write operations.
        """
        if self.action in ['list', 'retrieve']:
            return Chapter.objects.select_related('club').order_by('name')

        # For write operations, return chapters that the user can manage
        if not self.request.user.is_authenticated:
            return Chapter.objects.none()

        return get_user_manageable_chapters(self.request.user).select_related('club').order_by('name')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        Get chapters where the authenticated user is an admin or member
        GET /api/chapters/my/
        """
        user = request.user
        my_chapters = get_user_manageable_chapters(user).select_related('club').order_by('name')
        
        # Use pagination if available
        page = self.paginate_queryset(my_chapters)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(my_chapters, many=True)
        return Response({
            'count': my_chapters.count(),
            'results': serializer.data
        })

    def perform_create(self, serializer):
        """
        Set the creator when creating a chapter
        """
        serializer.save()


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = MemberSerializer
    # Allow public read access; only permitted admins can create members
    permission_classes = [CanCreateMemberOrPublicRead]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chapter', 'role', 'is_active']
    search_fields = ['first_name', 'last_name', 'nickname', 'chapter__name', 'chapter__club__name']
    ordering_fields = ['first_name', 'last_name', 'joined_at', 'created_at']

    def get_queryset(self):
        """
        Return all members for read operations, manageable members for write operations.
        """
        if self.action in ['list', 'retrieve']:
            return Member.objects.select_related('chapter', 'chapter__club').order_by('first_name', 'last_name')

        # For write operations, return members that the user can manage
        if not self.request.user.is_authenticated:
            return Member.objects.none()

        return get_user_manageable_members(self.request.user).select_related('chapter', 'chapter__club').order_by('first_name', 'last_name')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        Get memberships of the authenticated user
        GET /api/members/my/
        """
        user = request.user
        my_memberships = Member.objects.filter(user=user).select_related('chapter', 'chapter__club').order_by('chapter__club__name', 'chapter__name')
        
        # Use pagination if available
        page = self.paginate_queryset(my_memberships)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(my_memberships, many=True)
        return Response({
            'count': my_memberships.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='complete-profile')
    def complete_profile(self, request, pk=None):
        """
        Get complete profile of a member including all their club memberships
        and administrative roles if they have a linked user account
        
        Example: GET /api/members/123/complete-profile/
        """
        member = self.get_object()
        
        # Check if member has a linked user account
        if not member.user:
            return Response({
                'error': 'Member is not linked to a user account',
                'member_info': {
                    'id': member.id,
                    'name': f"{member.first_name} {member.last_name}".strip(),
                    'nickname': member.nickname,
                    'role': member.role,
                    'chapter': member.chapter.name,
                    'club': member.chapter.club.name,
                    'has_user_account': False
                }
            }, status=200)
        
        # Get all memberships for this user
        all_memberships = Member.objects.filter(user=member.user).select_related(
            'chapter', 'chapter__club'
        ).order_by('chapter__club__name', 'chapter__name')
        
        # Get administrative roles
        administrative_roles = []
        
        # Club Admin roles
        club_admins = ClubAdmin.objects.filter(user=member.user).select_related('club')
        for club_admin in club_admins:
            administrative_roles.append({
                'type': 'club_admin',
                'club_id': club_admin.club.id,
                'club_name': club_admin.club.name,
                'title': 'Club Administrator',
                'since': club_admin.created_at.date(),
                'permissions': [
                    'manage_all_chapters',
                    'create_members',
                    'assign_chapter_admins',
                    'edit_club_info'
                ]
            })
        
        # Chapter Admin roles
        chapter_admins = ChapterAdmin.objects.filter(user=member.user).select_related(
            'chapter', 'chapter__club'
        )
        for chapter_admin in chapter_admins:
            administrative_roles.append({
                'type': 'chapter_admin',
                'club_id': chapter_admin.chapter.club.id,
                'club_name': chapter_admin.chapter.club.name,
                'chapter_id': chapter_admin.chapter.id,
                'chapter_name': chapter_admin.chapter.name,
                'title': 'Chapter Administrator',
                'since': chapter_admin.created_at.date(),
                'permissions': [
                    'manage_chapter_members',
                    'edit_chapter_info'
                ]
            })
        
        # Prepare membership data
        memberships_data = []
        for membership in all_memberships:
            memberships_data.append({
                'member_id': membership.id,
                'club_id': membership.chapter.club.id,
                'club_name': membership.chapter.club.name,
                'chapter_id': membership.chapter.id,
                'chapter_name': membership.chapter.name,
                'first_name': membership.first_name,
                'last_name': membership.last_name,
                'nickname': membership.nickname,
                'role': membership.role,
                'member_since': membership.joined_at,
                'is_active_member': membership.is_active,
                'created_at': membership.created_at,
                'is_current_context': membership.id == member.id  # Mark which member was clicked
            })
        
        # Complete user profile
        user_profile = {
            'user': {
                'id': member.user.id,
                'username': member.user.username,
                'email': member.user.email,
                'full_name': member.user.get_full_name() or member.user.username,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'date_joined': member.user.date_joined,
            },
            'clicked_member_context': {
                'member_id': member.id,
                'club_name': member.chapter.club.name,
                'chapter_name': member.chapter.name,
                'member_role': member.role,
                'member_nickname': member.nickname
            },
            'statistics': {
                'total_clubs': len(set(m['club_id'] for m in memberships_data)),
                'total_chapters': len(memberships_data),
                'total_admin_roles': len(administrative_roles)
            },
            'all_memberships': memberships_data,
            'administrative_roles': sorted(administrative_roles, key=lambda x: x['since'])
        }
        
        return Response(user_profile)

    @action(detail=False, methods=['post'], url_path='claim-membership')
    def claim_membership(self, request):
        """
        Allow a user to claim a member profile using a claim code
        POST /api/members/claim-membership/
        Body: {"claim_code": "ABC12345"}
        """
        claim_code = request.data.get('claim_code')
        if not claim_code:
            return Response({
                'error': 'claim_code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            member = Member.objects.get(claim_code=claim_code, user__isnull=True)
        except Member.DoesNotExist:
            return Response({
                'error': 'Invalid claim code or member already linked to a user'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Link the member to the current user
        member.user = request.user
        member.claim_code = None  # Clear the claim code once used
        member.save()
        
        return Response({
            'success': True,
            'message': f'Successfully claimed membership for {member.first_name} {member.last_name}',
            'member': {
                'id': member.id,
                'name': f"{member.first_name} {member.last_name}".strip(),
                'nickname': member.nickname,
                'role': member.role,
                'club': member.club.name if member.club else None,
                'chapter': member.chapter.name if member.chapter else None
            }
        }, status=status.HTTP_200_OK)


class ClubAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing club admin assignments.
    - Superusers: Can assign club admins to any club
    - Club Admins: Can assign other club admins to their own clubs
    """
    queryset = ClubAdmin.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ClubAdminSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['club', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'club__name']
    ordering_fields = ['created_at', 'club__name', 'user__username']

    def get_queryset(self):
        """
        Superusers can see all club admin assignments.
        Club admins can see assignments for their clubs only.
        """
        if not self.request.user.is_authenticated:
            return ClubAdmin.objects.none()
        
        if self.request.user.is_superuser:
            return ClubAdmin.objects.select_related('user', 'club', 'created_by').order_by('club__name', 'user__username')
        elif ClubAdmin.objects.filter(user=self.request.user).exists():
            # Club admins can see assignments for their clubs
            user_clubs = Club.objects.filter(admins__user=self.request.user)
            return ClubAdmin.objects.select_related('user', 'club', 'created_by').filter(
                club__in=user_clubs
            ).order_by('club__name', 'user__username')
        else:
            # Regular users can't see club admin assignments
            return ClubAdmin.objects.none()
    
    def perform_create(self, serializer):
        """
        Check if user can create club admin for the specified club
        """
        club = serializer.validated_data['club']
        if not self.request.user.is_superuser:
            # Club admins can only assign to their own clubs
            user_clubs = Club.objects.filter(admins__user=self.request.user)
            if club not in user_clubs:
                raise PermissionDenied("You can only assign club admins to clubs you manage.")
        
        serializer.save(created_by=self.request.user)


class ChapterAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing chapter admins
    """
    queryset = ChapterAdmin.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ChapterAdminSerializer
    permission_classes = [IsClubAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chapter', 'chapter__club']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'chapter__name']
    ordering_fields = ['created_at', 'user__username']

    def get_queryset(self):
        """
        Return chapter admins that the user can view
        """
        if not self.request.user.is_authenticated:
            return ChapterAdmin.objects.none()
        
        if self.request.user.is_superuser:
            return ChapterAdmin.objects.select_related(
                'user', 'chapter', 'chapter__club', 'created_by'
            ).all()
        
        # Club admins can see chapter admins for their clubs
        user_clubs = get_user_manageable_clubs(self.request.user)
        if user_clubs.exists():
            return ChapterAdmin.objects.select_related(
                'user', 'chapter', 'chapter__club', 'created_by'
            ).filter(chapter__club__in=user_clubs)
        
        return ChapterAdmin.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

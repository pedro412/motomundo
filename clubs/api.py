from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from .serializers import ClubSerializer, ChapterSerializer, MemberSerializer, ClubAdminSerializer, ChapterAdminSerializer
from .permissions import (
    IsClubAdminOrReadOnly, 
    CanCreateChapter, 
    CanCreateMember,
    get_user_manageable_clubs,
    get_user_manageable_chapters,
    get_user_manageable_members
)


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ClubSerializer
    permission_classes = [IsClubAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['foundation_date']
    search_fields = ['name', 'website']
    ordering_fields = ['name', 'foundation_date', 'created_at']

    def get_queryset(self):
        """
        Return clubs that the user can manage, or all clubs if superuser
        """
        if not self.request.user.is_authenticated:
            return Club.objects.none()
        
        return get_user_manageable_clubs(self.request.user).order_by('name')


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ChapterSerializer
    permission_classes = [IsClubAdminOrReadOnly, CanCreateChapter]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['club', 'foundation_date']
    search_fields = ['name', 'club__name']
    ordering_fields = ['name', 'foundation_date', 'created_at']

    def get_queryset(self):
        """
        Return chapters that the user can manage
        """
        if not self.request.user.is_authenticated:
            return Chapter.objects.none()
        
        return get_user_manageable_chapters(self.request.user).select_related('club').order_by('name')

    def perform_create(self, serializer):
        """
        Set the creator when creating a chapter
        """
        serializer.save()


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = MemberSerializer
    permission_classes = [CanCreateMember]  # Use only CanCreateMember which handles both club admins and chapter managers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chapter', 'role', 'is_active']
    search_fields = ['first_name', 'last_name', 'nickname', 'chapter__name', 'chapter__club__name']
    ordering_fields = ['first_name', 'last_name', 'joined_at', 'created_at']

    def get_queryset(self):
        """
        Return members that the user can manage
        """
        if not self.request.user.is_authenticated:
            return Member.objects.none()
        
        return get_user_manageable_members(self.request.user).select_related(
            'chapter', 'chapter__club', 'user'
        ).order_by('first_name', 'last_name')


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

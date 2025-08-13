from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Club, Chapter, Member, ClubAdmin, ChapterManager
from .serializers import ClubSerializer, ChapterSerializer, MemberSerializer, ClubAdminSerializer, ChapterManagerSerializer
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
    permission_classes = [IsClubAdminOrReadOnly, CanCreateMember]
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
    queryset = ClubAdmin.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ClubAdminSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['club', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'club__name']
    ordering_fields = ['created_at', 'club__name', 'user__username']

    def get_queryset(self):
        """
        Only superusers can manage club admins
        """
        if not (self.request.user.is_authenticated and self.request.user.is_superuser):
            return ClubAdmin.objects.none()
        
        return ClubAdmin.objects.select_related('user', 'club', 'created_by').order_by('club__name', 'user__username')


class ChapterManagerViewSet(viewsets.ModelViewSet):
    queryset = ChapterManager.objects.all()  # Default queryset, will be filtered in get_queryset
    serializer_class = ChapterManagerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chapter', 'chapter__club', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'chapter__name', 'chapter__club__name']
    ordering_fields = ['created_at', 'chapter__club__name', 'chapter__name', 'user__username']

    def get_queryset(self):
        """
        Superusers and club admins can manage chapter managers
        """
        if not self.request.user.is_authenticated:
            return ChapterManager.objects.none()
        
        if self.request.user.is_superuser:
            return ChapterManager.objects.select_related(
                'user', 'chapter', 'chapter__club', 'created_by'
            ).order_by('chapter__club__name', 'chapter__name', 'user__username')
        
        # Club admins can only manage chapter managers for their clubs
        manageable_clubs = get_user_manageable_clubs(self.request.user)
        return ChapterManager.objects.filter(
            chapter__club__in=manageable_clubs
        ).select_related(
            'user', 'chapter', 'chapter__club', 'created_by'
        ).order_by('chapter__club__name', 'chapter__name', 'user__username')

    def perform_create(self, serializer):
        """
        Check if user can create chapter manager for the specified chapter
        """
        chapter = serializer.validated_data['chapter']
        if not (self.request.user.is_superuser or 
                ClubAdmin.objects.filter(user=self.request.user, club=chapter.club).exists()):
            raise PermissionDenied("You don't have permission to create managers for this chapter")
        
        serializer.save(created_by=self.request.user)

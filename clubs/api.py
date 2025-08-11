from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Club, Chapter, Member
from .serializers import ClubSerializer, ChapterSerializer, MemberSerializer


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all().order_by('name')
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['foundation_date']
    search_fields = ['name', 'website']
    ordering_fields = ['name', 'foundation_date', 'created_at']


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.select_related('club').all().order_by('name')
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['club', 'foundation_date']
    search_fields = ['name', 'club__name']
    ordering_fields = ['name', 'foundation_date', 'created_at']


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('chapter', 'chapter__club', 'user').all().order_by('first_name', 'last_name')
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chapter', 'role', 'is_active']
    search_fields = ['first_name', 'last_name', 'nickname', 'chapter__name', 'chapter__club__name']
    ordering_fields = ['first_name', 'last_name', 'joined_at', 'created_at']

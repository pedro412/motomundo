from rest_framework import permissions
from django.contrib.auth.models import User
from .models import ClubAdmin, ChapterManager, Club, Chapter, Member


class IsClubAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows club admins to manage chapters and members for their clubs
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # For Club objects
        if isinstance(obj, Club):
            return (
                request.user.is_superuser or 
                ClubAdmin.objects.filter(user=request.user, club=obj).exists()
            )
        
        # For Chapter objects
        if isinstance(obj, Chapter):
            return (
                request.user.is_superuser or 
                ClubAdmin.objects.filter(user=request.user, club=obj.club).exists()
            )
        
        # For Member objects
        if isinstance(obj, Member):
            return (
                request.user.is_superuser or 
                ClubAdmin.objects.filter(user=request.user, club=obj.chapter.club).exists() or
                ChapterManager.objects.filter(user=request.user, chapter=obj.chapter).exists()
            )
        
        return False


class IsChapterManagerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows chapter managers to manage members only for their chapters
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Chapter managers can only modify members
        if isinstance(obj, Member):
            return (
                request.user.is_superuser or 
                ClubAdmin.objects.filter(user=request.user, club=obj.chapter.club).exists() or
                ChapterManager.objects.filter(user=request.user, chapter=obj.chapter).exists()
            )
        
        # Chapter managers cannot modify clubs or chapters
        return request.user.is_superuser


class CanCreateChapter(permissions.BasePermission):
    """
    Permission to check if a user can create chapters for a specific club
    """
    
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        # Check if user is trying to create a chapter
        if hasattr(view, 'get_serializer_class'):
            club_id = request.data.get('club')
            if club_id:
                try:
                    club = Club.objects.get(id=club_id)
                    return (
                        request.user.is_superuser or
                        ClubAdmin.objects.filter(user=request.user, club=club).exists()
                    )
                except Club.DoesNotExist:
                    return False
        
        return request.user.is_superuser


class CanCreateMember(permissions.BasePermission):
    """
    Permission to check if a user can create members for a specific chapter
    """
    
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        # Check if user is trying to create a member
        if hasattr(view, 'get_serializer_class'):
            chapter_id = request.data.get('chapter')
            if chapter_id:
                try:
                    chapter = Chapter.objects.get(id=chapter_id)
                    return (
                        request.user.is_superuser or
                        ClubAdmin.objects.filter(user=request.user, club=chapter.club).exists() or
                        ChapterManager.objects.filter(user=request.user, chapter=chapter).exists()
                    )
                except Chapter.DoesNotExist:
                    return False
        
        return request.user.is_superuser


def user_can_manage_club(user, club):
    """
    Helper function to check if a user can manage a specific club
    """
    return (
        user.is_superuser or 
        ClubAdmin.objects.filter(user=user, club=club).exists()
    )


def user_can_manage_chapter(user, chapter):
    """
    Helper function to check if a user can manage a specific chapter
    """
    return (
        user.is_superuser or 
        ClubAdmin.objects.filter(user=user, club=chapter.club).exists() or
        ChapterManager.objects.filter(user=user, chapter=chapter).exists()
    )


def get_user_manageable_clubs(user):
    """
    Get all clubs that a user can manage
    """
    if user.is_superuser:
        return Club.objects.all()
    
    return Club.objects.filter(admins__user=user)


def get_user_manageable_chapters(user):
    """
    Get all chapters that a user can manage
    """
    if user.is_superuser:
        return Chapter.objects.all()
    
    # Clubs where user is admin
    club_chapters = Chapter.objects.filter(club__admins__user=user)
    
    # Chapters where user is manager
    direct_chapters = Chapter.objects.filter(managers__user=user)
    
    return (club_chapters | direct_chapters).distinct()


def get_user_manageable_members(user):
    """
    Get all members that a user can manage
    """
    if user.is_superuser:
        return Member.objects.all()
    
    # Members from clubs where user is admin
    club_members = Member.objects.filter(chapter__club__admins__user=user)
    
    # Members from chapters where user is manager
    chapter_members = Member.objects.filter(chapter__managers__user=user)
    
    return (club_members | chapter_members).distinct()

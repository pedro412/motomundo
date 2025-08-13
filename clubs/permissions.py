from rest_framework import permissions
from django.contrib.auth.models import User
from .models import ClubAdmin, ChapterAdmin, Club, Chapter, Member


class IsClubAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow club admins to edit clubs they manage,
    and read-only access for other authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for club admins or superusers
        return (request.user.is_authenticated and 
                (request.user.is_superuser or 
                 ClubAdmin.objects.filter(user=request.user).exists()))
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # Get user's administered clubs
        user_clubs = Club.objects.filter(admins__user=request.user)
        
        # Club admins can only edit clubs they manage
        if hasattr(obj, 'club'):
            # For chapters and members
            return obj.club in user_clubs
        elif hasattr(obj, 'chapter'):
            # For members through chapter
            return obj.chapter.club in user_clubs
        elif isinstance(obj, Club):
            # For clubs directly
            return obj in user_clubs
        elif isinstance(obj, ClubAdmin):
            # NEW: Club admins can manage other club admins for their clubs
            return obj.club in user_clubs
        elif isinstance(obj, ChapterAdmin):
            # Club admins can manage chapter managers for their chapters
            return obj.chapter.club in user_clubs
        
        return False


class IsChapterAdminOrReadOnly(permissions.BasePermission):
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
                ChapterAdmin.objects.filter(user=request.user, chapter=obj.chapter).exists()
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
    Also handles read access for authenticated users
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # For write operations (like POST), check if user can create members
        if request.method == 'POST':
            chapter_id = request.data.get('chapter')
            if chapter_id:
                try:
                    chapter = Chapter.objects.get(id=chapter_id)
                    return (
                        request.user.is_superuser or
                        ClubAdmin.objects.filter(user=request.user, club=chapter.club).exists() or
                        ChapterAdmin.objects.filter(user=request.user, chapter=chapter).exists()
                    )
                except Chapter.DoesNotExist:
                    return False
        
        # For other write operations (PUT, PATCH, DELETE), defer to object-level permissions
        # This allows the has_object_permission method to handle the detailed check
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # For member objects, check if user can manage this member's chapter
        return (
            ClubAdmin.objects.filter(user=request.user, club=obj.chapter.club).exists() or
            ChapterAdmin.objects.filter(user=request.user, chapter=obj.chapter).exists()
        )


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
        ChapterAdmin.objects.filter(user=user, chapter=chapter).exists()
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
    
    # Chapters where user is admin
    direct_chapters = Chapter.objects.filter(admins__user=user)
    
    return (club_chapters | direct_chapters).distinct()


def get_user_manageable_members(user):
    """
    Get all members that a user can manage
    """
    if user.is_superuser:
        return Member.objects.all()
    
    # Members from clubs where user is admin
    club_members = Member.objects.filter(chapter__club__admins__user=user)
    
    # Members from chapters where user is admin
    chapter_members = Member.objects.filter(chapter__admins__user=user)
    
    return (club_members | chapter_members).distinct()

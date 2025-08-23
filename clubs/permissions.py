from rest_framework import permissions
from django.contrib.auth.models import User
from .models import ClubAdmin, ChapterAdmin, Club, Chapter, Member


class IsClubAdminOrPublicReadOnly(permissions.BasePermission):
    """
    Custom permission to allow club admins to edit clubs they manage,
    and read-only access for all users (including unauthenticated).
    For club creation: any authenticated user can create a club (they become admin automatically).
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any user (authenticated or not)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is authenticated first for write operations
        if not request.user.is_authenticated:
            return False
        
        # For club creation (POST to clubs endpoint), allow any authenticated user
        if request.method == 'POST' and view.basename == 'club':
            return True
        
        # For other write operations, require admin permissions
        is_club_admin = ClubAdmin.objects.filter(user=request.user).exists()
        is_chapter_admin = ChapterAdmin.objects.filter(user=request.user).exists()
        
        return (request.user.is_superuser or is_club_admin or is_chapter_admin)
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any user (authenticated or not)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, user must be authenticated
        if not request.user.is_authenticated:
            return False
        
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # Get user's administered clubs
        user_clubs = Club.objects.filter(admins__user=request.user)
        
        # Club admins can only edit clubs they manage
        if hasattr(obj, 'club') and not isinstance(obj, Chapter):
            # For chapters and members
            return obj.club in user_clubs
        elif hasattr(obj, 'chapter'):
            # For members through chapter
            return obj.chapter.club in user_clubs
        elif isinstance(obj, Club):
            # For clubs directly
            return obj in user_clubs
        elif isinstance(obj, Chapter):
            # For chapters directly - allow chapter admins to edit their chapters
            is_chapter_admin = ChapterAdmin.objects.filter(user=request.user, chapter=obj).exists()
            return (obj.club in user_clubs or is_chapter_admin)
        elif isinstance(obj, ClubAdmin):
            # NEW: Club admins can manage other club admins for their clubs
            return obj.club in user_clubs
        elif isinstance(obj, ChapterAdmin):
            # Club admins can manage chapter managers for their chapters
            return obj.chapter.club in user_clubs
        
        return False


class IsClubAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow club admins to edit clubs they manage,
    and read-only access for other authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return False
        
        # Write permissions only for club admins, chapter admins, or superusers
        is_club_admin = ClubAdmin.objects.filter(user=request.user).exists()
        is_chapter_admin = ChapterAdmin.objects.filter(user=request.user).exists()
        
        return (request.user.is_superuser or is_club_admin or is_chapter_admin)
    
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
        if hasattr(obj, 'club') and not isinstance(obj, Chapter):
            # For chapters and members
            return obj.club in user_clubs
        elif hasattr(obj, 'chapter'):
            # For members through chapter
            return obj.chapter.club in user_clubs
        elif isinstance(obj, Club):
            # For clubs directly
            return obj in user_clubs
        elif isinstance(obj, Chapter):
            # For chapters directly - allow chapter admins to edit their chapters
            is_chapter_admin = ChapterAdmin.objects.filter(user=request.user, chapter=obj).exists()
            return (obj.club in user_clubs or is_chapter_admin)
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
    Only superusers can create chapters directly - others create join requests
    """
    
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        # Only authenticated users can create join requests/chapters
        if not request.user.is_authenticated:
            return False
        
        # Check if user is trying to create a chapter
        if hasattr(view, 'get_serializer_class'):
            club_id = request.data.get('club')
            if club_id:
                try:
                    club = Club.objects.get(id=club_id)
                    # For superusers, allow direct chapter creation
                    if request.user.is_superuser:
                        return True
                    # For others, they can create join requests (handled in perform_create)
                    # Check if club accepts new chapters
                    return club.accepts_new_chapters
                except Club.DoesNotExist:
                    return False
        
        return request.user.is_superuser


class CanCreateMemberOrPublicRead(permissions.BasePermission):
    """
    Permission to check if a user can create members for a specific chapter
    Also handles public read access for all users
    """
    
    def has_permission(self, request, view):
        # Allow read permissions for any user (authenticated or not)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations (like POST), check if user can create members
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return False
                
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
        return request.user.is_authenticated if request.user else False
    
    def has_object_permission(self, request, view, obj):
        # Allow read permissions for any user (authenticated or not)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, user must be authenticated
        if not request.user.is_authenticated:
            return False
        
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # For member objects, check if user can manage this member's chapter
        return (
            ClubAdmin.objects.filter(user=request.user, club=obj.chapter.club).exists() or
            ChapterAdmin.objects.filter(user=request.user, chapter=obj.chapter).exists()
        )


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
    
    all_chapters = (club_chapters | direct_chapters).distinct()
    
    return all_chapters


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


class IsClubAdminOrChapterAdmin(permissions.BasePermission):
    """
    Permission that allows only club admins or chapter admins to perform actions.
    Useful for email invitations and other administrative functions.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return False
        
        # Superusers have access
        if request.user.is_superuser:
            return True
        
        # Check if user is club admin or chapter admin
        is_club_admin = ClubAdmin.objects.filter(user=request.user).exists()
        is_chapter_admin = ChapterAdmin.objects.filter(user=request.user).exists()
        
        return is_club_admin or is_chapter_admin
    
    def has_object_permission(self, request, view, obj):
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # For club-related objects
        if hasattr(obj, 'club'):
            return user_can_manage_club(request.user, obj.club)
        
        # For chapter-related objects
        if hasattr(obj, 'chapter'):
            return user_can_manage_chapter(request.user, obj.chapter)
        
        # For direct club objects
        if isinstance(obj, Club):
            return user_can_manage_club(request.user, obj)
        
        # For direct chapter objects
        if isinstance(obj, Chapter):
            return user_can_manage_chapter(request.user, obj)
        
        # Default to basic permission check
        is_club_admin = ClubAdmin.objects.filter(user=request.user).exists()
        is_chapter_admin = ChapterAdmin.objects.filter(user=request.user).exists()
        
        return is_club_admin or is_chapter_admin

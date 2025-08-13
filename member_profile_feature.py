"""
Enhanced Member Detail View with Cross-Club Profile
Shows a member's complete profile across all clubs when they have a linked user account
"""

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class MemberCrossClubProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a member's complete profile across all clubs
    """
    club_name = serializers.CharField(source='chapter.club.name', read_only=True)
    club_id = serializers.IntegerField(source='chapter.club.id', read_only=True)
    chapter_name = serializers.CharField(source='chapter.name', read_only=True)
    chapter_id = serializers.IntegerField(source='chapter.id', read_only=True)
    member_since = serializers.DateField(source='joined_at', read_only=True)
    is_active_member = serializers.BooleanField(source='is_active', read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'club_id', 'club_name', 'chapter_id', 'chapter_name',
            'first_name', 'last_name', 'nickname', 'role', 
            'member_since', 'is_active_member', 'created_at'
        ]


class UserCompleteProfileSerializer(serializers.ModelSerializer):
    """
    Complete user profile including all memberships and administrative roles
    """
    full_name = serializers.SerializerMethodField()
    all_memberships = serializers.SerializerMethodField()
    administrative_roles = serializers.SerializerMethodField()
    total_clubs = serializers.SerializerMethodField()
    total_chapters = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'first_name', 'last_name',
            'date_joined', 'total_clubs', 'total_chapters',
            'all_memberships', 'administrative_roles'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_all_memberships(self, obj):
        """Get all member identities across all clubs"""
        memberships = Member.objects.filter(user=obj).select_related(
            'chapter', 'chapter__club'
        ).order_by('chapter__club__name', 'chapter__name')
        
        return MemberCrossClubProfileSerializer(memberships, many=True).data
    
    def get_administrative_roles(self, obj):
        """Get all administrative roles"""
        roles = []
        
        # Club Admin roles
        club_admins = ClubAdmin.objects.filter(user=obj).select_related('club')
        for club_admin in club_admins:
            roles.append({
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
        chapter_admins = ChapterAdmin.objects.filter(user=obj).select_related(
            'chapter', 'chapter__club'
        )
        for chapter_admin in chapter_admins:
            roles.append({
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
        
        return sorted(roles, key=lambda x: x['since'])
    
    def get_total_clubs(self, obj):
        """Count unique clubs user belongs to"""
        return Member.objects.filter(user=obj).values('chapter__club').distinct().count()
    
    def get_total_chapters(self, obj):
        """Count total chapters user is member of"""
        return Member.objects.filter(user=obj).count()


# Add this method to the existing MemberViewSet in clubs/api.py
def add_member_profile_action():
    """
    This is the code to add to MemberViewSet in clubs/api.py
    """
    return '''
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
        
        # Get complete user profile
        user_profile = UserCompleteProfileSerializer(member.user).data
        
        # Add context about which member was clicked
        user_profile['clicked_member_context'] = {
            'member_id': member.id,
            'club_name': member.chapter.club.name,
            'chapter_name': member.chapter.name,
            'member_role': member.role,
            'member_nickname': member.nickname
        }
        
        return Response(user_profile)
    '''


if __name__ == "__main__":
    print("This file contains serializers and method code for the member complete profile feature.")
    print("Add the complete_profile action to MemberViewSet in clubs/api.py")

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.conf import settings
from django.templatetags.static import static
import os
import logging
from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin

logger = logging.getLogger(__name__)


class ClubSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    featured_members = serializers.SerializerMethodField()
    total_members = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = [
            'id', 'name', 'description', 'foundation_date', 'logo', 'logo_url', 'website',
            'featured_members', 'created_at', 'updated_at', 'total_members'
        ]
    
    def validate_name(self, value):
        """
        Validate that club name is unique (case-insensitive)
        """
        # Check for existing clubs with the same name (case-insensitive)
        existing = Club.objects.filter(name__iexact=value)
        
        # If this is an update, exclude the current instance
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError(
                f"A club with the name '{value}' already exists. Please choose a different name."
            )
        
        return value

    def to_representation(self, instance):
        """
        Override to provide proper logo URL handling
        """
        data = super().to_representation(instance)
        return data

    def get_logo_url(self, obj):
        """
        Return logo URL using flexible storage backend
        """
        request = self.context.get('request')
        
        if obj.logo:
            try:
                # Get URL from the flexible storage backend
                logo_url = obj.logo.url
                
                # For Cloudinary URLs, they're already absolute
                if logo_url.startswith(('http://', 'https://')):
                    return logo_url
                
                # For local URLs, make them absolute if request context is available
                if request:
                    return request.build_absolute_uri(logo_url)
                else:
                    # Fallback for when request context is not available
                    return f"https://motomundo-production.up.railway.app{logo_url}"
                    
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error getting logo URL for club {obj.id}: {e}")
        
        # Return None if no logo available
        return None

    def get_featured_members(self, obj):
        """
        Return all members with national roles for this club
        """
        # Get all members of this club that have a national role
        featured_members = Member.objects.filter(
            chapter__club=obj,
            national_role__isnull=False,
            national_role__gt='',  # Exclude empty strings
            is_active=True
        ).select_related('chapter').order_by('national_role', 'first_name', 'last_name')
        
        # Get request context for building absolute URLs
        request = self.context.get('request')
        
        # Serialize the featured members
        featured_data = []
        for member in featured_members:
            # Get the human-readable national role
            national_role_display = None
            for choice_value, choice_label in Member.NATIONAL_ROLE_CHOICES:
                if choice_value == member.national_role:
                    national_role_display = choice_label
                    break
                
            # Build absolute URL for profile picture with flexible storage backend
            profile_picture_url = None
            if member.profile_picture:
                try:
                    # The flexible storage already handles URL generation
                    profile_picture_url = member.profile_picture.url
                    
                    # Ensure absolute URL
                    if request and not profile_picture_url.startswith(('http://', 'https://')):
                        profile_picture_url = request.build_absolute_uri(profile_picture_url)
                    
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error getting profile picture URL for member {member.id}: {e}")
                    profile_picture_url = None
            
            # If no profile picture is set, provide default avatar
            if not profile_picture_url and request:
                default_avatar_url = static('clubs/members/profiles/default-avatar.svg')
                profile_picture_url = request.build_absolute_uri(default_avatar_url)
  
            member_data = {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'nickname': member.nickname,
                'chapter_id': member.chapter.id,
                'chapter_name': member.chapter.name,
                'role': member.role,
                'national_role': member.national_role,
                'national_role_display': national_role_display,
                'profile_picture': profile_picture_url,
                'joined_at': member.joined_at,
                'is_active': member.is_active
            }
            featured_data.append(member_data)
        
        return featured_data

    def get_total_members(self, obj):
        """
        Return the total number of members for this club
        """
        return Member.objects.filter(chapter__club=obj).count()


class ChapterSerializer(serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all())
    total_members = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'club', 'name', 'description', 'foundation_date',
            'created_at', 'updated_at', 'total_members'
        ]

    def get_total_members(self, obj):
        """
        Return the total number of members for this chapter
        """
        return Member.objects.filter(chapter=obj).count()


class MemberSerializer(serializers.ModelSerializer):
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all())
    # Make user field optional - don't declare it explicitly, let it use model defaults
    club = serializers.SerializerMethodField()  # Read-only field that gets club from chapter
    claim_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Member
        fields = [
            'id', 'chapter', 'club', 'first_name', 'last_name', 'nickname', 'date_of_birth', 'profile_picture',
            'role', 'member_type', 'national_role', 'joined_at', 'user', 'claim_code', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'club']
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
            'claim_code': {'write_only': True}  # Don't expose claim codes in responses for security
        }

    def get_club(self, obj):
        """Get club information through the chapter relationship"""
        if obj.chapter:
            return {
                'id': obj.chapter.club.id,
                'name': obj.chapter.club.name
            }
        return None

    def validate(self, data):
        # Ensure user field is not required and defaults to None
        # Remove user field from data if it's empty string or not provided
        if 'user' not in data or data.get('user') == '' or data.get('user') is None:
            data.pop('user', None)  # Remove it entirely so it defaults to null
        return data


class ClubAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all())
    user_display = serializers.SerializerMethodField()
    club_display = serializers.SerializerMethodField()

    class Meta:
        model = ClubAdmin
        fields = [
            'id', 'user', 'club', 'user_display', 'club_display', 
            'created_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'created_by']

    def get_user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_club_display(self, obj):
        return obj.club.name

    def validate(self, data):
        user = data.get('user')
        club = data.get('club')
        
        # Check if assignment already exists
        if ClubAdmin.objects.filter(user=user, club=club).exists():
            raise serializers.ValidationError("This user is already a club admin for this club.")
        
        # Prevent self-assignment (except for superusers)
        request = self.context.get('request')
        if request and not request.user.is_superuser and user == request.user:
            raise serializers.ValidationError("You cannot assign yourself as a club admin.")
        
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ChapterAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all())
    user_display = serializers.SerializerMethodField()
    chapter_display = serializers.SerializerMethodField()

    class Meta:
        model = ChapterAdmin
        fields = [
            'id', 'user', 'chapter', 'user_display', 'chapter_display',
            'created_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'created_by']

    def get_user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_chapter_display(self, obj):
        return f"{obj.chapter.name} ({obj.chapter.club.name})"

    def validate(self, data):
        user = data.get('user')
        chapter = data.get('chapter')
        
        # Check if assignment already exists
        if ChapterAdmin.objects.filter(user=user, chapter=chapter).exists():
            raise serializers.ValidationError("This user is already a chapter admin for this chapter.")
        
        # Prevent self-assignment (except for superusers)
        request = self.context.get('request')
        if request and not request.user.is_superuser and user == request.user:
            raise serializers.ValidationError("You cannot assign yourself as a chapter admin.")
        
        # Ensure club admins can only assign chapter admins to chapters in their clubs
        if request and not request.user.is_superuser:
            user_clubs = Club.objects.filter(admins__user=request.user)
            if chapter and chapter.club not in user_clubs:
                raise PermissionDenied("You can only assign chapter admins to chapters in clubs you manage.")
        
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

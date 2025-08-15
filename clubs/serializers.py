from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.conf import settings
from django.templatetags.static import static
import os
from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class ClubSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = [
            'id', 'name', 'description', 'foundation_date', 'logo', 'logo_url', 'website',
            'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """
        Override to provide working logo URL for Alterados MC
        """
        data = super().to_representation(instance)
        
        # For Alterados MC, replace the broken media URL with working static URL
        if instance.name == "Alterados MC":
            request = self.context.get('request')
            static_url = static('clubs/logos/nacionalmc.jpg')
            if request:
                # Override the logo field with the working static URL
                data['logo'] = request.build_absolute_uri(static_url)
            else:
                # Fallback for when request context is not available
                data['logo'] = f"https://motomundo-production.up.railway.app{static_url}"
        
        return data

    def get_logo_url(self, obj):
        """
        Return logo URL with fallback to static file if media file doesn't exist
        """
        request = self.context.get('request')
        
        if obj.logo:
            # Check if media file exists or return fallback
            try:
                if hasattr(obj.logo, 'url'):
                    media_path = os.path.join(settings.MEDIA_ROOT, str(obj.logo))
                    if os.path.exists(media_path):
                        return obj.logo.url
            except (ValueError, AttributeError):
                pass
        
        # Fallback to static file for Alterados MC
        if obj.name == "Alterados MC":
            static_url = static('clubs/logos/nacionalmc.jpg')
            if request:
                return request.build_absolute_uri(static_url)
            else:
                return f"https://motomundo-production.up.railway.app{static_url}"
        
        # Return None if no logo available
        return None


class ChapterSerializer(serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all())

    class Meta:
        model = Chapter
        fields = [
            'id', 'club', 'name', 'description', 'foundation_date',
            'created_at', 'updated_at'
        ]


class MemberSerializer(serializers.ModelSerializer):
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Member
        fields = [
            'id', 'chapter', 'first_name', 'last_name', 'nickname', 'date_of_birth',
            'role', 'joined_at', 'user', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        # Ensure user field is not required
        if 'user' not in data:
            data['user'] = None
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

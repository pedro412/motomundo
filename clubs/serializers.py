from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            'id', 'name', 'description', 'foundation_date', 'logo', 'website',
            'created_at', 'updated_at'
        ]


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

    class Meta:
        model = Member
        fields = [
            'id', 'chapter', 'first_name', 'last_name', 'nickname', 'date_of_birth',
            'role', 'joined_at', 'user', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


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

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Club, Chapter, Member, ClubAdmin, ChapterManager


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

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ChapterManagerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all())
    user_display = serializers.SerializerMethodField()
    chapter_display = serializers.SerializerMethodField()

    class Meta:
        model = ChapterManager
        fields = [
            'id', 'user', 'chapter', 'user_display', 'chapter_display',
            'created_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'created_by']

    def get_user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_chapter_display(self, obj):
        return f"{obj.chapter.name} ({obj.chapter.club.name})"

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

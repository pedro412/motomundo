from rest_framework import serializers
from .models import Club, Chapter, Member


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

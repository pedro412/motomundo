from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import ClubAdmin, ChapterAdmin


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional username; if omitted the email will be used as username"
    )

    email = serializers.EmailField(
        required=True,
        help_text="Valid email address"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True},
        }

    # Username is auto-set to email, so no need to validate username

    def validate_email(self, value):
        """
        Validate email is unique (case-insensitive)
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        If username provided, ensure it's unique (case-insensitive) and not blank when given.
        """
        if value is None or value == '':
            return value
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password using Django's password validators
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Validate that passwords match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        """
        Create a new user with encrypted password, username set to email
        """
        validated_data.pop('password_confirm', None)
        email = validated_data['email']
        username = validated_data.get('username') or email
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information (read-only)
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        """
        Validate new password using Django's password validators
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Validate that new passwords match
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords do not match."
            })
        return attrs

    def validate_old_password(self, value):
        """
        Validate old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information and permissions
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        # Add permission information
        is_club_admin = ClubAdmin.objects.filter(user=self.user).exists()
        is_chapter_admin = ChapterAdmin.objects.filter(user=self.user).exists()
        
        data['permissions'] = {
            'is_club_admin': is_club_admin,
            'is_chapter_admin': is_chapter_admin,
            'clubs': [],
            'chapters': []
        }
        
        # Get user's clubs and chapters
        if is_club_admin:
            club_admins = ClubAdmin.objects.filter(user=self.user).select_related('club')
            data['permissions']['clubs'] = [
                {'id': ca.club.id, 'name': ca.club.name} for ca in club_admins
            ]
        
        if is_chapter_admin:
            chapter_admins = ChapterAdmin.objects.filter(user=self.user).select_related('chapter', 'chapter__club')
            data['permissions']['chapters'] = [
                {
                    'id': cm.chapter.id, 
                    'name': cm.chapter.name,
                    'club': {'id': cm.chapter.club.id, 'name': cm.chapter.club.name}
                } for cm in chapter_admins
            ]
        
        return data


class JWTRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with JWT response
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional username; if omitted the email will be used as username"
    )

    email = serializers.EmailField(
        required=True,
        help_text="Valid email address"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True},
        }

    # Username is auto-set to email, so no need to validate username

    def validate_email(self, value):
        """
        Validate email is unique (case-insensitive)
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        If username provided, ensure it's unique (case-insensitive) and not blank when given.
        """
        if value is None or value == '':
            return value
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password using Django's password validators
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Validate that passwords match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        """
        Create a new user with encrypted password, username set to email
        """
        validated_data.pop('password_confirm', None)
        email = validated_data['email']
        username = validated_data.get('username') or email
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

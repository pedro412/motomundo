"""
Test utilities for creating test data with proper defaults
"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from PIL import Image
import io


def create_test_image(name='test.jpg', size=(100, 100), color='RGB'):
    """
    Create a simple test image for testing purposes
    """
    image = Image.new(color, size, color=(255, 255, 255))
    image_io = io.BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=image_io.read(),
        content_type='image/jpeg'
    )


def create_test_user(username='testuser', email='test@example.com', password='testpass123', **kwargs):
    """Create a test user with default values"""
    defaults = {
        'username': username,
        'email': email,
        'password': password,
    }
    defaults.update(kwargs)
    
    user = User.objects.create_user(**defaults)
    return user


def create_test_club(name='Test Club', **kwargs):
    """Create a test club with default values"""
    defaults = {
        'name': name,
        'description': 'A test club',
    }
    defaults.update(kwargs)
    return Club.objects.create(**defaults)


def create_test_chapter(club=None, name='Test Chapter', **kwargs):
    """Create a test chapter with default values"""
    if club is None:
        club = create_test_club()
    
    defaults = {
        'club': club,
        'name': name,
        'description': 'A test chapter',
    }
    defaults.update(kwargs)
    return Chapter.objects.create(**defaults)


def create_test_member(chapter=None, first_name='Test', last_name='Member', role='member', **kwargs):
    """Create a test member with default values including profile picture"""
    if chapter is None:
        chapter = create_test_chapter()
    
    # Create default profile picture if not provided
    if 'profile_picture' not in kwargs:
        kwargs['profile_picture'] = create_test_image(f'{first_name}_profile.jpg')
    
    defaults = {
        'chapter': chapter,
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
    }
    defaults.update(kwargs)
    return Member.objects.create(**defaults)


def create_test_club_admin(user=None, club=None, **kwargs):
    """Create a test club admin with default values"""
    if user is None:
        user = create_test_user()
    if club is None:
        club = create_test_club()
    
    defaults = {
        'user': user,
        'club': club,
    }
    defaults.update(kwargs)
    return ClubAdmin.objects.create(**defaults)


def create_test_chapter_admin(user=None, chapter=None, **kwargs):
    """Create a test chapter admin with default values"""
    if user is None:
        user = create_test_user()
    if chapter is None:
        chapter = create_test_chapter()
    
    defaults = {
        'user': user,
        'chapter': chapter,
    }
    defaults.update(kwargs)
    return ChapterAdmin.objects.create(**defaults)

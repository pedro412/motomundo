#!/usr/bin/env python
"""
Permission System Test Script

This script provides interactive tests for the permission system.
Run with: python manage.py shell < test_permissions.py
"""

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterAdmin
from clubs.permissions import (
    get_user_manageable_clubs,
    get_user_manageable_chapters, 
    get_user_manageable_members,
    user_can_manage_club,
    user_can_manage_chapter
)

def test_permission_system():
    """
    Test the permission system with current data
    """
    print("=== PERMISSION SYSTEM TEST ===\n")
    
    # Get all users
    users = User.objects.all()
    clubs = Club.objects.all()
    chapters = Chapter.objects.all()
    
    print(f"Total Users: {users.count()}")
    print(f"Total Clubs: {clubs.count()}")
    print(f"Total Chapters: {chapters.count()}")
    print(f"Total Members: {Member.objects.count()}")
    print(f"Total Club Admins: {ClubAdmin.objects.count()}")
    print(f"Total Chapter Admins: {ChapterAdmin.objects.count()}\n")
    
    # Test each user's permissions
    for user in users:
        print(f"=== USER: {user.username} ({user.first_name} {user.last_name}) ===")
        print(f"Superuser: {user.is_superuser}")
        
        # Show roles
        club_admin_roles = ClubAdmin.objects.filter(user=user)
        chapter_admin_roles = ChapterAdmin.objects.filter(user=user)
        
        if club_admin_roles.exists():
            print("Club Admin for:")
            for role in club_admin_roles:
                print(f"  - {role.club.name}")
        
        if chapter_admin_roles.exists():
            print("Chapter Admin for:")
            for role in chapter_admin_roles:
                print(f"  - {role.chapter.name} ({role.chapter.club.name})")
        
        # Test permissions
        manageable_clubs = get_user_manageable_clubs(user)
        manageable_chapters = get_user_manageable_chapters(user)
        manageable_members = get_user_manageable_members(user)
        
        print(f"Can manage {manageable_clubs.count()} clubs:")
        for club in manageable_clubs:
            print(f"  - {club.name}")
        
        print(f"Can manage {manageable_chapters.count()} chapters:")
        for chapter in manageable_chapters:
            print(f"  - {chapter.name} ({chapter.club.name})")
        
        print(f"Can manage {manageable_members.count()} members:")
        for member in manageable_members[:3]:  # Show first 3
            print(f"  - {member.first_name} {member.last_name} ({member.chapter.name})")
        if manageable_members.count() > 3:
            print(f"  ... and {manageable_members.count() - 3} more")
        
        print()

def test_specific_permissions():
    """
    Test specific permission scenarios
    """
    print("=== SPECIFIC PERMISSION TESTS ===\n")
    
    try:
        harley_admin = User.objects.get(username='harley_admin')
        sf_manager = User.objects.get(username='sf_manager')
        harley_club = Club.objects.get(name__icontains='Harley')
        bmw_club = Club.objects.get(name__icontains='BMW')
        sf_chapter = Chapter.objects.get(name__icontains='San Francisco')
        
        print("Test 1: Harley admin should manage Harley club")
        result = user_can_manage_club(harley_admin, harley_club)
        print(f"✅ PASS: {result}" if result else f"❌ FAIL: {result}")
        
        print("Test 2: Harley admin should NOT manage BMW club")
        result = user_can_manage_club(harley_admin, bmw_club)
        print(f"✅ PASS: {not result}" if not result else f"❌ FAIL: {result}")
        
        print("Test 3: SF manager should manage SF chapter")
        result = user_can_manage_chapter(sf_manager, sf_chapter)
        print(f"✅ PASS: {result}" if result else f"❌ FAIL: {result}")
        
        print("Test 4: SF manager should NOT manage BMW club")
        result = user_can_manage_club(sf_manager, bmw_club)
        print(f"✅ PASS: {not result}" if not result else f"❌ FAIL: {result}")
        
    except Exception as e:
        print(f"❌ Error running specific tests: {e}")

def show_data_summary():
    """
    Show a summary of all data
    """
    print("=== DATA SUMMARY ===\n")
    
    for club in Club.objects.all():
        print(f"🏍️  CLUB: {club.name}")
        print(f"   Description: {club.description}")
        print(f"   Website: {club.website}")
        
        chapters = club.chapters.all()
        print(f"   Chapters ({chapters.count()}):")
        for chapter in chapters:
            member_count = chapter.members.count()
            print(f"     - {chapter.name} ({member_count} members)")
        
        admins = club.admins.all()
        print(f"   Admins ({admins.count()}):")
        for admin in admins:
            print(f"     - {admin.user.get_full_name() or admin.user.username}")
        
        print()

if __name__ == "__main__":
    show_data_summary()
    test_permission_system()
    test_specific_permissions()
    print("=== PERMISSION TESTS COMPLETE ===")

#!/usr/bin/env python
"""
Clean up duplicate club names before applying unique constraint
"""
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.db.models import Count
from clubs.models import Club, ClubAdmin, Chapter, Member

def cleanup_duplicate_clubs():
    print("🧹 Cleaning up duplicate club names...")
    print("=" * 50)
    
    # Find duplicate club names
    duplicates = Club.objects.values('name').annotate(count=Count('name')).filter(count__gt=1)
    
    if not duplicates:
        print("✅ No duplicate club names found.")
        return
    
    for dup in duplicates:
        club_name = dup['name']
        count = dup['count']
        print(f"\n🔍 Processing '{club_name}' ({count} duplicates)")
        
        # Get all clubs with this name, ordered by creation date (keep oldest)
        clubs_with_name = Club.objects.filter(name=club_name).order_by('created_at')
        
        # Keep the first (oldest) club
        club_to_keep = clubs_with_name.first()
        clubs_to_remove = clubs_with_name[1:]
        
        print(f"   ✅ Keeping: Club ID {club_to_keep.id} (created {club_to_keep.created_at})")
        
        for club in clubs_to_remove:
            print(f"   🗑️  Removing: Club ID {club.id} (created {club.created_at})")
            
            # Check if this club has any members or admins
            member_count = Member.objects.filter(chapter__club=club).count()
            admin_count = ClubAdmin.objects.filter(club=club).count()
            chapter_count = Chapter.objects.filter(club=club).count()
            
            if member_count > 0 or admin_count > 0:
                print(f"      ⚠️  Club has {member_count} members, {admin_count} admins, {chapter_count} chapters")
                
                # Move club admins (avoid duplicates)
                admins_to_move = ClubAdmin.objects.filter(club=club)
                moved_admins = 0
                for admin in admins_to_move:
                    # Check if this user is already an admin of the target club
                    if not ClubAdmin.objects.filter(user=admin.user, club=club_to_keep).exists():
                        admin.club = club_to_keep
                        admin.save()
                        moved_admins += 1
                    else:
                        # Delete duplicate admin entry
                        admin.delete()
                print(f"      📦 Moved {moved_admins} admin(s) to kept club")
                
                # Move chapters (and their members)
                chapters = Chapter.objects.filter(club=club)
                for chapter in chapters:
                    # Check if chapter name conflicts with existing chapters in target club
                    existing_chapter = Chapter.objects.filter(
                        club=club_to_keep, 
                        name=chapter.name
                    ).first()
                    
                    if existing_chapter:
                        # Move members to existing chapter
                        Member.objects.filter(chapter=chapter).update(chapter=existing_chapter)
                        print(f"      📦 Moved {chapter.members.count()} member(s) from '{chapter.name}' to existing chapter")
                        chapter.delete()
                    else:
                        # Move entire chapter
                        chapter.club = club_to_keep
                        chapter.save()
                        print(f"      📦 Moved chapter '{chapter.name}' with {chapter.members.count()} member(s)")
            
            # Now safe to delete the empty club
            club.delete()
            print(f"      ✅ Deleted duplicate club")
    
    print(f"\n🎉 Cleanup complete!")
    
    # Verify no more duplicates
    remaining_duplicates = Club.objects.values('name').annotate(count=Count('name')).filter(count__gt=1)
    if remaining_duplicates:
        print("❌ Still have duplicates:")
        for dup in remaining_duplicates:
            print(f"   - {dup['name']}: {dup['count']} clubs")
    else:
        print("✅ All duplicate club names resolved!")

if __name__ == "__main__":
    cleanup_duplicate_clubs()

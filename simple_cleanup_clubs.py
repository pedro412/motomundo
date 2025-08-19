#!/usr/bin/env python
"""
Simple cleanup: Delete duplicate clubs, keeping the one with most members
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

def simple_cleanup():
    print("🧹 Simple cleanup of duplicate clubs...")
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
        
        # Get all clubs with this name
        clubs_with_name = Club.objects.filter(name=club_name)
        
        # Calculate score for each club (members + admins + chapters)
        club_scores = []
        for club in clubs_with_name:
            member_count = Member.objects.filter(chapter__club=club).count()
            admin_count = ClubAdmin.objects.filter(club=club).count()
            chapter_count = Chapter.objects.filter(club=club).count()
            score = member_count + admin_count + chapter_count
            
            club_scores.append({
                'club': club,
                'score': score,
                'members': member_count,
                'admins': admin_count,
                'chapters': chapter_count
            })
            
            print(f"   Club ID {club.id}: {member_count} members, {admin_count} admins, {chapter_count} chapters (score: {score})")
        
        # Sort by score (highest first), then by creation date (oldest first)
        club_scores.sort(key=lambda x: (-x['score'], x['club'].created_at))
        
        # Keep the highest scoring club
        club_to_keep = club_scores[0]['club']
        clubs_to_delete = [item['club'] for item in club_scores[1:]]
        
        print(f"   ✅ Keeping: Club ID {club_to_keep.id} (highest score)")
        
        for club in clubs_to_delete:
            print(f"   🗑️  Deleting: Club ID {club.id}")
            # Django will cascade delete related objects
            club.delete()
    
    print(f"\n🎉 Simple cleanup complete!")
    
    # Verify no more duplicates
    remaining_duplicates = Club.objects.values('name').annotate(count=Count('name')).filter(count__gt=1)
    if remaining_duplicates:
        print("❌ Still have duplicates:")
        for dup in remaining_duplicates:
            print(f"   - {dup['name']}: {dup['count']} clubs")
    else:
        print("✅ All duplicate club names resolved!")

if __name__ == "__main__":
    simple_cleanup()

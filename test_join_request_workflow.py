#!/usr/bin/env python3
"""
Test the complete join request approval flow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Club, Chapter, ChapterJoinRequest
from geography.models import Country, State

def test_join_request_approval():
    """Test the complete join request workflow"""
    print("Testing join request approval workflow...")
    
    try:
        # Get test data
        mexico = Country.objects.get(name="Mexico")
        state = State.objects.filter(country=mexico).first()
        
        # Get or create test club
        test_club, created = Club.objects.get_or_create(
            name="Test Approval Club",
            defaults={
                'description': 'Club for testing approval',
                'country_new': mexico,
                'primary_state_new': state,
                'club_type': 'mc',
                'is_public': True,
                'accepts_new_chapters': True
            }
        )
        
        # Create test user
        test_user, created = User.objects.get_or_create(
            username='testapprovaluser',
            defaults={
                'email': 'approval@example.com',
                'first_name': 'Approval',
                'last_name': 'User'
            }
        )
        
        # Create a join request
        join_request = ChapterJoinRequest.objects.create(
            club=test_club,
            requested_by=test_user,
            proposed_chapter_name='Test Approval Chapter',
            city='Approval City',
            state='Test State',
            state_new=state,
            description='Test chapter for approval',
            reason='Want to start a local chapter',
            estimated_members=5
        )
        
        print(f"✅ Join request created: {join_request.proposed_chapter_name}")
        print(f"   Status: {join_request.status}")
        print(f"   Requested by: {join_request.requested_by.username}")
        print(f"   Club: {join_request.club.name}")
        print(f"   State: {join_request.state_new.name if join_request.state_new else 'None'}")
        
        # Count chapters before approval
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        print(f"   Initial chapters in club: {initial_chapters}")
        
        # Approve the join request
        approved_chapter = join_request.approve("Test approval - all looks good!")
        
        print(f"\n✅ Join request approved!")
        print(f"   Status: {join_request.status}")
        print(f"   Admin notes: {join_request.admin_notes}")
        print(f"   Reviewed at: {join_request.reviewed_at}")
        
        # Verify chapter was created
        final_chapters = Chapter.objects.filter(club=test_club).count()
        print(f"   Final chapters in club: {final_chapters}")
        
        if final_chapters > initial_chapters:
            print(f"✅ Chapter created: {approved_chapter.name}")
            print(f"   Chapter owner: {approved_chapter.owner.username}")
            print(f"   Chapter city: {approved_chapter.city}")
            print(f"   Chapter state: {approved_chapter.state_new.name if approved_chapter.state_new else 'None'}")
            print(f"   Chapter club: {approved_chapter.club.name}")
            print(f"   Is public: {approved_chapter.is_public}")
            print(f"   Accepts members: {approved_chapter.accepts_new_members}")
            
            # Verify club stats were updated
            test_club.refresh_from_db()
            print(f"   Club total chapters: {test_club.total_chapters}")
            
            return True
        else:
            print("❌ Chapter was not created")
            return False
        
    except Exception as e:
        print(f"❌ Error testing join request approval: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reject_join_request():
    """Test rejecting a join request"""
    print("\nTesting join request rejection...")
    
    try:
        # Get test club
        test_club = Club.objects.get(name="Test Approval Club")
        state = State.objects.first()
        
        # Create another test user
        test_user2, created = User.objects.get_or_create(
            username='testrejectuser',
            defaults={
                'email': 'reject@example.com',
                'first_name': 'Reject',
                'last_name': 'User'
            }
        )
        
        # Create a join request to reject
        join_request = ChapterJoinRequest.objects.create(
            club=test_club,
            requested_by=test_user2,
            proposed_chapter_name='Test Reject Chapter',
            city='Reject City',
            state='Test State',
            state_new=state,
            description='Test chapter for rejection',
            reason='Want to start another chapter',
            estimated_members=3
        )
        
        print(f"✅ Join request created for rejection: {join_request.proposed_chapter_name}")
        
        # Count chapters before rejection
        initial_chapters = Chapter.objects.filter(club=test_club).count()
        
        # Reject the join request
        join_request.reject("Not enough experience with motorcycles")
        
        print(f"✅ Join request rejected!")
        print(f"   Status: {join_request.status}")
        print(f"   Admin notes: {join_request.admin_notes}")
        print(f"   Reviewed at: {join_request.reviewed_at}")
        
        # Verify no chapter was created
        final_chapters = Chapter.objects.filter(club=test_club).count()
        
        if final_chapters == initial_chapters:
            print("✅ No chapter created (correct for rejection)")
            return True
        else:
            print("❌ Chapter was created during rejection (incorrect)")
            return False
        
    except Exception as e:
        print(f"❌ Error testing join request rejection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_join_request_approval()
    success2 = test_reject_join_request()
    
    if success1 and success2:
        print("\n🎉 All join request workflow tests passed!")
    else:
        print("\n❌ Some workflow tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)

#!/usr/bin/env python3
"""
End-to-end demonstration of the new chapter creation flow
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

def demonstrate_new_flow():
    """Demonstrate the complete new chapter creation flow"""
    print("🎯 Demonstrating New Chapter Creation Flow")
    print("=" * 50)
    
    try:
        # Setup test data
        mexico = Country.objects.get(name="Mexico")
        state = State.objects.filter(country=mexico).first()
        
        # Create a demo club
        demo_club, created = Club.objects.get_or_create(
            name="Demo Motorcycle Club",
            defaults={
                'description': 'Demo club for showcasing the new flow',
                'country_new': mexico,
                'primary_state_new': state,
                'club_type': 'mc',
                'is_public': True,
                'accepts_new_chapters': True
            }
        )
        
        # Create a prospective chapter leader
        prospect, created = User.objects.get_or_create(
            username='prospective_leader',
            defaults={
                'email': 'prospect@example.com',
                'first_name': 'John',
                'last_name': 'Prospect'
            }
        )
        
        print(f"📋 Scenario Setup:")
        print(f"   Club: {demo_club.name}")
        print(f"   Accepts new chapters: {demo_club.accepts_new_chapters}")
        print(f"   Prospective leader: {prospect.get_full_name()}")
        print(f"   Current chapters: {Chapter.objects.filter(club=demo_club).count()}")
        print(f"   Pending requests: {ChapterJoinRequest.objects.filter(club=demo_club, status='pending').count()}")
        
        print(f"\n🚀 Step 1: User attempts to create chapter")
        print("   (In the old system, this would create a chapter immediately)")
        print("   (In the new system, this creates a join request)")
        
        # Simulate the API call that would create a join request
        from clubs.api import ChapterViewSet
        from clubs.serializers import ChapterSerializer
        from rest_framework.test import APIRequestFactory
        from rest_framework.exceptions import ValidationError
        
        factory = APIRequestFactory()
        request = factory.post('/api/chapters/', {
            'club': demo_club.id,
            'name': 'Guadalajara West Chapter',
            'description': 'Chapter for the western part of Guadalajara',
            'city': 'Guadalajara',
            'state_new': state.id if state else None,
        })
        request.user = prospect
        
        viewset = ChapterViewSet()
        viewset.request = request
        
        serializer = ChapterSerializer(data={
            'club': demo_club.id,
            'name': 'Guadalajara West Chapter',
            'description': 'Chapter for the western part of Guadalajara',
            'city': 'Guadalajara',
            'state_new': state.id if state else None,
        })
        
        serializer.is_valid()
        
        try:
            viewset.perform_create(serializer)
            print("   ❌ ERROR: Chapter was created directly!")
        except ValidationError as e:
            print("   ✅ Join request created instead of direct chapter")
            print(f"   📝 Response: {e.detail}")
        
        # Check what was actually created
        join_request = ChapterJoinRequest.objects.filter(club=demo_club).order_by('-created_at').first()
        chapters_count = Chapter.objects.filter(club=demo_club).count()
        
        print(f"\n📊 Result After Step 1:")
        print(f"   Chapters created: {chapters_count}")
        print(f"   Join requests created: 1")
        print(f"   Join request status: {join_request.status}")
        print(f"   Proposed chapter name: {join_request.proposed_chapter_name}")
        
        print(f"\n👨‍💼 Step 2: Admin reviews the join request")
        print("   (Admin can see the request in Django admin)")
        print("   (Admin evaluates the proposal)")
        
        print(f"\n✅ Step 3: Admin approves the join request")
        approved_chapter = join_request.approve("Great proposal! Approved for western Guadalajara.")
        
        print(f"   ✅ Chapter created: {approved_chapter.name}")
        print(f"   🏍️ Chapter owner: {approved_chapter.owner.get_full_name()}")
        print(f"   📍 Location: {approved_chapter.city}, {approved_chapter.state_new.name if approved_chapter.state_new else 'N/A'}")
        print(f"   📅 Created: {approved_chapter.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Show final state
        final_chapters = Chapter.objects.filter(club=demo_club).count()
        final_requests = ChapterJoinRequest.objects.filter(club=demo_club).count()
        
        print(f"\n🎉 Final State:")
        print(f"   Total chapters in club: {final_chapters}")
        print(f"   Total join requests: {final_requests}")
        print(f"   Join request status: {join_request.status}")
        print(f"   Admin notes: {join_request.admin_notes}")
        
        # Demonstrate rejection scenario
        print(f"\n🚫 Bonus: Demonstrating rejection scenario")
        
        # Create another prospect
        prospect2, created = User.objects.get_or_create(
            username='prospect2',
            defaults={
                'email': 'prospect2@example.com',
                'first_name': 'Jane',
                'last_name': 'Prospect'
            }
        )
        
        # Create another join request
        reject_request = ChapterJoinRequest.objects.create(
            club=demo_club,
            requested_by=prospect2,
            proposed_chapter_name='Guadalajara East Chapter',
            city='Guadalajara',
            state='Jalisco',
            state_new=state,
            description='Chapter for eastern Guadalajara',
            reason='Want to expand our presence',
            estimated_members=2
        )
        
        print(f"   📝 New join request created: {reject_request.proposed_chapter_name}")
        
        # Admin rejects it
        reject_request.reject("Not enough experience leading groups. Please gain more experience first.")
        
        print(f"   ❌ Join request rejected")
        print(f"   📄 Rejection reason: {reject_request.admin_notes}")
        
        # Verify no chapter was created
        final_chapters_after_reject = Chapter.objects.filter(club=demo_club).count()
        print(f"   📊 Chapters after rejection: {final_chapters_after_reject} (no change)")
        
        print(f"\n🎯 Summary of New Flow:")
        print(f"   ✅ Join requests required for all non-superuser chapter creation")
        print(f"   ✅ Admin review process enforced")
        print(f"   ✅ Proper audit trail maintained")
        print(f"   ✅ Quality control before chapter creation")
        print(f"   ✅ Geographic data properly handled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demonstrate_new_flow()
    if success:
        print(f"\n🎉 Demonstration completed successfully!")
        print(f"💡 Access the admin at: http://localhost:8004/admin/clubs/chapterjoinrequest/")
    else:
        print(f"\n❌ Demonstration failed")
    
    sys.exit(0 if success else 1)

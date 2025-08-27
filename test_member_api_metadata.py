#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from clubs.models import Member
from clubs.serializers import MemberSerializer

def test_member_api_metadata():
    """Test that the member API returns metadata"""
    print("🔧 Testing Member API Metadata...")
    
    try:
        # Get a copilot member with metadata
        copilot = Member.objects.filter(
            member_type='copilot',
            metadata__isnull=False
        ).first()
        
        if copilot:
            print(f"✅ Found copilot: {copilot.first_name} {copilot.last_name}")
            print(f"✅ Metadata in model: {copilot.metadata}")
            
            # Test serializer
            serializer = MemberSerializer(copilot)
            serialized_data = serializer.data
            
            print(f"✅ Serialized fields: {list(serialized_data.keys())}")
            
            if 'metadata' in serialized_data:
                print(f"✅ Metadata in API response: {serialized_data['metadata']}")
            else:
                print("❌ Metadata field missing from API response")
                
            # Test with multiple members
            print("\n🔧 Testing with queryset...")
            members = Member.objects.filter(chapter=copilot.chapter)[:3]
            serializer = MemberSerializer(members, many=True)
            
            for i, member_data in enumerate(serializer.data):
                member = members[i]
                print(f"Member {member.first_name}: metadata in response = {'metadata' in member_data}")
                if 'metadata' in member_data:
                    print(f"  Metadata: {member_data['metadata']}")
                    
        else:
            print("ℹ️  No copilot members with metadata found")
            
            # Test with any member
            any_member = Member.objects.first()
            if any_member:
                print(f"✅ Testing with any member: {any_member.first_name} {any_member.last_name}")
                serializer = MemberSerializer(any_member)
                print(f"✅ Serialized fields: {list(serializer.data.keys())}")
                
                if 'metadata' in serializer.data:
                    print(f"✅ Metadata in response: {serializer.data['metadata']}")
                else:
                    print("❌ Metadata field missing from API response")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_member_api_metadata()

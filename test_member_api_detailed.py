#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')
django.setup()

from django.test import Client
from clubs.models import Member
from clubs.serializers import MemberSerializer
import json

def test_member_api_detailed():
    """Detailed test of the member API response"""
    print("🔧 Testing Member API Response...")
    
    try:
        # Test 1: Direct serializer test
        print("\n1️⃣ Testing MemberSerializer directly...")
        member = Member.objects.first()
        if member:
            serializer = MemberSerializer(member)
            data = serializer.data
            print(f"✅ Member: {member.first_name} {member.last_name}")
            print(f"✅ Fields in serializer: {list(data.keys())}")
            print(f"✅ Metadata in serializer: {'metadata' in data}")
            if 'metadata' in data:
                print(f"✅ Metadata value: {data['metadata']}")
        else:
            print("❌ No members found")
            return
        
        # Test 2: Test client test
        print("\n2️⃣ Testing API endpoint with test client...")
        client = Client()
        response = client.get('/api/members/')
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Response type: {type(data)}")
                
                if isinstance(data, list) and data:
                    first_member = data[0]
                    print(f"✅ First member fields: {list(first_member.keys())}")
                    print(f"✅ Metadata in response: {'metadata' in first_member}")
                    if 'metadata' in first_member:
                        print(f"✅ Metadata value: {first_member['metadata']}")
                elif isinstance(data, dict) and 'results' in data:
                    results = data['results']
                    if results:
                        first_member = results[0]
                        print(f"✅ First member fields: {list(first_member.keys())}")
                        print(f"✅ Metadata in response: {'metadata' in first_member}")
                        if 'metadata' in first_member:
                            print(f"✅ Metadata value: {first_member['metadata']}")
                    else:
                        print("❌ No results in paginated response")
                else:
                    print(f"❌ Unexpected response format: {data}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Response content: {response.content.decode()[:200]}")
        else:
            print(f"❌ Error response: {response.content.decode()[:200]}")
        
        # Test 3: Test specific member with metadata
        print("\n3️⃣ Testing copilot member with metadata...")
        copilot = Member.objects.filter(member_type='copilot', metadata__isnull=False).first()
        if copilot:
            print(f"✅ Found copilot: {copilot.first_name} {copilot.last_name}")
            print(f"✅ Model metadata: {copilot.metadata}")
            
            # Test serializer for this specific member
            serializer = MemberSerializer(copilot)
            print(f"✅ Serializer metadata: {serializer.data.get('metadata', 'NOT FOUND')}")
            
            # Test API for this specific member
            response = client.get(f'/api/members/{copilot.id}/')
            if response.status_code == 200:
                member_data = response.json()
                print(f"✅ API metadata for copilot: {member_data.get('metadata', 'NOT FOUND')}")
            else:
                print(f"❌ Error getting specific member: {response.content.decode()}")
        else:
            print("ℹ️  No copilot members with metadata found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_member_api_detailed()

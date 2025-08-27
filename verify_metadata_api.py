#!/usr/bin/env python
"""
Quick test to verify the metadata field is working in the API
"""
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

# Simple verification
try:
    print("=== MEMBER API METADATA TEST ===")
    
    # Get a member with metadata
    member = Member.objects.filter(metadata__isnull=False).first()
    if not member:
        member = Member.objects.first()
    
    print(f"Testing member: {member.first_name} {member.last_name}")
    print(f"Database metadata: {member.metadata}")
    
    # Test the serializer
    serializer = MemberSerializer(member)
    
    # Check if metadata is in the serialized data
    if 'metadata' in serializer.data:
        print("✅ SUCCESS: 'metadata' field is present in the API serializer")
        print(f"API metadata value: {serializer.data['metadata']}")
    else:
        print("❌ ERROR: 'metadata' field is missing from the API serializer")
        print(f"Available fields: {list(serializer.data.keys())}")
        
except Exception as e:
    print(f"Error: {e}")

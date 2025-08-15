#!/usr/bin/env python3
"""
Simple script to test API access without JWT authentication
"""

import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test an API endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - Accessible without authentication")
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"📊 Found {len(data)} items")
                    if data:
                        print(f"📋 Sample item keys: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"📋 Response keys: {list(data.keys())}")
                    if 'results' in data:
                        print(f"📊 Found {len(data['results'])} items in results")
            except json.JSONDecodeError:
                print("📄 Response is not JSON")
                print(f"Content preview: {response.text[:200]}...")
        elif response.status_code == 401:
            print("🔒 AUTHENTICATION REQUIRED - JWT needed")
        elif response.status_code == 403:
            print("🚫 FORBIDDEN - No permission")
        elif response.status_code == 404:
            print("❌ NOT FOUND - Endpoint doesn't exist")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Server not running on localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Server taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    return True

def main():
    print("🚀 Testing Motomundo API Access")
    print("=" * 50)
    
    # Test various endpoints
    endpoints = [
        ("/healthz", "Health Check"),
        ("/api/clubs/", "Clubs API"),
        ("/api/chapters/", "Chapters API"), 
        ("/api/members/", "Members API"),
        ("/api/achievements/", "Achievements API"),
        ("/api/achievements/achievements/", "Achievements List"),
        ("/api/achievements/user-achievements/", "User Achievements"),
        ("/api/users/", "Users API"),
        ("/api/dashboard/", "Dashboard API"),
    ]
    
    # Check if server is running first
    if not test_endpoint("/healthz", "Health Check"):
        print("\n❌ Server appears to be down. Please start the server with:")
        print("   docker-compose up")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    for endpoint, description in endpoints[1:]:  # Skip health check since we already tested it
        test_endpoint(endpoint, description)
    
    print("\n" + "=" * 50)
    print("📝 Summary:")
    print("- ✅ = Accessible without authentication")
    print("- 🔒 = Requires JWT authentication") 
    print("- 🚫 = Forbidden")
    print("- ❌ = Not found or error")
    print("=" * 50)

if __name__ == "__main__":
    main()

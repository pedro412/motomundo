#!/usr/bin/env python3
"""
Test script for JWT and Token authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_jwt_endpoints():
    print("🚀 Testing JWT Authentication Endpoints")
    print("=" * 50)
    
    # Test JWT Registration
    print("\n1. Testing JWT Registration...")
    registration_data = {
        "username": "jwt_test_user",
        "email": "jwt_test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "JWT",
        "last_name": "Test"
    }
    
    response = requests.post(f"{BASE_URL}/jwt/register/", json=registration_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ JWT Registration successful!")
        print(f"Access Token: {data['access'][:50]}...")
        print(f"Refresh Token: {data['refresh'][:50]}...")
        print(f"User: {data['user']['username']} ({data['user']['email']})")
        print(f"Permissions: {data['permissions']}")
        
        access_token = data['access']
        refresh_token = data['refresh']
    else:
        print(f"❌ JWT Registration failed: {response.text}")
        return
    
    # Test JWT Login
    print("\n2. Testing JWT Login...")
    login_data = {
        "username": "harley_admin",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/jwt/login/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ JWT Login successful!")
        print(f"Access Token: {data['access'][:50]}...")
        print(f"User: {data['user']['username']}")
        print(f"Permissions: {data['permissions']}")
        
        admin_access_token = data['access']
        admin_refresh_token = data['refresh']
    else:
        print(f"❌ JWT Login failed: {response.text}")
        return
    
    # Test JWT Token Refresh
    print("\n3. Testing JWT Token Refresh...")
    refresh_data = {"refresh": admin_refresh_token}
    
    response = requests.post(f"{BASE_URL}/jwt/refresh/", json=refresh_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ JWT Token refresh successful!")
        print(f"New Access Token: {data['access'][:50]}...")
    else:
        print(f"❌ JWT Token refresh failed: {response.text}")
    
    # Test accessing protected API with JWT
    print("\n4. Testing API access with JWT...")
    headers = {"Authorization": f"Bearer {admin_access_token}"}
    
    response = requests.get("http://localhost:8000/api/clubs/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API access with JWT successful!")
        print(f"Found {len(data['results'])} clubs")
    else:
        print(f"❌ API access with JWT failed: {response.text}")
    
    # Test JWT Logout
    print("\n5. Testing JWT Logout...")
    logout_data = {"refresh": admin_refresh_token}
    
    response = requests.post(f"{BASE_URL}/jwt/logout/", json=logout_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ JWT Logout successful!")
    else:
        print(f"❌ JWT Logout failed: {response.text}")

def test_token_endpoints():
    print("\n\n🔑 Testing Token Authentication Endpoints")
    print("=" * 50)
    
    # Test Token Login
    print("\n1. Testing Token Login...")
    login_data = {
        "username": "harley_admin",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Token Login successful!")
        print(f"Token: {data['token'][:20]}...")
        print(f"User: {data['user']['username']}")
        
        token = data['token']
    else:
        print(f"❌ Token Login failed: {response.text}")
        return
    
    # Test accessing protected API with Token
    print("\n2. Testing API access with Token...")
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.get("http://localhost:8000/api/clubs/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API access with Token successful!")
        print(f"Found {len(data['results'])} clubs")
    else:
        print(f"❌ API access with Token failed: {response.text}")

if __name__ == "__main__":
    try:
        test_jwt_endpoints()
        test_token_endpoints()
        print("\n🎉 All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

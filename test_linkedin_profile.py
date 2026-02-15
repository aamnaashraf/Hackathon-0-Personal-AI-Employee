#!/usr/bin/env python3
"""Test different LinkedIn API endpoints to find correct member URN"""
import os
import requests
import dotenv

dotenv.load_dotenv()

access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
api_url = 'https://api.linkedin.com/v2/'

headers = {
    'Authorization': f'Bearer {access_token}',
    'X-Restli-Protocol-Version': '2.0.0'
}

print("=== Testing LinkedIn API Endpoints ===\n")

# Test 1: /me endpoint
print("1. Testing /v2/me endpoint:")
response = requests.get(f"{api_url}me", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Response: {data}")
    if 'id' in data:
        print(f"   ✓ Member ID: {data['id']}")
        print(f"   ✓ Correct URN: urn:li:person:{data['id']}")
else:
    print(f"   ✗ Error: {response.text}")

# Test 2: /userinfo endpoint (OpenID Connect)
print("\n2. Testing /v2/userinfo endpoint:")
response = requests.get(f"{api_url}userinfo", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Response: {data}")
    print(f"   Sub ID: {data.get('sub')}")

# Test 3: Try to introspect token permissions
print("\n3. Checking token scopes:")
print("   Note: LinkedIn doesn't provide a direct introspection endpoint")
print("   You need to verify scopes in the LinkedIn Developer Portal")

# Test 4: Try posting with different URN formats
print("\n4. Testing different URN formats:")
person_id_from_env = os.getenv('LINKEDIN_PERSON_ID', '').split(':')[-1]
print(f"   From .env: {person_id_from_env}")
print(f"   Format 1: urn:li:person:{person_id_from_env}")
print(f"   Format 2: urn:li:member:{person_id_from_env}")

# Test 5: Check if we can access profile with projection
print("\n5. Testing /v2/me with projection:")
projection_url = f"{api_url}me?projection=(id,localizedFirstName,localizedLastName)"
response = requests.get(projection_url, headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Response: {response.json()}")
else:
    print(f"   Error: {response.text}")

print("\n=== Recommendations ===")
print("If /me endpoint returns 403, your token is missing 'r_liteprofile' or 'r_basicprofile' scope")
print("For posting, you need 'w_member_social' scope")
print("\nRequired scopes for posting:")
print("  - r_liteprofile (or r_basicprofile)")
print("  - w_member_social")

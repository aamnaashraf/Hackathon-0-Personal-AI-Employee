#!/usr/bin/env python3
"""Test LinkedIn API authentication and get correct member ID"""
import os
import requests
import dotenv

dotenv.load_dotenv()

access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')

print(f"Testing LinkedIn API access...")
print(f"API URL: {api_url}")
print(f"Access Token (first 20 chars): {access_token[:20]}...")

# Test 1: Get user profile info
print("\n=== Test 1: GET /me ===")
headers = {
    'Authorization': f'Bearer {access_token}',
    'X-Restli-Protocol-Version': '2.0.0'
}

response = requests.get(f"{api_url}me", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nExtracted Member ID: {data.get('id')}")
    print(f"Correct URN format: urn:li:person:{data.get('id')}")
else:
    print("\n[ERROR] Failed to get profile info")

# Test 2: Try userinfo endpoint
print("\n=== Test 2: GET /userinfo ===")
response2 = requests.get(f"{api_url}userinfo", headers=headers)
print(f"Status Code: {response2.status_code}")
print(f"Response: {response2.text}")

# Test 3: Check token introspection
print("\n=== Test 3: Token Info ===")
print("If the above tests failed, the access token may be expired or invalid.")
print("You may need to regenerate the LinkedIn access token.")

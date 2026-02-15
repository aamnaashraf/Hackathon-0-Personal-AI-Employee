#!/usr/bin/env python3
"""
Test different URN formats for LinkedIn posting
"""
import os
import requests
import dotenv

dotenv.load_dotenv()

access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
api_url = 'https://api.linkedin.com/v2/'

# Get the sub ID from userinfo
headers = {
    'Authorization': f'Bearer {access_token}',
    'X-Restli-Protocol-Version': '2.0.0'
}

print("Getting user info...")
response = requests.get(f"{api_url}userinfo", headers=headers)
if response.status_code == 200:
    userinfo = response.json()
    sub_id = userinfo.get('sub')
    print(f"Sub ID: {sub_id}")
else:
    print("Failed to get userinfo")
    exit(1)

# Test post content
post_content = "Test post from Personal AI Employee"

# Try different URN formats
urn_formats = [
    f"urn:li:person:{sub_id}",
    f"urn:li:member:{sub_id}",
]

for author_urn in urn_formats:
    print(f"\n{'='*70}")
    print(f"Testing with author URN: {author_urn}")
    print('='*70)

    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers_post = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    response = requests.post(
        f"{api_url}ugcPosts",
        headers=headers_post,
        json=post_data
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code in [200, 201]:
        print(f"\n[SUCCESS] Post created with URN format: {author_urn}")
        break
    else:
        print(f"[FAILED] This URN format didn't work")

print("\n" + "="*70)
print("If all formats failed, the issue is likely:")
print("1. 'Share on LinkedIn' product not approved in your app")
print("2. Token doesn't have w_member_social scope")
print("3. Need to use LinkedIn API v3 (newer version)")
print("="*70)

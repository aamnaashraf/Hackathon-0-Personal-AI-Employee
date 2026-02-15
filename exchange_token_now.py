#!/usr/bin/env python3
"""Exchange LinkedIn authorization code for access token"""
import requests

# Your credentials
auth_code = "AQScurp1M4RbM0re-EDFDg8NsLHKbuZUg34VdDwRYhTxNVnIWAk6qriqBgcNv8agWRqTmwLBySk2oXR5Pwbx_269xc7qzPXIkP-OmtSuYb-485ZJtLdeO7PiplI_2HKgn-w7-_2AjjvwbeqZXRJybJsvlM9M-nm0w6kxLO9R_UuOGhcW0P5cjNYYyKzuwGBHYHKZqEF95w6Ypm7jM8E"
client_id = "86xugwmkxi2epn"
client_secret = "WPL_AP1.BjOEfv6JZSpMnBSO.HpJTPQ=="
redirect_uri = "https://www.linkedin.com/developers/tools/oauth/redirect"

print("=" * 70)
print("Exchanging Authorization Code for Access Token")
print("=" * 70)

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}

print("\nSending request to LinkedIn...")
response = requests.post(token_url, data=token_data)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in', 0)

    print("\n" + "=" * 70)
    print("[SUCCESS] Access Token Generated!")
    print("=" * 70)
    print(f"\nAccess Token:\n{access_token}")
    print(f"\nExpires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Update your .env file with:")
    print(f"   LINKEDIN_ACCESS_TOKEN={access_token}")
    print("\n2. Test the token:")
    print("   python test_linkedin_auth.py")
    print("\n3. Post to LinkedIn:")
    print("   python post_linkedin_from_approved.py")
    print("=" * 70)

else:
    print(f"\n[ERROR] Failed to get access token")
    print(f"Response: {response.text}")

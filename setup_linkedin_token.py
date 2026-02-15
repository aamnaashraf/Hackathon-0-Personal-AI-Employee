#!/usr/bin/env python3
"""
Step-by-step LinkedIn OAuth Token Generator
This script will guide you through getting the correct access token
"""
import webbrowser
import urllib.parse

print("=" * 70)
print("LinkedIn Access Token Setup Guide")
print("=" * 70)

print("\n[STEP 1] Create or Configure LinkedIn App")
print("-" * 70)
print("1. Go to: https://www.linkedin.com/developers/apps")
print("2. Click 'Create app' or select your existing app")
print("3. Fill in required details if creating new app:")
print("   - App name: Personal AI Employee")
print("   - LinkedIn Page: (select your company page or create one)")
print("   - App logo: (upload any image)")
print("   - Legal agreement: Check the box")

print("\n[STEP 2] Request API Access Products")
print("-" * 70)
print("1. In your app, go to the 'Products' tab")
print("2. Request access to: 'Share on LinkedIn'")
print("3. Request access to: 'Sign In with LinkedIn using OpenID Connect'")
print("4. Wait for approval (usually instant for personal use)")

print("\n[STEP 3] Configure OAuth 2.0 Settings")
print("-" * 70)
print("1. Go to the 'Auth' tab in your app")
print("2. Add Redirect URL: http://localhost:8080/callback")
print("   (or use: https://www.linkedin.com/developers/tools/oauth/redirect)")
print("3. Note down your:")
print("   - Client ID")
print("   - Client Secret")

print("\n[STEP 4] Verify OAuth 2.0 Scopes")
print("-" * 70)
print("Make sure these scopes are available (they should be after product approval):")
print("   [OK] openid")
print("   [OK] profile")
print("   [OK] email")
print("   [OK] w_member_social")
print("\nNote: 'w_member_social' is the key scope for posting!")

print("\n[STEP 5] Generate Authorization URL")
print("-" * 70)

# You need to fill these in
CLIENT_ID = input("\nEnter your LinkedIn App Client ID: ").strip()
REDIRECT_URI = "http://localhost:8080/callback"

if not CLIENT_ID or CLIENT_ID == "":
    print("\n[ERROR] Client ID is required!")
    exit(1)

# Build authorization URL
auth_params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'openid profile email w_member_social'
}

auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(auth_params)}"

print("\n[STEP 6] Authorize the App")
print("-" * 70)
print("Opening browser to authorize your app...")
print(f"\nAuthorization URL:\n{auth_url}\n")

try:
    webbrowser.open(auth_url)
    print("[OK] Browser opened")
except:
    print("[ERROR] Could not open browser automatically")
    print(f"Please manually open this URL:\n{auth_url}")

print("\n[STEP 7] Get Authorization Code")
print("-" * 70)
print("After authorizing, you'll be redirected to:")
print(f"{REDIRECT_URI}?code=AUTHORIZATION_CODE&state=...")
print("\nCopy the 'code' parameter from the URL")

auth_code = input("\nPaste the authorization code here: ").strip()

if not auth_code:
    print("\n[ERROR] Authorization code is required!")
    exit(1)

print("\n[STEP 8] Exchange Code for Access Token")
print("-" * 70)

CLIENT_SECRET = input("Enter your LinkedIn App Client Secret: ").strip()

if not CLIENT_SECRET:
    print("\n[ERROR] Client Secret is required!")
    exit(1)

import requests

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
}

print("\nRequesting access token...")
response = requests.post(token_url, data=token_data)

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in')

    print("\n" + "=" * 70)
    print("SUCCESS! Access Token Generated")
    print("=" * 70)
    print(f"\nAccess Token:\n{access_token}")
    print(f"\nExpires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")

    print("\n[STEP 9] Update .env File")
    print("-" * 70)
    print("Add this line to your .env file:")
    print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")

    print("\n[STEP 10] Test the Token")
    print("-" * 70)
    print("Run: python test_linkedin_auth.py")
    print("The /me endpoint should now return 200 OK")

else:
    print(f"\n[ERROR] Failed to get access token")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print("\nCommon issues:")
    print("- Authorization code expired (they expire quickly, try again)")
    print("- Wrong Client ID or Client Secret")
    print("- Redirect URI mismatch")

print("\n" + "=" * 70)

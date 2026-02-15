#!/usr/bin/env python3
"""
LinkedIn Token Generator - Step by Step
Run each step separately with your credentials
"""
import sys
import urllib.parse
import requests

def step1_generate_auth_url(client_id):
    """Generate the authorization URL"""
    redirect_uri = "http://localhost:8080/callback"
    scopes = "openid profile email w_member_social"

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scopes
    }

    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

    print("=" * 70)
    print("STEP 1: Authorization URL Generated")
    print("=" * 70)
    print(f"\n1. Open this URL in your browser:\n\n{auth_url}\n")
    print("2. Authorize the app")
    print("3. You'll be redirected to: http://localhost:8080/callback?code=...")
    print("4. Copy the 'code' parameter from the URL")
    print("\nThen run: python linkedin_token_step2.py YOUR_CODE YOUR_CLIENT_ID YOUR_CLIENT_SECRET")
    print("=" * 70)

def step2_exchange_code(auth_code, client_id, client_secret):
    """Exchange authorization code for access token"""
    redirect_uri = "http://localhost:8080/callback"

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    print("\n" + "=" * 70)
    print("STEP 2: Exchanging Code for Access Token")
    print("=" * 70)
    print("Requesting access token from LinkedIn...")

    response = requests.post(token_url, data=token_data)

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get('access_token')
        expires_in = token_info.get('expires_in', 0)

        print("\n[SUCCESS] Access Token Generated!")
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

        return access_token
    else:
        print(f"\n[ERROR] Failed to get access token")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nCommon issues:")
        print("- Authorization code expired (get a new one)")
        print("- Wrong Client ID or Client Secret")
        print("- Redirect URI mismatch")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  Step 1: python linkedin_token_generator.py step1 YOUR_CLIENT_ID")
        print("  Step 2: python linkedin_token_generator.py step2 AUTH_CODE CLIENT_ID CLIENT_SECRET")
        print("\nExample:")
        print("  python linkedin_token_generator.py step1 86abc123xyz")
        print("  python linkedin_token_generator.py step2 AQT9x... 86abc123xyz your_secret")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "step1":
        if len(sys.argv) < 3:
            print("[ERROR] Client ID required")
            print("Usage: python linkedin_token_generator.py step1 YOUR_CLIENT_ID")
            sys.exit(1)
        client_id = sys.argv[2]
        step1_generate_auth_url(client_id)

    elif command == "step2":
        if len(sys.argv) < 5:
            print("[ERROR] Missing parameters")
            print("Usage: python linkedin_token_generator.py step2 AUTH_CODE CLIENT_ID CLIENT_SECRET")
            sys.exit(1)
        auth_code = sys.argv[2]
        client_id = sys.argv[3]
        client_secret = sys.argv[4]
        step2_exchange_code(auth_code, client_id, client_secret)

    else:
        print(f"[ERROR] Unknown command: {command}")
        print("Valid commands: step1, step2")

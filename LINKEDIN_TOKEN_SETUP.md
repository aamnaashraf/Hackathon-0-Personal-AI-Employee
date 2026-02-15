# LinkedIn Token Setup - Quick Reference

## Problem
Your current LinkedIn access token is missing the required OAuth scopes to post content.

## Current Status
- ✓ Token is valid
- ✓ Can access `/userinfo` endpoint
- ✗ Cannot access `/me` endpoint (missing `profile` scope)
- ✗ Cannot post content (missing `w_member_social` scope)

## Required OAuth 2.0 Scopes
To post on LinkedIn, you need ALL of these scopes:
1. `openid` - Basic OpenID Connect
2. `profile` - Access profile information (replaces deprecated r_liteprofile)
3. `email` - Access email address
4. `w_member_social` - **CRITICAL: Required to post content**

## Two Options to Get Proper Token

### Option 1: Use the Automated Script (Recommended)
```bash
cd Hackathon-0-FTE-s-
python setup_linkedin_token.py
```
This script will guide you through the entire OAuth flow step-by-step.

### Option 2: Manual OAuth Flow

#### Step 1: Configure LinkedIn App
1. Go to https://www.linkedin.com/developers/apps
2. Create new app or select existing app
3. Go to **Products** tab
4. Request access to:
   - "Share on LinkedIn" (provides w_member_social scope)
   - "Sign In with LinkedIn using OpenID Connect" (provides profile scope)

#### Step 2: Get Authorization Code
Visit this URL (replace YOUR_CLIENT_ID):
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20email%20w_member_social
```

#### Step 3: Exchange Code for Token
After authorization, you'll get a code. Use curl or Postman:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

#### Step 4: Update .env
Copy the access_token from the response and update:
```
LINKEDIN_ACCESS_TOKEN=your_new_token_here
```

## Verification
After updating the token, test it:
```bash
python test_linkedin_auth.py
```

You should see:
- ✓ `/me` endpoint returns 200 OK
- ✓ `/userinfo` endpoint returns 200 OK

## Then Retry Posting
```bash
python post_linkedin_from_approved.py
```

## Important Notes
- Access tokens expire (usually 60 days)
- You need a LinkedIn Company Page to create an app
- Personal accounts can post via `w_member_social` scope
- The scope `w_member_social` is ONLY available after "Share on LinkedIn" product is approved

## Troubleshooting
- **403 on /me**: Missing `profile` scope
- **403 on posting**: Missing `w_member_social` scope
- **Invalid redirect_uri**: Must match exactly what's configured in app
- **Code expired**: Authorization codes expire in ~10 minutes, get a new one

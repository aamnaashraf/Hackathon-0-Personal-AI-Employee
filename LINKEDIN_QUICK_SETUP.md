# LinkedIn Token Setup - Simple Instructions

## What You Need
1. LinkedIn App Client ID
2. LinkedIn App Client Secret

## Where to Get Them
1. Go to: https://www.linkedin.com/developers/apps
2. Select your app (or create one)
3. Make sure "Share on LinkedIn" product is approved
4. Go to "Auth" tab
5. Copy your Client ID and Client Secret

## Step-by-Step Process

### Step 1: Generate Authorization URL
Run this command with YOUR Client ID:
```bash
python linkedin_token_generator.py step1 YOUR_CLIENT_ID
```

This will output an authorization URL. Open it in your browser.

### Step 2: Authorize the App
- Click "Allow" to authorize
- You'll be redirected to: `http://localhost:8080/callback?code=XXXXXX`
- Copy the `code` parameter from the URL

### Step 3: Exchange Code for Token
Run this command with your authorization code, Client ID, and Client Secret:
```bash
python linkedin_token_generator.py step2 YOUR_AUTH_CODE YOUR_CLIENT_ID YOUR_CLIENT_SECRET
```

### Step 4: Update .env File
The script will output your access token. Copy it and update your .env file:
```
LINKEDIN_ACCESS_TOKEN=your_new_token_here
```

### Step 5: Test and Post
```bash
python test_linkedin_auth.py
python post_linkedin_from_approved.py
```

## Quick Example
```bash
# Step 1
python linkedin_token_generator.py step1 86abc123xyz

# (Open URL, authorize, get code)

# Step 2
python linkedin_token_generator.py step2 AQT9x...code...xyz 86abc123xyz your_secret_here
```

## Important Notes
- Authorization codes expire in ~10 minutes
- Make sure "Share on LinkedIn" product is approved in your app
- The redirect URI must be: http://localhost:8080/callback
- Access tokens expire after 60 days

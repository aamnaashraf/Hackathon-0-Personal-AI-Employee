# Twitter/X Personal Poster - Quick Setup Guide

## Overview
Posts to your personal Twitter/X profile using browser automation (FREE - no paid API needed).

## Features
- **Session Persistence**: Login once, auto-login forever
- **Privacy-First**: No credentials in code, manual login only
- **2FA Support**: Works with two-factor authentication
- **Local Storage**: Session saved to `./twitter_session.json`

## First-Time Setup

### 1. Install Dependencies
```bash
pip install playwright python-dotenv
playwright install chromium
```

### 2. First Run (Manual Login)
```bash
python twitter_personal_poster.py
```

**What happens:**
1. Browser opens (visible mode)
2. Twitter/X login page appears
3. You manually login (username, password, 2FA if needed)
4. Wait for home feed to load
5. Press Enter in terminal
6. Session saved to `twitter_session.json`
7. Script posts approved content

### 3. Subsequent Runs (Auto-Login)
```bash
python twitter_personal_poster.py
```

**What happens:**
1. Browser opens
2. Auto-logs in using saved session (no manual steps!)
3. Posts approved content
4. Done!

## Workflow

### Create a Twitter Post Draft
1. Create file in `AI_Employee_Vault/Approved/` folder
2. Name it: `X_POST_<description>_<date>.md`
3. Content format:
```markdown
---
type: twitter_post
status: approved
created: 2026-02-13
---

Your tweet content here (max 280 characters)

Can be multiple lines if needed.
```

### Run the Poster
```bash
python twitter_personal_poster.py
```

The script will:
- Find all `X_POST_*.md` files in Approved folder
- Auto-login to Twitter/X
- Post each one
- Move completed posts to Done folder
- Update Dashboard.md

## Session Management

### Session File Location
Default: `./twitter_session.json`

Custom location via environment variable:
```bash
# In .env file
TWITTER_SESSION_PATH=./my_custom_session.json
```

### Reset Session (Force Re-Login)
```bash
# Delete the session file
rm twitter_session.json

# Or on Windows
del twitter_session.json
```

Next run will prompt for manual login again.

## Claude Prompt to Trigger

Use this prompt with Claude Code:

```
Post this draft to my personal Twitter/X profile using Playwright:

[Your tweet content here]

Use the twitter_personal_poster.py script with session persistence.
```

Or simply:

```
Run the Twitter poster to publish approved X_POST drafts
```

## Troubleshooting

### "Login verification failed"
- Make sure you're on the Twitter/X home feed before pressing Enter
- Wait 5-10 seconds after login completes
- Check that you see the "Home" timeline

### Session not saving
- Check file permissions on `twitter_session.json`
- Make sure the script has write access to the directory
- Try running with elevated permissions if needed

### Auto-login not working
- Delete `twitter_session.json` and login again
- Twitter may have invalidated the session (security reasons)
- Check that the session file exists and is not empty

### Browser doesn't open
- Make sure Playwright is installed: `playwright install chromium`
- Check that chromium browser was downloaded successfully
- Try running: `playwright install --force chromium`

## Privacy & Security

✓ No credentials stored in code or .env
✓ Session state saved locally (cookies, localStorage)
✓ Manual login only - you control your credentials
✓ Browser runs in visible mode (you see everything)
✓ Session file is local JSON (not uploaded anywhere)

## Advanced Configuration

### Environment Variables (.env)
```bash
# Vault location
VAULT_PATH=E:/hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault

# Session file location
TWITTER_SESSION_PATH=./twitter_session.json
```

### Headless Mode (Not Recommended)
To run in headless mode (no visible browser):
```python
# In twitter_personal_poster.py, line ~316
browser = p.chromium.launch(
    headless=True,  # Change to True
    args=['--start-maximized']
)
```

**Warning**: Headless mode may trigger Twitter's bot detection. Use visible mode for reliability.

## Integration with AI Employee System

The script integrates with the AI Employee Vault workflow:

1. AI drafts Twitter post → `Needs_Action/X_POST_*.md`
2. Human reviews → moves to `Pending_Approval/`
3. Human approves → moves to `Approved/`
4. Script runs → posts and moves to `Done/`
5. Dashboard updated automatically

## Demo Script

For live demos:
```bash
# 1. Create a test post
echo "🚀 Testing my AI Employee Twitter automation! #AI #Automation" > AI_Employee_Vault/Approved/X_POST_demo_20260213.md

# 2. Run the poster
python twitter_personal_poster.py

# 3. Watch it post automatically!
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the script output for error messages
- Ensure Playwright and dependencies are up to date

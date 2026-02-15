# Facebook Personal Profile Poster - Setup Guide

## Overview
Since Meta Graph API only allows posting to Pages (not personal profiles), this tool uses Playwright browser automation to post to your personal Facebook profile.

**Key Feature:** Manual login only - no credentials stored anywhere!

## Prerequisites

1. **Install Playwright**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Session Storage** (automatic)
   - No credentials needed in `.env` file
   - Login manually in browser (first time only)
   - Session is saved to `./facebook_session/` folder
   - Future runs will reuse the saved session

## How It Works

1. **Reads approved posts** from `AI_Employee_Vault/Approved/` folder
   - Looks for files matching `FB_POST_*.md`

2. **Opens browser in visible mode** (headless=False)
   - Uses saved session from `facebook_session/` folder
   - If no session exists, prompts you to login manually in the browser
   - **No credentials stored** - completely manual login for security

3. **Posts to your personal profile**
   - Navigates to Facebook home
   - Clicks "What's on your mind" box
   - Types the post content
   - Clicks "Post" button

4. **Moves completed posts** to `AI_Employee_Vault/Done/` folder

5. **Updates Dashboard.md** with activity log

## Usage

### Quick Start (Windows):
```bash
run_facebook_poster.bat
```

### Manual Run:
```bash
python facebook_personal_poster.py
```

### Create a post draft:
1. Create a file in `AI_Employee_Vault/Approved/` named `FB_POST_<topic>.md`
2. Add your post content (see example below)
3. Run the poster script

### Example Post Format:
```markdown
---
type: facebook_post
post_id: fb_post_demo
created: 2026-02-12
status: approved
---

# Facebook Post - Demo

🚀 Your post content here!

This is what will be posted to your personal Facebook profile.

#Hashtags #Work #Here
```

## Features

✅ **Session persistence** - Login once, reuse session
✅ **No credentials stored** - 100% manual login for security
✅ **Visible mode** - See what's happening in real-time
✅ **Manual fallback** - If automation fails, complete manually
✅ **Media support** - Can attach images/videos (manual step)
✅ **Safe workflow** - Only posts from Approved folder
✅ **Activity logging** - Updates Dashboard.md automatically

## Security Notes

- **No credentials stored** - you login manually in the browser
- Browser session is saved locally in `facebook_session/` folder (cookies only)
- The browser runs in visible mode so you can monitor activity
- You can complete any step manually if automation fails
- Session folder should be added to `.gitignore` (already configured)

## Troubleshooting

**First-time login:**
- Browser will open to Facebook login page
- Login manually with your credentials
- Complete any 2FA or CAPTCHA challenges
- Press Enter in the terminal when done
- Session will be saved for next time

**Session expired:**
- If session expires, you'll be prompted to login again
- Just login manually and press Enter
- New session will be saved

**Post box not found:**
- Facebook's UI changes frequently
- Script will prompt you to click manually
- Paste content manually if needed

**Post button not found:**
- Click the "Post" button manually
- Press Enter when done

## Integration with Workflow

This tool integrates with your existing AI Employee system:

1. **Draft creation** → Create post in `Needs_Action/` or `Pending_Approval/`
2. **Approval** → Move to `Approved/` folder
3. **Posting** → Run `facebook_personal_poster.py`
4. **Completion** → File moves to `Done/`, Dashboard updates

## Demo Post

A sample post has been created at:
`AI_Employee_Vault/Approved/FB_POST_hackathon_demo.md`

Run the script to test it!

## First Run Instructions

1. Install Playwright:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. Run the poster:
   ```bash
   python facebook_personal_poster.py
   ```

3. When browser opens:
   - Login to Facebook manually
   - Complete any 2FA/CAPTCHA
   - Press Enter in terminal

4. Watch the automation:
   - Script will navigate to your profile
   - Type the post content
   - Click Post button

5. Done!
   - Post appears on your Facebook
   - File moves to Done folder
   - Dashboard gets updated

## Why Manual Login?

- **Security**: No credentials stored in files or environment variables
- **2FA Support**: Works with any authentication method Facebook requires
- **Privacy**: Your password never touches the script
- **Reliability**: No risk of credential-based automation detection
- **Flexibility**: Works even if Facebook changes login flow

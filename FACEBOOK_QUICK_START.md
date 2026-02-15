# Facebook Personal Poster - Quick Start

## ✅ Setup Complete!

All files are ready for your hackathon demo.

## What Was Created

1. **facebook_personal_poster.py** - Main script
2. **run_facebook_poster.bat** - Windows launcher
3. **FACEBOOK_PERSONAL_SETUP.md** - Full documentation
4. **FB_POST_hackathon_demo.md** - Sample post (in Approved folder)

## How to Use (3 Steps)

### Step 1: Run the Script
```bash
python facebook_personal_poster.py
```
Or double-click: `run_facebook_poster.bat`

### Step 2: Login to Facebook
- Browser will open automatically
- Login manually (first time only)
- Complete any 2FA/CAPTCHA
- Press Enter in terminal when done
- Session saves automatically for next time

### Step 3: Watch It Post
- Script navigates to Facebook home
- Types your post content
- Clicks "Post" button
- Moves file to Done folder
- Updates Dashboard.md

## Demo Post Ready

Location: `AI_Employee_Vault/Approved/FB_POST_hackathon_demo.md`

Content preview:
```
🚀 Excited to share what I've been building at the hackathon!

I've created an AI-powered autonomous employee system that:
✅ Monitors emails, WhatsApp, and social media
✅ Drafts intelligent responses
✅ Posts to LinkedIn and Facebook automatically
...
```

## For Your Hackathon Demo

1. **Show the workflow:**
   - Draft in Needs_Action → Review → Move to Approved → Auto-post

2. **Highlight the tech:**
   - "Meta API only supports Pages, not personal profiles"
   - "So I built a Playwright automation that posts like a human"
   - "Manual login for security - no credentials stored"

3. **Live demo:**
   - Run the script
   - Show browser opening
   - Show it typing and posting
   - Show file moving to Done folder

## Create Your Own Posts

Just create a file in `Approved/` folder:

**Filename:** `FB_POST_<topic>.md`

**Content:**
```markdown
---
type: facebook_post
post_id: fb_post_<unique_id>
created: 2026-02-12
status: approved
---

Your post content here!

#Hashtags #Here
```

## Troubleshooting

**If automation fails:** Just complete manually in the browser and press Enter

**Session expires:** Login again manually, session will be saved

**Need help:** See FACEBOOK_PERSONAL_SETUP.md for full docs

---

Ready to demo! 🚀

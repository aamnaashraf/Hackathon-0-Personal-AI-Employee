# Instagram Personal Profile Poster - Quick Setup Guide

## Overview
This tool posts to your **personal Instagram profile** using Playwright browser automation. Meta Graph API only supports Business accounts, so we use browser automation for personal profiles.

## Features
- ✅ Posts to personal Instagram profile
- ✅ Visible browser mode (great for demos)
- ✅ Session persistence (login once, reuse session)
- ✅ Manual login (no credentials in code)
- ✅ Caption support
- ✅ Media upload support (photos/videos)
- ✅ Automatic workflow integration

## Prerequisites

1. **Python 3.8+** installed
2. **Playwright** installed:
   ```bash
   pip install playwright python-dotenv
   playwright install chromium
   ```

## Setup Steps

### 1. Configure Environment Variables

Edit `.env` file and ensure these lines exist:
```env
# Instagram Personal Profile (Playwright automation)
INSTAGRAM_SESSION_PATH=./instagram_session

# Vault path (should already be set)
VAULT_PATH=E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault
```

### 2. Create Instagram Post Draft

Create a file in `AI_Employee_Vault/Approved/` folder with naming pattern:
`INSTA_POST_<description>.md`

Example: `INSTA_POST_hackathon_demo.md`

**Draft Format:**
```markdown
---
type: instagram_post
status: approved
created: 2026-02-12
media: ./path/to/image.jpg
---

# Instagram Post

🚀 Exciting news! We're building an AI-powered autonomous employee system at the hackathon!

This system can:
✅ Monitor emails and messages
✅ Draft responses automatically
✅ Post to social media
✅ Handle approvals workflow

#AI #Automation #Hackathon #Innovation #TechDemo

Follow for more updates! 🔥
```

**Optional Media Field:**
- Add `media: ./path/to/image.jpg` in frontmatter to upload photo/video
- Supported formats: JPG, PNG, MP4, etc.
- Leave blank for text-only posts

### 3. Run the Poster

**Option A: Using Batch File (Windows)**
```bash
run_instagram_poster.bat
```

**Option B: Direct Python**
```bash
python instagram_personal_poster.py
```

### 4. First-Time Login

On first run:
1. Browser will open automatically (visible mode)
2. Navigate to Instagram login page
3. **Login manually** in the browser window
4. Press Enter in the terminal after logging in
5. Session will be saved for future use

### 5. Posting Process

The script will:
1. ✅ Open Instagram with saved session
2. ✅ Click "Create" button
3. ✅ Upload media (if specified)
4. ✅ Type caption automatically
5. ✅ Click "Share" button
6. ✅ Move completed post to `Done/` folder
7. ✅ Update Dashboard.md

## Workflow Integration

### Manual Workflow
1. Create draft in `Approved/INSTA_POST_*.md`
2. Run `run_instagram_poster.bat`
3. Check `Done/` folder for completed posts

### Automated Workflow
The script can be integrated with:
- Approval handler skill
- Scheduled tasks
- Orchestrator system

## File Naming Convention

Instagram posts must follow this pattern:
- `INSTA_POST_*.md` - Instagram posts
- `FB_POST_*.md` - Facebook posts (different script)
- `LINKEDIN_POST_*.md` - LinkedIn posts (different script)

## Troubleshooting

### Session Expired
- Delete `./instagram_session` folder
- Run script again and login manually
- New session will be saved

### Post Button Not Found
- Script will prompt for manual action
- Complete the step manually in browser
- Press Enter to continue

### Media Upload Failed
- Ensure file path is correct and absolute
- Supported formats: JPG, PNG, MP4
- File size limits apply (Instagram limits)

### Browser Doesn't Open
```bash
# Reinstall Playwright browsers
playwright install chromium
```

## Demo Tips

For hackathon demo:
1. Prepare 2-3 draft posts in advance
2. Use visible browser mode (already default)
3. Show session persistence (login once)
4. Demonstrate auto-typing caption
5. Show workflow: Approved → Done folder

## Security Notes

- ✅ No credentials stored in code
- ✅ Session files stored locally only
- ✅ Manual login required (secure)
- ✅ Session encrypted by browser
- ⚠️ Don't commit `instagram_session/` folder to Git

## Advanced Usage

### Batch Processing
Script automatically processes all `INSTA_POST_*.md` files in Approved folder.

### Custom Session Path
```env
INSTAGRAM_SESSION_PATH=./custom/path/instagram_session
```

### Integration with Other Scripts
```python
from instagram_personal_poster import InstagramPersonalPoster

poster = InstagramPersonalPoster()
poster.process_approved_posts()
```

## Support

For issues or questions:
- Check Instagram's posting limits (avoid spam)
- Ensure stable internet connection
- Verify Instagram account is not restricted

---

**Ready to post!** 🚀

Run `run_instagram_poster.bat` to start posting to Instagram!

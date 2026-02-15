---
name: instagram-poster
description: Posts content to personal Instagram profile using browser automation with approval workflow.
---

## Overview
This skill posts content to personal Instagram profiles using Playwright browser automation. Meta Graph API only supports Business accounts, so browser automation is required for personal profiles.

## When to Use
- When user wants to post to personal Instagram profile
- When creating social media content for Instagram
- When demonstrating Instagram automation in hackathon
- When Meta API is not available for personal accounts

## Parameters
- caption: Text content for the Instagram post
- media: (Optional) Path to image/video file
- hashtags: Relevant hashtags for the post

## Process
1. Generate engaging Instagram caption with emojis
2. Add relevant hashtags
3. Create draft in Approved folder as INSTA_POST_*.md
4. Run instagram_personal_poster.py to post via browser automation
5. Browser opens in visible mode (great for demos)
6. Auto-types caption and uploads media
7. Moves completed post to Done folder
8. Updates Dashboard with activity

## Technical Details
- Uses Playwright for browser automation
- Session persistence (login once, reuse forever)
- Visible browser mode for demonstrations
- Manual login required (no credentials in code)
- Supports photos, videos, and text-only posts

## File Format
```markdown
---
type: instagram_post
status: approved
created: 2026-02-12
media: ./path/to/image.jpg
---

# Instagram Post

Caption text with emojis 🚀

#hashtags #go #here
```

## Execution
```bash
python instagram_personal_poster.py
# or
run_instagram_poster.bat
```

## Integration
- Works with approval_handler skill
- Updates Dashboard automatically
- Session saved for future use
- Batch processing supported

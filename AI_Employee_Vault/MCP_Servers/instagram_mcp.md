# Instagram Personal Profile Poster - MCP Server Documentation

## Overview
Instagram Personal Profile Poster uses Playwright browser automation to post content to personal Instagram profiles. This is necessary because Meta Graph API only supports Instagram Business accounts, not personal profiles.

## Architecture

### Technology Stack
- **Playwright**: Browser automation framework
- **Chromium**: Browser engine for Instagram Web
- **Session Persistence**: Saves login session for reuse
- **Visible Mode**: Browser runs in visible mode (great for demos)

### Workflow
```
Approved/INSTA_POST_*.md → Instagram Poster → Instagram.com → Done/
```

## Configuration

### Environment Variables (.env)
```env
INSTAGRAM_SESSION_PATH=./instagram_session
VAULT_PATH=E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault
```

### Session Management
- Session stored in `./instagram_session/` directory
- Persistent across runs (login once, reuse forever)
- Manual login required (no credentials in code)
- Browser-encrypted session files

## File Format

### Instagram Post Draft
Location: `AI_Employee_Vault/Approved/INSTA_POST_*.md`

```markdown
---
type: instagram_post
status: approved
created: 2026-02-12
media: ./path/to/image.jpg  # Optional
---

# Instagram Post

Your caption text here with emojis 🚀

#hashtags #go #here

Multiple paragraphs supported.
```

### Frontmatter Fields
- `type`: Must be "instagram_post"
- `status`: Must be "approved" to process
- `created`: ISO date format
- `media`: (Optional) Path to image/video file

## Automation Flow

### 1. Post Creation
```python
# Read draft from Approved folder
draft = read_post_draft("INSTA_POST_demo.md")

# Extract caption and media
caption = extract_caption(draft)
media_path = extract_media_path(draft)

# Post to Instagram
post_to_instagram(caption, media_path)
```

### 2. Browser Automation Steps
1. Launch Chromium with persistent session
2. Navigate to instagram.com
3. Verify login status (or prompt manual login)
4. Click "Create" button
5. Select "Post" option
6. Upload media (if provided)
7. Click "Next" through editing screens
8. Fill caption text area
9. Click "Share" button
10. Wait for confirmation
11. Close browser

### 3. Post-Processing
- Move file from `Approved/` to `Done/`
- Update `Dashboard.md` with activity log
- Generate timestamp and summary

## API Reference

### InstagramPersonalPoster Class

#### Methods

**`__init__()`**
- Initializes poster with vault paths
- Creates necessary directories
- Sets up session path

**`login_to_instagram(page)`**
- Handles Instagram login flow
- Uses saved session if available
- Prompts for manual login if needed
- Returns: `bool` (success/failure)

**`post_to_profile(page, post_content, media_path=None)`**
- Posts content to Instagram profile
- Handles media upload if provided
- Auto-types caption
- Clicks Share button
- Returns: `bool` (success/failure)

**`read_post_draft(file_path)`**
- Reads markdown file
- Extracts caption from content
- Skips frontmatter and headers
- Returns: `str` (caption text)

**`extract_media_path(file_path)`**
- Extracts media path from frontmatter
- Validates file exists
- Returns: `str` or `None`

**`process_approved_posts()`**
- Main processing loop
- Finds all INSTA_POST_*.md files
- Posts each one sequentially
- Moves completed posts to Done

**`update_dashboard(filename, content_preview)`**
- Updates Dashboard.md
- Adds activity log entry
- Timestamps the action

**`run()`**
- Main entry point
- Prints banner
- Processes all approved posts
- Handles cleanup

## Usage Examples

### Basic Usage
```bash
# Run the poster
python instagram_personal_poster.py

# Or use batch file
run_instagram_poster.bat
```

### Programmatic Usage
```python
from instagram_personal_poster import InstagramPersonalPoster

poster = InstagramPersonalPoster()
poster.run()
```

### Integration with Approval Handler
```python
# In approval_handler skill
if filename.startswith("INSTA_POST_"):
    from instagram_personal_poster import InstagramPersonalPoster
    poster = InstagramPersonalPoster()
    poster.process_approved_posts()
```

## Selectors Reference

### Login Detection
- `svg[aria-label="Home"]` - Home icon
- `svg[aria-label="New post"]` - Create icon
- `a[href*="/direct/inbox"]` - Messages link

### Post Creation
- `svg[aria-label="New post"]` - Create button
- `span:has-text("Create")` - Create text
- `span:has-text("Post")` - Post option

### Media Upload
- `input[type="file"]` - File input
- `button:has-text("Next")` - Next button

### Caption Input
- `textarea[aria-label="Write a caption..."]` - Caption area
- `textarea[placeholder="Write a caption..."]` - Alternative

### Share Button
- `button:has-text("Share")` - Share button
- `div[role="button"]:has-text("Share")` - Alternative

## Error Handling

### Common Issues

**Session Expired**
- Detection: Login page appears
- Solution: Manual login prompt
- Prevention: Session refresh on each run

**Element Not Found**
- Detection: Timeout on selector
- Solution: Manual action prompt
- Fallback: User completes step manually

**Media Upload Failed**
- Detection: File input not found
- Solution: Manual file selection
- Validation: Check file exists and format

**Post Failed**
- Detection: No success confirmation
- Solution: Retry or manual completion
- Logging: Error logged to console

## Security Considerations

### Authentication
- ✅ No credentials stored in code
- ✅ Manual login required
- ✅ Session encrypted by browser
- ✅ Session files local only

### Data Privacy
- ✅ No data sent to external servers
- ✅ All processing local
- ✅ Session files not committed to Git
- ✅ Draft files remain in vault

### Rate Limiting
- Instagram has posting limits
- Script adds delays between posts
- Recommended: Max 5-10 posts per session
- Wait 10+ seconds between posts

## Troubleshooting

### Browser Doesn't Open
```bash
playwright install chromium
```

### Session Not Persisting
- Check `INSTAGRAM_SESSION_PATH` in .env
- Ensure directory has write permissions
- Delete session folder and re-login

### Selectors Not Working
- Instagram UI changes frequently
- Update selectors in script
- Use browser DevTools to find new selectors
- Fallback to manual actions

### Post Not Appearing
- Check Instagram app/website
- May take a few seconds to appear
- Check for Instagram restrictions
- Verify account not shadowbanned

## Performance

### Timing
- Login: 3-5 seconds (with session)
- Post creation: 10-15 seconds
- Media upload: +5-10 seconds
- Total per post: ~20-30 seconds

### Resource Usage
- Memory: ~200-300 MB (Chromium)
- CPU: Low (mostly waiting)
- Network: Minimal (Instagram API calls)
- Disk: ~100 MB (session files)

## Future Enhancements

### Potential Features
- [ ] Multi-image carousel support
- [ ] Video upload with thumbnail
- [ ] Story posting
- [ ] Reel posting
- [ ] Location tagging
- [ ] User tagging
- [ ] First comment automation
- [ ] Scheduled posting
- [ ] Analytics tracking

### API Limitations
- Personal profiles not supported by Meta API
- Browser automation required
- Subject to Instagram UI changes
- Rate limits apply

## Integration Points

### Approval Handler
- Monitors `Approved/INSTA_POST_*.md`
- Triggers Instagram poster
- Moves to Done on success

### Dashboard Updater
- Logs posting activity
- Updates recent activity section
- Timestamps all actions

### Orchestrator
- Can schedule Instagram posts
- Batch processing support
- Error recovery handling

## Maintenance

### Regular Tasks
- Update Playwright: `pip install -U playwright`
- Update browsers: `playwright install chromium`
- Check selector validity
- Monitor Instagram UI changes
- Review session security

### Monitoring
- Check Done folder for completed posts
- Review Dashboard.md for activity
- Monitor error logs
- Verify posts on Instagram

---

**Status**: Production Ready ✅
**Last Updated**: 2026-02-12
**Maintainer**: AI Employee System

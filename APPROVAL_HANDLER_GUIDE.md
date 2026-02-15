# Approval Handler - Automatic Social Media Integration

## Overview
The Approval Handler automatically monitors the `Approved/` folder and triggers the appropriate posting script when files are moved there. This creates a seamless workflow from draft → approval → automatic posting.

## Supported Actions

### 📸 Instagram Posts
- **Pattern**: `INSTA_POST_*.md`
- **Action**: Launches `instagram_personal_poster.py`
- **Browser**: Opens automatically in visible mode
- **Session**: Uses saved Instagram session
- **Result**: Posts to Instagram, moves file to Done/

### 📘 Facebook Posts
- **Pattern**: `FB_POST_*.md`
- **Action**: Launches `facebook_personal_poster.py`
- **Browser**: Opens automatically in visible mode
- **Session**: Uses saved Facebook session
- **Result**: Posts to Facebook, moves file to Done/

### 💼 LinkedIn Posts
- **Pattern**: `LINKEDIN_POST_*.md`
- **Action**: Runs `complete_linkedin_tasks.py`
- **API**: Uses LinkedIn API
- **Result**: Posts to LinkedIn, moves file to Done/

### 💬 WhatsApp Replies
- **Pattern**: `WHATSAPP_REPLY_*.md`
- **Action**: Logs for manual sending
- **Note**: Requires manual execution via `whatsapp_sender.py`

### 📧 Email Replies
- **Pattern**: `REPLY_APPROVED_*.md`
- **Action**: Logs for manual sending
- **Note**: Requires manual execution via `email_mcp.py`

## Installation

### Prerequisites
```bash
pip install playwright python-dotenv
playwright install chromium
```

### Environment Setup
Ensure `.env` file has:
```env
VAULT_PATH=E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault
INSTAGRAM_SESSION_PATH=./instagram_session
FACEBOOK_SESSION_PATH=./facebook_session
```

## Usage

### Continuous Monitoring (Recommended)
```bash
# Run the batch file
run_approval_handler.bat

# Or run Python directly
python approval_handler.py
```

This will:
- Monitor `Approved/` folder every 30 seconds
- Automatically detect file type
- Launch appropriate posting script
- Move completed files to `Done/`
- Log all actions

### Single Run (Process Once)
```bash
python approval_handler.py --once
```

This will:
- Scan `Approved/` folder once
- Process all pending files
- Exit after completion

## Workflow

### Complete Automation Flow
```
1. Draft created → Pending_Approval/
2. User reviews → Moves to Approved/
3. Approval Handler detects file
4. Identifies file type (Instagram/Facebook/LinkedIn)
5. Launches appropriate poster script
6. Browser opens (visible mode)
7. Auto-posts content
8. Moves file to Done/
9. Updates Dashboard.md
10. Logs action
```

### Example: Instagram Post
```
User: Creates INSTA_POST_demo.md in Pending_Approval/
User: Reviews and moves to Approved/
Handler: Detects INSTA_POST_demo.md
Handler: Launches instagram_personal_poster.py
Browser: Opens Instagram (already logged in)
Browser: Types caption automatically
Browser: Clicks Share button
Handler: Moves file to Done/
Handler: Updates Dashboard
Handler: Logs success
```

## File Detection Logic

The handler uses filename patterns to detect file types:

```python
INSTA_POST_*.md      → Instagram posting
FB_POST_*.md         → Facebook posting
LINKEDIN_POST_*.md   → LinkedIn posting
WHATSAPP_REPLY_*.md  → WhatsApp reply (manual)
REPLY_APPROVED_*.md  → Email reply (manual)
```

## Logging

All actions are logged to:
```
AI_Employee_Vault/Logs/YYYY-MM-DD_approval_handler.json
```

Log format:
```json
{
  "timestamp": "2026-02-12T22:30:00",
  "action_type": "instagram_post",
  "filename": "INSTA_POST_demo.md",
  "status": "success",
  "error": null
}
```

## Error Handling

### Session Expired
- Handler will prompt for manual login
- Session saved for future use
- Processing continues after login

### Browser Issues
- Handler falls back to manual prompts
- User can complete steps manually
- Processing marked as success after confirmation

### File Processing Errors
- Error logged to JSON log
- File remains in Approved/ folder
- Can be retried on next scan

## Configuration

### Change Scan Interval
Edit `approval_handler.py`:
```python
handler.run_continuous(interval=60)  # Check every 60 seconds
```

### Disable Specific File Types
Comment out processing in `process_file()` method:
```python
# if file_type == "instagram_post":
#     success = self.process_instagram_post(file_path)
```

## Integration with Orchestrator

### Add to Orchestrator
```python
# In orchestrator.py or orchestrator_gold.py
def start_approval_handler(self):
    """Start approval handler in background"""
    subprocess.Popen([
        sys.executable,
        "approval_handler.py"
    ])
```

### Startup Script
Create `startup.bat`:
```batch
@echo off
start "Approval Handler" run_approval_handler.bat
start "Gmail Watcher" python gmail_watcher.py
start "WhatsApp Watcher" python whatsapp_watcher.py
```

## Testing

### Test Instagram Integration
1. Create `AI_Employee_Vault/Approved/INSTA_POST_test.md`
2. Run `python approval_handler.py --once`
3. Verify browser opens and posts
4. Check file moved to Done/
5. Verify Dashboard updated

### Test Facebook Integration
1. Create `AI_Employee_Vault/Approved/FB_POST_test.md`
2. Run `python approval_handler.py --once`
3. Verify browser opens and posts
4. Check file moved to Done/
5. Verify Dashboard updated

### Test Continuous Monitoring
1. Run `run_approval_handler.bat`
2. Create test file in Approved/
3. Wait 30 seconds
4. Verify automatic processing
5. Press Ctrl+C to stop

## Troubleshooting

### Handler Not Detecting Files
- Check `VAULT_PATH` in .env
- Verify Approved/ folder exists
- Check file naming pattern matches

### Browser Not Opening
- Verify Playwright installed: `playwright install chromium`
- Check session path in .env
- Try deleting session folder and re-login

### Posts Not Appearing
- Check Instagram/Facebook for post
- May take a few seconds to appear
- Verify account not restricted
- Check logs for errors

### Multiple Browsers Opening
- Handler processes one file at a time
- Wait for first to complete
- Or use `--once` flag for single run

## Performance

### Resource Usage
- Memory: ~300-400 MB (with browser)
- CPU: Low (mostly idle)
- Network: Minimal
- Disk: ~200 MB (sessions)

### Timing
- Scan interval: 30 seconds (configurable)
- Instagram post: ~20-30 seconds
- Facebook post: ~20-30 seconds
- LinkedIn post: ~10-15 seconds

## Security

### Best Practices
- ✅ No credentials in code
- ✅ Manual login required
- ✅ Sessions encrypted by browser
- ✅ Session files local only
- ⚠️ Don't commit session folders to Git

### .gitignore Entries
```
instagram_session/
facebook_session/
whatsapp_session/
*.log
```

## Demo Tips

For hackathon demo:
1. Start handler before demo: `run_approval_handler.bat`
2. Show Approved/ folder with test posts
3. Demonstrate automatic detection
4. Show browser opening automatically
5. Watch auto-posting in real-time
6. Show file moving to Done/
7. Display Dashboard updates

## Future Enhancements

Potential features:
- [ ] Scheduled posting (time-based)
- [ ] Batch processing with delays
- [ ] Retry failed posts automatically
- [ ] Email notifications on success/failure
- [ ] Web dashboard for monitoring
- [ ] Multi-account support
- [ ] Analytics tracking

---

**Status**: Production Ready ✅
**Last Updated**: 2026-02-12
**Integration**: Instagram, Facebook, LinkedIn

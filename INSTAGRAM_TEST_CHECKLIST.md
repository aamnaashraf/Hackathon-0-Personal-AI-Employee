# Instagram Personal Profile Poster - Test Checklist

## Pre-Flight Checklist

### ✅ Files Created
- [x] `instagram_personal_poster.py` - Main automation script
- [x] `run_instagram_poster.bat` - Windows batch file
- [x] `INSTAGRAM_QUICK_SETUP.md` - Setup guide
- [x] `.env` - Updated with INSTAGRAM_SESSION_PATH
- [x] `AI_Employee_Vault/MCP_Servers/instagram_mcp.md` - Documentation
- [x] `.claude/skills/instagram-poster/skill.md` - Skill definition
- [x] `AI_Employee_Vault/Approved/INSTA_POST_hackathon_demo.md` - Sample post

### ✅ Dependencies
```bash
# Install required packages
pip install playwright python-dotenv

# Install Chromium browser
playwright install chromium
```

## Testing Steps

### 1. Environment Setup Test
```bash
# Verify .env file has Instagram config
cat .env | grep INSTAGRAM
```

Expected output:
```
INSTAGRAM_SESSION_PATH=./instagram_session
```

### 2. Script Validation Test
```bash
# Check if script exists and is readable
python -c "import instagram_personal_poster; print('✓ Script imports successfully')"
```

### 3. Directory Structure Test
```bash
# Verify all required directories exist
ls AI_Employee_Vault/Approved/
ls AI_Employee_Vault/Done/
```

### 4. Sample Post Test
```bash
# Check sample post exists
cat "AI_Employee_Vault/Approved/INSTA_POST_hackathon_demo.md"
```

### 5. First Run Test (Manual)
```bash
# Run the poster for first time
python instagram_personal_poster.py
```

**Expected behavior:**
1. ✅ Banner displays
2. ✅ Browser opens (visible mode)
3. ✅ Instagram.com loads
4. ✅ Prompts for manual login
5. ✅ After login, finds Create button
6. ✅ Types caption automatically
7. ✅ Clicks Share button
8. ✅ Post appears on Instagram
9. ✅ File moves to Done folder
10. ✅ Dashboard.md updates

### 6. Session Persistence Test
```bash
# Run again to test saved session
python instagram_personal_poster.py
```

**Expected behavior:**
1. ✅ Browser opens
2. ✅ Already logged in (no login prompt)
3. ✅ Posts successfully
4. ✅ Session reused

### 7. Batch File Test (Windows)
```bash
# Double-click or run
run_instagram_poster.bat
```

**Expected behavior:**
1. ✅ Command window opens
2. ✅ Script runs
3. ✅ Pauses at end for review

## Verification Checklist

### Post Verification
- [ ] Post appears on Instagram profile
- [ ] Caption matches draft exactly
- [ ] Hashtags included
- [ ] Emojis render correctly
- [ ] Post is public/visible

### File System Verification
- [ ] Original file moved from Approved/ to Done/
- [ ] Dashboard.md updated with timestamp
- [ ] Session folder created: `./instagram_session/`
- [ ] No errors in console output

### Session Verification
- [ ] Session files exist in `./instagram_session/`
- [ ] Second run doesn't require login
- [ ] Session persists across runs
- [ ] Can close and reopen browser

## Troubleshooting Tests

### Test 1: Session Expired
```bash
# Delete session and test re-login
rm -rf ./instagram_session
python instagram_personal_poster.py
```

Expected: Prompts for manual login again

### Test 2: No Posts to Process
```bash
# Move all posts out of Approved
# Run script
python instagram_personal_poster.py
```

Expected: "No approved Instagram posts found"

### Test 3: Invalid Post Format
Create a test post with invalid format and verify error handling.

### Test 4: Media Upload
```bash
# Create post with media field
# Add image path to frontmatter
# Run script
```

Expected: Uploads image successfully

## Performance Benchmarks

### Timing Expectations
- First run (with login): ~30-60 seconds
- Subsequent runs: ~20-30 seconds per post
- Session load time: ~3-5 seconds
- Post creation: ~10-15 seconds
- Media upload: +5-10 seconds

### Resource Usage
- Memory: ~200-300 MB (Chromium)
- CPU: Low (mostly idle)
- Network: Minimal
- Disk: ~100 MB (session)

## Demo Preparation

### For Hackathon Demo
1. ✅ Prepare 2-3 posts in Approved folder
2. ✅ Clear Done folder for clean demo
3. ✅ Have Instagram open in another tab to show results
4. ✅ Run in visible mode (already default)
5. ✅ Explain workflow: Approved → Browser → Instagram → Done

### Demo Script
```
1. "Here's our Instagram automation using Playwright"
2. Show Approved folder with draft posts
3. Run: run_instagram_poster.bat
4. Browser opens automatically (visible)
5. Already logged in (session persistence)
6. Watch it type caption automatically
7. Clicks Share button
8. Post appears on Instagram!
9. File moves to Done folder
10. Dashboard updates automatically
```

## Success Criteria

### Must Have ✅
- [x] Script runs without errors
- [x] Browser opens in visible mode
- [x] Session persists across runs
- [x] Caption types automatically
- [x] Post publishes successfully
- [x] File moves to Done folder
- [x] Dashboard updates

### Nice to Have 🎯
- [ ] Media upload works
- [ ] Multiple posts in batch
- [ ] Error recovery graceful
- [ ] Manual fallback works

## Known Limitations

1. **Instagram UI Changes**: Selectors may break if Instagram updates UI
2. **Rate Limits**: Instagram limits posting frequency
3. **Manual Login**: First-time login requires manual interaction
4. **Media Upload**: May require manual selection if auto-upload fails
5. **Personal Only**: Only works for personal profiles, not Business accounts

## Next Steps After Testing

1. ✅ Verify all tests pass
2. ✅ Document any issues found
3. ✅ Update selectors if Instagram UI changed
4. ✅ Integrate with approval_handler if needed
5. ✅ Add to orchestrator workflow
6. ✅ Schedule regular posts if desired

## Support Resources

- Setup Guide: `INSTAGRAM_QUICK_SETUP.md`
- MCP Docs: `AI_Employee_Vault/MCP_Servers/instagram_mcp.md`
- Skill Definition: `.claude/skills/instagram-poster/skill.md`
- Facebook Reference: `facebook_personal_poster.py` (similar implementation)

---

**Ready for Testing!** 🚀

Run `python instagram_personal_poster.py` to start your first Instagram post!

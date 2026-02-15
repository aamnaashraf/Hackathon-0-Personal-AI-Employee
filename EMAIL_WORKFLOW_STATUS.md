# EMAIL WORKFLOW - QUICK REFERENCE

## REAL EMAILS SENT TODAY (2026-02-14)

### 1. Test Email (08:21 AM)
- **To**: aamnaashraf501@gmail.com
- **Subject**: Re: Test Email Workflow
- **Status**: ✓ SENT
- **File**: AI_Employee_Vault/Done/REPLY_DRAFT_test_workflow.md

### 2. Render Payment Email (07:54 AM)
- **To**: support@render.com
- **Subject**: Re: Payment Information Update - Account Action Taken
- **Status**: ✓ SENT (via manual script)
- **File**: AI_Employee_Vault/Done/REPLY_DRAFT_render_payment_1770346558.md

### 3. Google Security Alert
- **Status**: ✓ ACKNOWLEDGED (no-reply address, not sent)
- **File**: AI_Employee_Vault/Done/REPLY_DRAFT_google_security_1770346559.md

---

## HOW TO VERIFY EMAILS WERE SENT

### Option 1: Check Gmail Inbox (BEST WAY)
1. Open: https://mail.google.com
2. Login: aamnaashraf501@gmail.com
3. Check "Sent" folder
4. Look for:
   - "Re: Test Email Workflow" (sent to yourself)
   - "Re: Payment Information Update" (sent to Render support)

### Option 2: Check System Logs
```bash
# View today's email log
type AI_Employee_Vault\Logs\2026-02-14_email_sender.log

# Or on Linux/Git Bash
cat AI_Employee_Vault/Logs/2026-02-14_email_sender.log
```

### Option 3: Check Done Folder
```bash
# List all sent emails
dir AI_Employee_Vault\Done\REPLY_*.md

# Or on Linux/Git Bash
ls -la AI_Employee_Vault/Done/REPLY_*.md
```

---

## FILES TO RUN

### Start Email Sender Watcher (MAIN FILE)
```bash
python done_folder_email_sender.py
```
OR double-click:
```
run_done_email_sender.bat
```

This watches the Done folder and automatically sends emails when you move drafts there.

### Check Gmail for New Emails
```bash
# Use the gmail_reader skill
# (Already integrated in your system)
```

### Check Workflow Status
```bash
# Run the check script
check_email_workflow.bat
```

---

## WORKFLOW STEPS (HOW TO USE)

```
1. NEW EMAIL ARRIVES
   └─> Gmail → AI_Employee_Vault/Needs_Action/

2. CREATE DRAFT REPLY
   └─> AI_Employee_Vault/Pending_Approval/REPLY_DRAFT_*.md

3. REVIEW DRAFT
   └─> Move to: AI_Employee_Vault/Approved/

4. SEND EMAIL (AUTOMATIC)
   └─> Move to: AI_Employee_Vault/Done/
   └─> Email sent automatically via SMTP
   └─> File stays in Done as record

5. VERIFY
   └─> Check Gmail Sent folder
   └─> Check Logs/2026-02-14_email_sender.log
```

---

## CURRENT STATUS

✓ Email sender watcher: RUNNING (background)
✓ Gmail credentials: CONFIGURED
✓ SMTP connection: WORKING
✓ Test email: SENT successfully
✓ Real email to Render: SENT successfully

---

## TROUBLESHOOTING

**Email not sending?**
1. Check watcher is running: `tasklist | findstr python`
2. Check logs: `AI_Employee_Vault/Logs/2026-02-14_email_sender.log`
3. Restart watcher: `python done_folder_email_sender.py`

**How to verify email was really sent?**
1. Check your Gmail "Sent" folder (most reliable)
2. Check the log file shows "Status: sent"
3. Check recipient received it

**Need to send more emails?**
1. Create draft in Pending_Approval
2. Move to Approved (review)
3. Move to Done (auto-send)

---

## NEXT STEPS

1. **Verify in Gmail**: Check your Sent folder for the test email
2. **Keep watcher running**: Leave `done_folder_email_sender.py` running
3. **Use workflow**: Create drafts → Approve → Move to Done → Auto-send


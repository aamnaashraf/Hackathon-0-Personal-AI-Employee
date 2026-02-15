# Email Automation Workflow Guide

## Complete Workflow

### Step 1: Check Recent Emails
Run the gmail_reader skill or check the Needs_Action folder for new emails.

### Step 2: Draft Replies
Create email reply drafts in the `Pending_Approval` folder with this format:

```markdown
---
type: email_reply_draft
original_subject: "Subject of original email"
reply_to: recipient@example.com
priority: high/medium/low
action: send_email
---

# Email Reply Draft: [Title]

## Original Message
- **From**: Sender Name <sender@example.com>
- **Subject**: Original Subject
- **Received**: Date

## Draft Reply

**To**: recipient@example.com
**Subject**: Re: Original Subject

Dear [Name],

[Your email body here]

Best regards,
Aamna Ashraf Rajput

---

## Approval Instructions
- Move this file to `/Approved/` folder when ready to review
- Move from `/Approved/` to `/Done/` folder to send automatically
```

### Step 3: Review and Approve
- Review drafts in `Pending_Approval` folder
- When satisfied, move to `Approved` folder
- Files in Approved are ready to send but NOT sent yet

### Step 4: Send Email
- When ready to actually send, move file from `Approved` to `Done` folder
- The `done_folder_email_sender.py` watcher automatically detects the file
- Email is sent via SMTP immediately
- File remains in Done folder as a record

## Running the Email Sender

### Start the Watcher:
```bash
python done_folder_email_sender.py
```

Or use the batch file:
```bash
run_done_email_sender.bat
```

### The watcher will:
- Monitor the Done folder continuously
- Detect when email drafts are moved there
- Extract recipient, subject, and body
- Send via Gmail SMTP
- Log all actions to `AI_Employee_Vault/Logs/`

## Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/          # New emails from gmail-watcher
├── Pending_Approval/      # Draft replies waiting for your review
├── Approved/              # Reviewed drafts ready to send
├── Done/                  # Sent emails (trigger folder for auto-send)
└── Logs/                  # Email sending logs
```

## Important Notes

- **No-reply addresses**: Emails to no-reply addresses are skipped automatically
- **Gmail credentials**: Uses GMAIL_USERNAME and GMAIL_PASSWORD from .env
- **Logs**: All sending attempts are logged with timestamps
- **Safety**: Two-step approval (Approved → Done) prevents accidental sends

## Testing the Workflow

1. Create a test draft in Pending_Approval
2. Move to Approved (review step)
3. Move to Done (send step)
4. Check logs to verify sending

## Troubleshooting

- **Email not sending**: Check .env has correct GMAIL_USERNAME and GMAIL_PASSWORD
- **Watcher not running**: Run `python done_folder_email_sender.py`
- **Check logs**: Look in `AI_Employee_Vault/Logs/[date]_email_sender.log`

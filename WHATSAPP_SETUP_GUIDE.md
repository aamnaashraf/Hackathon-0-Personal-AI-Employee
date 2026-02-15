# WhatsApp Watcher Setup and Usage Guide

## Overview
This guide explains how to run the fixed WhatsApp watcher that detects messages and creates tasks in the Needs_Action folder, plus how to send replies.

## Prerequisites
- Playwright installed: `pip install playwright`
- WhatsApp Business account or regular WhatsApp Web access
- Proper .env configuration with WhatsApp settings

## Step 1: Install Playwright Browser
```bash
playwright install chromium
```

## Step 2: Run the WhatsApp Watcher
```bash
python whatsapp_watcher.py
```

## Step 3: Scan QR Code
1. When prompted, scan the QR code with your WhatsApp Business app
2. The session will be saved to ./whatsapp_session/storage-state.json
3. The watcher will start monitoring for new messages

## Step 4: How It Works
1. **Message Detection**: The watcher checks for unread messages every 2 minutes
2. **Task Creation**: When a new message is detected, it creates a task in Needs_Action folder
3. **Processing**: The orchestrator will pick up the task and create a plan
4. **Reply**: You can draft a response and send it using the MCP system

## Step 5: Sending Replies via MCP
To send a WhatsApp message to a contact like "Aamna Ashraf Rajput":

### Option A: Using the MCP Script Directly
```bash
python whatsapp_mcp.py "Aamna Ashraf Rajput" "Your message here"
```

### Option B: Using the WhatsApp Sender Skill
The skill can be used within the Claude system:
```
whatsapp_sender.send_message("Aamna Ashraf Rajput", "Thank you for your inquiry!")
```

## Step 6: Testing the Full Flow
1. Start the WhatsApp watcher
2. Send yourself a test message on WhatsApp
3. Wait for the watcher to detect it (within 2 minutes)
4. Check that a new file appears in Needs_Action folder
5. Use Claude to process the task and create a reply plan
6. Submit the reply to Pending_Approval if needed
7. Use the MCP to send the reply to the contact

## Troubleshooting
- If messages aren't detected, ensure the WhatsApp Web page is fully loaded
- Check that the session file exists in ./whatsapp_session/
- Verify that the contact has unread messages
- Make sure the browser window stays open while watching

## Files Created
- Session data: ./whatsapp_session/storage-state.json
- New message tasks: AI_Employee_Vault/Needs_Action/whatsapp_*.md
- MCP configuration: AI_Employee_Vault/MCP_Servers/whatsapp_mcp.md

## Integration Points
- The orchestrator automatically moves WhatsApp messages to Needs_Action
- The whatsapp_handler skill processes incoming messages
- The whatsapp_sender skill sends replies via MCP
- All communication follows Company Handbook guidelines
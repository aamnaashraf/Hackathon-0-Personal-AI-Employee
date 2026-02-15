"""
WhatsApp Message Detector - Single Run Approach
Runs once, detects messages, creates tasks, then exits
Call this script repeatedly (every 2-5 minutes) for continuous monitoring
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from pathlib import Path
from datetime import datetime
import json
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def detect_whatsapp_messages(vault_path, session_path):
    """
    Single-run message detection
    Returns list of task files created
    """
    print("\n" + "="*60)
    print("WHATSAPP MESSAGE DETECTOR - SINGLE RUN")
    print("="*60)

    vault_path = Path(vault_path)
    session_file = Path(session_path) / 'storage-state.json'

    if not session_file.exists():
        print(f"[ERROR] Session file not found: {session_file}")
        print("[INFO] Run setup_whatsapp_session.py first")
        return []

    print(f"[INFO] Loading session from: {session_file}")

    # Start Playwright
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=str(session_file))
    page = context.new_page()

    # Apply stealth
    print("[INFO] Applying stealth mode...")
    stealth = Stealth()
    stealth.apply_stealth_sync(page)

    # Navigate to WhatsApp Web
    print("[INFO] Navigating to WhatsApp Web...")
    page.goto("https://web.whatsapp.com")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=60000)
    except:
        pass

    # Wait for WhatsApp to fully load (this is the key - same as diagnostic)
    print("[INFO] Waiting 45 seconds for WhatsApp to load...")
    time.sleep(45)

    print("\n[INFO] Checking for chats...")

    # Get chats using the working selector
    chat_items = page.locator('#pane-side div[role="row"]')
    chat_count = chat_items.count()

    if chat_count == 0:
        chat_items = page.locator('div[aria-label="Chat list"] div[role="row"]')
        chat_count = chat_items.count()

    print(f"[INFO] Found {chat_count} chats")

    if chat_count == 0:
        print("[WARNING] No chats found - WhatsApp may not be loaded")
        browser.close()
        playwright.stop()
        return []

    # Process chats to find messages
    new_task_files = []
    needs_action_dir = vault_path / 'Needs_Action'
    needs_action_dir.mkdir(exist_ok=True)

    print(f"\n[INFO] Checking first 10 chats for messages...")

    for i in range(min(chat_count, 10)):
        try:
            chat_item = chat_items.nth(i)

            # Get chat name (sanitized for printing)
            chat_name = f"Contact_{i}"
            try:
                title_element = chat_item.locator('[title]').first
                if title_element.count() > 0:
                    chat_name_raw = title_element.get_attribute('title') or chat_name
                    # Sanitize for safe printing
                    chat_name = chat_name_raw.encode('ascii', 'ignore').decode('ascii')
                    if not chat_name:
                        chat_name = f"Contact_{i}"
            except:
                pass

            print(f"  [{i+1}/{min(chat_count, 10)}] Checking: {chat_name}")

            # Check for unread badge
            has_unread = False
            try:
                unread_badge = chat_item.locator('[data-testid="unread-count"]')
                if unread_badge.count() > 0:
                    has_unread = True
                    print(f"    → Has unread messages")
            except:
                pass

            # For testing: process ALL chats (change to has_unread for production)
            if True:  # Change to: if has_unread:
                # Click on chat
                chat_item.click(timeout=5000)
                time.sleep(3)  # Wait for messages to load

                # Extract latest message
                latest_message = ""
                try:
                    # Get all message text spans
                    chat_area = page.locator('[data-testid="conversation-panel-body"], #main')
                    if chat_area.count() > 0:
                        text_spans = chat_area.locator('span.selectable-text')
                        span_count = text_spans.count()

                        if span_count > 0:
                            # Get last message
                            latest_message = text_spans.last.text_content().strip()
                            print(f"    → Message: {latest_message[:50]}...")
                except Exception as e:
                    print(f"    → Could not extract message: {e}")

                if latest_message:
                    # Create task file
                    timestamp = int(time.time())
                    msg_hash = hash(latest_message + chat_name_raw) % 10000
                    task_id = f"whatsapp_{timestamp}_{msg_hash}"
                    task_file = needs_action_dir / f"{task_id}.md"

                    # Skip if already exists
                    if task_file.exists():
                        print(f"    → Task already exists, skipping")
                        continue

                    # Determine priority
                    priority = 'low'
                    msg_lower = latest_message.lower()
                    if any(kw in msg_lower for kw in ['urgent', 'asap', 'emergency', 'critical']):
                        priority = 'high'
                    elif any(kw in msg_lower for kw in ['important', 'meeting', 'call', 'today']):
                        priority = 'medium'

                    # Create task content
                    content = f"""---
type: whatsapp_message
sender: {chat_name_raw}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# WhatsApp Message from {chat_name_raw}

## Message Details
- **From**: {chat_name_raw}
- **Received**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Status**: pending

## Content
{latest_message}

## Action Required
- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Draft response (Urdu/English as appropriate)
- [ ] Submit to Pending_Approval if external communication needed

## Processing Instructions
1. Analyze the message content and context
2. Identify if it requires immediate attention
3. Draft appropriate response considering:
   - Language preference (Urdu/English)
   - Tone and formality
   - Business context
4. Use whatsapp_sender skill to send approved replies

## Next Steps
1. Move to Approved folder when ready to process
2. Create reply draft in Plans folder
3. Update status to 'completed' when resolved
"""

                    task_file.write_text(content, encoding='utf-8')
                    new_task_files.append(task_file)
                    print(f"    ✓ Task created: {task_file.name}")

        except Exception as e:
            print(f"  [ERROR] Failed to process chat {i}: {e}")
            continue

    # Cleanup
    print(f"\n[INFO] Closing browser...")
    browser.close()
    playwright.stop()

    print("\n" + "="*60)
    print(f"DETECTION COMPLETE: {len(new_task_files)} new tasks created")
    print("="*60)

    return new_task_files


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    VAULT_PATH = os.getenv('VAULT_PATH', "E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault")
    SESSION_PATH = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')

    task_files = detect_whatsapp_messages(VAULT_PATH, SESSION_PATH)

    if task_files:
        print(f"\nCreated {len(task_files)} task files:")
        for tf in task_files:
            print(f"  - {tf.name}")
    else:
        print("\nNo new messages detected")

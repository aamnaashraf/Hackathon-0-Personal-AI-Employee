#!/usr/bin/env python3
"""
WhatsApp Watcher (STABLE)
- Detects unread chats
- Opens chat
- Extracts last incoming message
- Writes to /Needs_Action
"""

import time
import json
import hashlib
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

VAULT = Path("AI_Employee_Vault")
SESSION_DIR = Path("whatsapp_session")
NEEDS_ACTION = VAULT / "Needs_Action"
STATE_FILE = Path("whatsapp_state.json")

NEEDS_ACTION.mkdir(parents=True, exist_ok=True)

def load_state():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def save_state(state):
    STATE_FILE.write_text(json.dumps(list(state), indent=2))

def uid(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]

print("🚀 WhatsApp Watcher Started")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://web.whatsapp.com")

    print("⏳ Waiting for WhatsApp...")
    page.wait_for_selector("div[role='grid']", timeout=60000)
    print("✅ WhatsApp Ready")

    processed = load_state()

    while True:
        try:
            # Get all chats using working selector
            chats = page.query_selector_all("div[role='row']")
            print(f"🔍 Scanning {len(chats)} chats...")
            
            if len(chats) == 0:
                print("⚠️ No chats found, waiting...")
                time.sleep(10)
                continue
            
            # Check first 15 chats for new messages
            for i, chat in enumerate(chats[:15]):
                try:
                    # Click on chat to open it
                    chat.click()
                    time.sleep(1)  # Wait for chat to load
                    
                    # Get chat name from header
                    chat_name_elem = page.query_selector("header span[dir='auto']")
                    if not chat_name_elem:
                        continue
                    chat_name = chat_name_elem.inner_text()
                    
                    # Get all messages
                    messages = page.query_selector_all("div.copyable-text")
                    if not messages:
                        continue
                    
                    # Get last message
                    message_text = messages[-1].inner_text()
                    if not message_text.strip():
                        continue
                    
                    key = uid(chat_name + message_text)
                    
                    # Skip if already processed
                    if key in processed:
                        continue
                    
                    # Save new message
                    ts = datetime.now().isoformat()
                    
                    md = f"""---
type: whatsapp
chat_name: {chat_name}
received_at: {ts}
status: needs_reply
---

{message_text}
"""
                    
                    file = NEEDS_ACTION / f"WHATSAPP_{key}.md"
                    file.write_text(md, encoding="utf-8")
                    
                    print(f"📥 NEW MESSAGE from {chat_name} → {file.name}")
                    print(f"📝 Message: {message_text[:100]}...")
                    processed.add(key)
                    save_state(processed)
                    
                except Exception as e:
                    continue  # Silently skip errors in individual chats

            time.sleep(10)

        except KeyboardInterrupt:
            print("⏹ Stopped")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(10)

    try:
        browser.close()
    except:
        pass
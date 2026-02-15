#!/usr/bin/env python3
"""
WhatsApp Watcher + Sender
- Detects incoming messages → Need_Action
- Sends approved replies from To_Send folder
"""

import time
import json
import hashlib
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


VAULT = Path(".")
SESSION_DIR = VAULT / "whatsapp_session"
NEEDS_ACTION = VAULT / "Need_Action"
TO_SEND = VAULT / "To_Send"
DONE = VAULT / "Done"
STATE_FILE = VAULT / "whatsapp_state.json"

NEEDS_ACTION.mkdir(exist_ok=True)
TO_SEND.mkdir(exist_ok=True)
DONE.mkdir(exist_ok=True)

def load_state():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def save_state(state):
    STATE_FILE.write_text(json.dumps(list(state), indent=2))

def uid(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]

def send_message(page, chat_name, message):
    """Send a WhatsApp message"""
    try:
        # Search for chat
        search_box = page.query_selector("div[contenteditable='true'][data-tab='3']")
        if not search_box:
            return False
        
        search_box.click()
        time.sleep(0.5)
        search_box.fill("")
        time.sleep(0.3)
        search_box.fill(chat_name)
        time.sleep(2)
        
        # Click first result
        first_chat = page.query_selector("div[role='row']")
        if not first_chat:
            return False
        
        first_chat.click()
        time.sleep(1)
        
        # Type and send message
        message_box = page.query_selector("div[contenteditable='true'][data-tab='10']")
        if not message_box:
            return False
        
        message_box.click()
        time.sleep(0.3)
        message_box.fill(message)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        
        return True
    except:
        return False

print("🚀 WhatsApp Watcher + Sender Started")

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
    send_processed = set()

    while True:
        try:
            # === PART 1: Check for messages to SEND ===
            send_files = list(TO_SEND.glob("SEND_*.md"))
            for file in send_files:
                if file.name in send_processed:
                    continue
                
                print(f"\n📤 Sending message: {file.name}")
                
                content = file.read_text(encoding="utf-8")
                lines = content.split('\n')
                
                chat_name = ""
                message = ""
                in_message = False
                
                for line in lines:
                    if line.startswith("chat_name:"):
                        chat_name = line.split(":", 1)[1].strip()
                    if line == "---" and chat_name:
                        in_message = True
                        continue
                    if in_message:
                        message += line + "\n"
                
                message = message.strip()
                
                if chat_name and message:
                    print(f"💬 To: {chat_name}")
                    print(f"📝 Message: {message[:100]}...")
                    
                    success = send_message(page, chat_name, message)
                    
                    if success:
                        print("✅ Message sent!")
                        done_file = DONE / file.name
                        file.rename(done_file)
                    else:
                        print("❌ Failed to send")
                
                send_processed.add(file.name)
            
            # === PART 2: Check for INCOMING messages ===
            chats = page.query_selector_all("div[role='row']")
            print(f"🔍 Scanning {len(chats)} chats...")
            
            if len(chats) == 0:
                time.sleep(10)
                continue
            
            for i, chat in enumerate(chats[:15]):
                try:
                    chat.click()
                    time.sleep(1)
                    
                    chat_name_elem = page.query_selector("header span[dir='auto']")
                    if not chat_name_elem:
                        continue
                    chat_name = chat_name_elem.inner_text()
                    
                    messages = page.query_selector_all("div.copyable-text")
                    if not messages:
                        continue
                    
                    message_text = messages[-1].inner_text()
                    if not message_text.strip():
                        continue
                    
                    key = uid(chat_name + message_text)
                    
                    if key in processed:
                        continue
                    
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
                    continue

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
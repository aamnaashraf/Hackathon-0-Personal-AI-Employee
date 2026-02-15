"""
WhatsApp MCP Server for AI Employee
Handles WhatsApp communication via Playwright browser automation
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys

class WhatsAppMCP:
    def __init__(self, vault_path, whatsapp_config):
        self.vault_path = Path(vault_path)
        self.whatsapp_config = whatsapp_config
        self.session_path = Path(whatsapp_config['session_path'])
        self.browser = None
        self.page = None
        self.playwright = None
        self.context = None

    def setup_browser(self):
        """Setup browser with saved session or create new session"""
        self.playwright = sync_playwright().start()

        # Check if session file exists
        session_file_path = self.session_path / 'storage-state.json'

        if session_file_path.exists():
            # Use existing session
            print("[INFO] Using existing WhatsApp session...")
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Keep visible for interaction
                args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            try:
                self.context = self.browser.new_context(
                    storage_state=session_file_path
                )
            except Exception as e:
                print(f"[ERROR] Could not load stored session: {e}")
                return False
        else:
            print("[ERROR] No existing WhatsApp session found. Please run whatsapp_watcher.py first to set up the session.")
            return False

        self.page = self.context.new_page()
        self.page.goto("https://web.whatsapp.com")

        # Wait for WhatsApp to load
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)  # Additional wait for interface to stabilize

            # Check if we're authenticated by looking for main interface elements
            chat_list_selectors = [
                '[data-testid="chat-list"]',
                '#pane-side',
                '[data-testid="conversation-panel"]',
                '[data-testid="chat"]',
                '[data-testid="cell-frame-container"]'
            ]

            is_authenticated = False
            for selector in chat_list_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        is_authenticated = True
                        break
                except:
                    continue

            if is_authenticated:
                print("[SUCCESS] WhatsApp connected and authenticated.")
                return True
            else:
                print("[ERROR] WhatsApp not authenticated. Please check session.")
                return False

        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False

    def force_read_last_unread_message(self):
        """Force read the last unread message and create a task in Needs_Action"""
        try:
            # Wait for page to be loaded
            if self.page.url != "https://web.whatsapp.com":
                self.page.goto("https://web.whatsapp.com")
                self.page.wait_for_load_state("networkidle")

            # Wait for chat list to load
            try:
                self.page.wait_for_selector('#pane-side, [data-testid="chat-list"], [role="navigation"]', timeout=10000)
            except:
                print("[ERROR] Main interface not loaded")
                return False

            # Get all chat items that might have unread messages
            chat_items = self.page.locator('#pane-side [data-testid="chat"], #pane-side [role="row"], [data-testid="conversation"]')
            chat_count = chat_items.count()

            if chat_count == 0:
                # Try alternative selectors
                chat_items = self.page.locator('#pane-side div[tabindex]')
                chat_count = chat_items.count()

            print(f"[INFO] Found {chat_count} chats to check")

            # Look for chats with unread indicators first
            unread_chats = []
            for i in range(min(chat_count, 20)):  # Limit to first 20 chats
                chat_item = chat_items.nth(i)

                # Check if this chat has unread messages
                has_unread = False
                try:
                    # Check for unread count badges
                    unread_badge = chat_item.locator('[data-testid="unread-count"], .P6z4j, .gqwa7oj8')
                    if unread_badge.count() > 0:
                        has_unread = True
                    else:
                        # Check for other indicators
                        for selector in ['.g0rxnqlm', '.gg0TEMId26wfC2i09Ntn', '.zoWTgvAR26YVQUFDmk8n']:
                            if chat_item.locator(selector).count() > 0:
                                has_unread = True
                                break
                except:
                    pass

                if has_unread:
                    unread_chats.append((i, chat_item))

            # If no unread chats found, try the most recent chat
            if not unread_chats:
                print("[INFO] No unread chats with badges found, checking most recent chat...")
                if chat_count > 0:
                    unread_chats.append((0, chat_items.nth(0)))

            # Process the first unread chat (most urgent)
            if unread_chats:
                chat_idx, chat_item = unread_chats[0]

                # Get chat name
                chat_name = f"Contact {chat_idx}"
                try:
                    # Try multiple possible selectors for chat name
                    name_selectors = [
                        '[title]',  # Direct title attribute
                        '.emoji-group, .selectable-text',  # Common name containers
                        'span[dir="auto"]:first-child',  # Name spans
                        '.zoWTgvAR26YVQUFDmk8n span',  # Unread message name
                        '.gg0TEMId26wfC2i09Ntn span',  # Alternative unread selector
                        '.pd2BYOH3YfkFQOypu75ZL'  # Another common selector for contact names
                    ]

                    for selector in name_selectors:
                        try:
                            elements = chat_item.locator(selector)
                            element_count = elements.count()

                            for idx in range(element_count):
                                try:
                                    text = elements.nth(idx).text_content(timeout=1000).strip()
                                    if text and not text.startswith('Contact'):
                                        chat_name = text
                                        break
                                except:
                                    continue

                            if chat_name != f"Contact {chat_idx}":
                                break
                        except:
                            continue
                except:
                    pass

                print(f"[INFO] Processing chat: {chat_name}")

                # Click on the chat to open it
                try:
                    chat_item.click(timeout=5000)
                    time.sleep(3)  # Allow time for chat to load

                    # Get messages in the chat - focusing on incoming messages
                    message_selectors = [
                        '[data-id*="false"]',  # Incoming messages often have 'false' in data-id
                        'div.copyable-text',  # Common selector for message content
                        '.selectable-text',  # Another common selector
                        'span.selectable-text',  # Message text spans
                        '[data-testid="msg"]'  # Standard message selector
                    ]

                    latest_message_text = ""

                    # Loop through all selectors to find the latest incoming message
                    for selector in message_selectors:
                        try:
                            message_elements = self.page.locator(selector)
                            message_count = message_elements.count()

                            if message_count > 0:
                                # Get the most recent message (last in the chat)
                                for idx in range(message_count - 1, max(-1, message_count - 15), -1):
                                    try:
                                        msg_element = message_elements.nth(idx)
                                        msg_text = msg_element.text_content().strip()

                                        if msg_text and len(msg_text) > 0:
                                            # Get element attributes to identify incoming messages
                                            element_classes = msg_element.get_attribute('class') or ''
                                            data_id = msg_element.get_attribute('data-id') or ''

                                            # Look for indicators that this is an incoming message
                                            is_incoming = (
                                                'false' in data_id or  # Usually indicates incoming message
                                                'message-out' not in element_classes and
                                                'msg-out' not in element_classes and
                                                'copyable-text' in element_classes and
                                                'data-icon="msg-dblcheck-out"' not in element_classes and
                                                'data-icon="msg-check-out"' not in element_classes and
                                                len(msg_text) > 0
                                            )

                                            if is_incoming:
                                                latest_message_text = msg_text
                                                print(f"[INFO] Found incoming message: {msg_text[:50]}...")
                                                break

                                    except Exception as e:
                                        print(f"[DEBUG] Error getting message text: {e}")
                                        continue

                            if latest_message_text:
                                break

                        except Exception as e:
                            print(f"[DEBUG] Error with selector {selector}: {e}")
                            continue

                    if latest_message_text:
                        # Create task file for the message in Needs_Action folder
                        needs_action_dir = self.vault_path / 'Needs_Action'
                        needs_action_dir.mkdir(exist_ok=True)

                        # Create a more descriptive filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        msg_id = f"whatsapp_{timestamp}_{hash(latest_message_text + chat_name) % 10000}"
                        task_file = needs_action_dir / f"{msg_id}.md"

                        received_time = datetime.now().isoformat()

                        # Determine priority
                        priority_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'help', 'as soon as possible']
                        priority = 'low'
                        msg_lower = latest_message_text.lower()
                        for keyword in priority_keywords:
                            if keyword in msg_lower:
                                priority = 'high'
                                break
                        else:
                            if any(word in msg_lower for word in ['meeting', 'call', 'urgent', 'important', 'today', 'now']):
                                priority = 'medium'

                        content = f"""---
type: whatsapp_message
sender: {chat_name}
received: {received_time}
priority: {priority}
status: pending
---

# WhatsApp Message from {chat_name}

## Message Details
- **From**: {chat_name}
- **Received**: {received_time}
- **Priority**: {priority}
- **Status**: pending

## Content
{latest_message_text}

## Action Required
- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Create plan in /Plans/ folder
- [ ] Draft response if needed (with approval if external communication)
- [ ] Use whatsapp_handler skill to process response

## Processing Instructions
1. Analyze the message content
2. Identify if it requires immediate attention
3. Check if it's a business inquiry that needs escalation
4. Use whatsapp_handler skill to process response
5. If external communication is needed, submit to Pending_Approval

## Next Steps
1. Move this file to Approved folder when processed
2. Create corresponding plan in Plans folder if needed
3. Update status to 'completed' when resolved
"""
                        task_file.write_text(content, encoding='utf-8')

                        print(f"[SUCCESS] Created task for WhatsApp message from {chat_name}: {latest_message_text[:50]}...")
                        print(f"[INFO] Task saved to: {task_file}")

                        # Now create a reply draft
                        self.create_reply_draft(chat_name, latest_message_text)

                        return True
                    else:
                        print("[WARNING] No incoming messages found in the chat")
                        return False

                except Exception as e:
                    print(f"[ERROR] Could not process chat {chat_name}: {e}")
                    return False
            else:
                print("[INFO] No chats with unread messages found")
                return False

        except Exception as e:
            print(f"[ERROR] Could not force read messages: {e}")
            return False

    def create_reply_draft(self, sender, message_content):
        """Create a reply draft for the received message"""
        try:
            # Create a reply draft in the Plans folder
            plans_dir = self.vault_path / 'Plans'
            plans_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_id = f"REPLY_DRAFT_WHATSAPP_{timestamp}_{hash(sender + message_content) % 10000}"
            draft_file = plans_dir / f"{draft_id}.md"

            # Analyze the message to suggest an appropriate response
            message_lower = message_content.lower()
            suggested_tone = "professional"

            if any(word in message_lower for word in ['urgent', 'asap', 'help', 'emergency']):
                suggested_tone = "urgent and helpful"
            elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
                suggested_tone = "grateful and helpful"
            elif any(word in message_lower for word in ['complaint', 'problem', 'issue']):
                suggested_tone = "empathetic and solution-oriented"

            content = f"""---
type: whatsapp_reply_draft
sender: {sender}
original_message: "{message_content}"
status: draft
---

# WhatsApp Reply Draft for {sender}

## Original Message
{message_content}

## Response Guidelines
- Tone: {suggested_tone}
- Keep it concise and helpful
- Address the main concern/query directly
- Follow up with any necessary questions

## Suggested Response
<!-- Draft your response here -->

## Approval Status
- [ ] Draft completed
- [ ] Sent for approval (move to Pending_Approval folder)
- [ ] Approved (awaiting whatsapp_sender)
- [ ] Sent to {sender}

## Next Steps
1. Complete the response draft above
2. Move this file to Pending_Approval folder for review
3. Once approved, use whatsapp_sender skill to send the message
4. Update original task status to reflect response sent
"""
            draft_file.write_text(content, encoding='utf-8')

            print(f"[SUCCESS] Reply draft created for {sender}")
            print(f"[INFO] Draft saved to: {draft_file}")

        except Exception as e:
            print(f"[ERROR] Could not create reply draft: {e}")

    def close(self):
        """Close browser and playwright"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


def handle_command(command, data):
    """Handle MCP commands"""
    # Load configuration
    import dotenv
    dotenv.load_dotenv()

    whatsapp_config = {
        'session_path': os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'),
        'watch_interval': int(os.getenv('WHATSAPP_WATCH_INTERVAL', '30')),
        'labels': os.getenv('WHATSAPP_LABELS', 'UNREAD,IMPORTANT').split(','),
        'business_mode': os.getenv('WHATSAPP_BUSINESS_MODE', 'false').lower() == 'true'
    }

    vault_path = os.getenv('VAULT_PATH', "E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault")

    if command == "force_read_last_unread":
        mcp = WhatsAppMCP(vault_path, whatsapp_config)

        if mcp.setup_browser():
            success = mcp.force_read_last_unread_message()
            mcp.close()
            return {"success": success}
        else:
            mcp.close()
            return {"success": False, "error": "Could not setup browser or authenticate"}

    elif command == "send_message":
        mcp = WhatsAppMCP(vault_path, whatsapp_config)

        if mcp.setup_browser():
            contact_name = data.get('contact_name', '')
            message_text = data.get('message_text', '')

            try:
                # Search for the contact
                search_box = mcp.page.locator('div[data-testid="chatlist-search"] input, [data-testid="chat"] input')
                if search_box.count() > 0:
                    search_box.fill(contact_name)
                    time.sleep(1)

                # Find and click on the contact
                contact_element = mcp.page.locator(f'[title="{contact_name}"], [data-testid="cell-frame-container"]')
                if contact_element.count() > 0:
                    contact_element.first.click()
                    time.sleep(2)  # Wait for chat to open

                    # Find the message input box
                    message_input = mcp.page.locator('div[data-testid="conversation-compose-box-input"], [data-testid="conversation-compose-box-send"]')
                    if message_input.count() > 0:
                        message_input.fill(message_text)

                        # Send the message
                        send_button = mcp.page.locator('button[data-testid="compose-btn-send"]')
                        if send_button.count() > 0:
                            send_button.click()
                            print(f"[WHATSAPP] Message sent to {contact_name}: {message_text[:30]}...")

                            # Close and return success
                            mcp.close()
                            return {"success": True, "message": f"Message sent to {contact_name}"}
                        else:
                            result = {"success": False, "error": "Could not find send button"}
                    else:
                        result = {"success": False, "error": "Could not find message input box"}
                else:
                    result = {"success": False, "error": f"Could not find contact: {contact_name}"}
            except Exception as e:
                result = {"success": False, "error": str(e)}

            mcp.close()
            return result

    else:
        return {"success": False, "error": f"Unknown command: {command}"}


if __name__ == "__main__":
    # Example usage for testing
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "force_read":
            result = handle_command("force_read_last_unread", {})
            print(json.dumps(result))
        else:
            print(json.dumps({"success": False, "error": f"Unknown command: {command}"}))
    else:
        print(json.dumps({"success": False, "error": "No command provided"}))
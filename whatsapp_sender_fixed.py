#!/usr/bin/env python3
"""
WhatsApp Sender - Fixed Version
Sends approved messages via WhatsApp Web with improved reliability
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class WhatsAppSenderFixed:
    def __init__(
        self,
        approved_dir="AI_Employee_Vault/Approved",
        done_dir="AI_Employee_Vault/Done",
        log_file="AI_Employee_Vault/System_Log.md",
        dry_run=False
    ):
        self.approved_dir = Path(approved_dir).resolve()
        self.done_dir = Path(done_dir).resolve()
        self.log_file = Path(log_file).resolve()
        self.dry_run = dry_run

        # Create directories if they don't exist
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)

    def _parse_markdown_file(self, filepath):
        """Parse markdown file with YAML frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                return None

            frontmatter_text = frontmatter_match.group(1)
            body = frontmatter_match.group(2).strip()

            # Parse frontmatter fields
            metadata = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Extract reply text - handle multiple formats
            reply_text = None

            # Format 1: "## Draft Reply" section
            draft_reply_match = re.search(r'## Draft Reply\s*\n\n(.*?)(?=\n##|\n---|\Z)', body, re.DOTALL)
            if draft_reply_match:
                reply_text = draft_reply_match.group(1).strip()

            # Format 2: "Reply:" label
            if not reply_text:
                reply_match = re.search(r'Reply:\s*\n(.+?)(?=\n##|\n---|\Z)', body, re.DOTALL)
                if reply_match:
                    reply_text = reply_match.group(1).strip()

            # Format 3: Just use body if no specific format found
            if not reply_text:
                reply_text = body

            # Clean up: Remove any trailing instructions or metadata
            # Stop at "---" or "## Instructions"
            if '---' in reply_text:
                reply_text = reply_text.split('---')[0].strip()
            if '## Instructions' in reply_text:
                reply_text = reply_text.split('## Instructions')[0].strip()

            return {
                'chat_name': metadata.get('chat_name', ''),
                'chat_id': metadata.get('chat_id', ''),
                'reply_text': reply_text,
                'metadata': metadata
            }

        except Exception as e:
            print(f"✗ Error parsing file {filepath}: {e}")
            return None

    def _log_action(self, action, chat_name, message, status, error=None):
        """Log action to System_Log.md"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"\n## {timestamp}\n"
            log_entry += f"- **Action**: {action}\n"
            log_entry += f"- **Chat**: {chat_name}\n"
            log_entry += f"- **Status**: {status}\n"
            if self.dry_run:
                log_entry += f"- **Mode**: DRY_RUN\n"
            if error:
                log_entry += f"- **Error**: {error}\n"
            log_entry += f"- **Message**: {message[:100]}...\n" if len(message) > 100 else f"- **Message**: {message}\n"
            log_entry += "\n"

            # Append to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            print(f"✓ Logged action to {self.log_file}")

        except Exception as e:
            print(f"✗ Error logging action: {e}")

    def _send_message_to_open_chat(self, page, expected_chat_name, message_text):
        """Send message to currently open chat after verification"""
        try:
            print(f"\n{'='*60}")
            print(f"Expected chat: {expected_chat_name}")
            print(f"Message to send: {message_text[:100]}...")
            print(f"{'='*60}")

            # Verify correct chat is open
            print("\nVerifying chat name...")
            time.sleep(1)

            # Get chat name from header
            header_selectors = [
                'header span[dir="auto"]',
                'header [data-testid="conversation-info-header"]',
                'header span[title]'
            ]

            current_chat_name = None
            for selector in header_selectors:
                try:
                    header_elem = page.query_selector(selector)
                    if header_elem:
                        current_chat_name = header_elem.inner_text().strip()
                        if current_chat_name:
                            print(f"✓ Currently open chat: {current_chat_name}")
                            break
                except:
                    continue

            if not current_chat_name:
                print("✗ Could not read chat name from header")
                return False

            # Verify chat name matches (case-insensitive)
            if current_chat_name.lower() != expected_chat_name.lower():
                print(f"\n⚠️  WARNING: Wrong chat is open!")
                print(f"   Expected: {expected_chat_name}")
                print(f"   Current:  {current_chat_name}")
                return False

            print(f"✓ Correct chat is open: {current_chat_name}")

            # Find message input box
            print("\nFinding message input box...")
            input_selectors = [
                '[data-testid="conversation-compose-box-input"]',
                'footer div[contenteditable="true"]',
                'div[contenteditable="true"][data-tab="10"]'
            ]

            message_box = None
            for selector in input_selectors:
                try:
                    message_box = page.query_selector(selector)
                    if message_box:
                        print(f"✓ Found message box: {selector}")
                        break
                except:
                    continue

            if not message_box:
                print("✗ Could not find message box")
                return False

            # Click and focus
            message_box.click()
            time.sleep(0.5)

            # Type message
            print("Typing message...")
            lines = message_text.split('\n')
            for i, line in enumerate(lines):
                page.keyboard.type(line, delay=50)
                if i < len(lines) - 1:
                    page.keyboard.press('Shift+Enter')
                    time.sleep(0.1)

            print("✓ Message typed")
            time.sleep(0.5)

            # Send with Enter key
            print("Sending message...")
            page.keyboard.press('Enter')
            time.sleep(2)

            print("✓ Message sent successfully!")
            return True

        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def _move_to_done(self, filepath):
        """Move processed file to Done folder"""
        try:
            filename = filepath.name
            destination = self.done_dir / filename

            # Handle duplicate filenames
            counter = 1
            while destination.exists():
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    destination = self.done_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    destination = self.done_dir / f"{filename}_{counter}"
                counter += 1

            filepath.rename(destination)
            print(f"✓ Moved file to: {destination}")
            return True

        except Exception as e:
            print(f"✗ Error moving file: {e}")
            return False

    def process_approved_messages(self):
        """Process all approved messages in the Approved folder"""
        print("=" * 60)
        print("WhatsApp Sender - Fixed Version")
        print("=" * 60)
        print(f"Mode: {'DRY_RUN (no messages will be sent)' if self.dry_run else 'LIVE (messages WILL be sent)'}")
        print(f"Approved directory: {self.approved_dir}")
        print(f"Done directory: {self.done_dir}")
        print(f"Log file: {self.log_file}")
        print("=" * 60)

        # Find all WHATSAPP_REPLY_*.md files
        reply_files = sorted(self.approved_dir.glob("WHATSAPP_REPLY_*.md"))

        if not reply_files:
            print("\n✓ No files to process in Approved folder")
            return

        print(f"\nFound {len(reply_files)} file(s) to process\n")

        # Use fresh browser context (no persistent session to avoid corruption)
        with sync_playwright() as p:
            try:
                print("Launching browser...")
                browser = p.chromium.launch(
                    headless=False,
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
                )

                context = browser.new_context()
                page = context.new_page()

                # Navigate to WhatsApp Web
                print("Navigating to WhatsApp Web...")
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

                # Wait for user to scan QR code or for WhatsApp to load
                print("\n" + "="*60)
                print("IMPORTANT: Please scan QR code if needed")
                print("Wait for WhatsApp to fully load")
                print("="*60)

                try:
                    print("\nWaiting for WhatsApp to load (max 120 seconds)...")
                    page.wait_for_selector("div[role='grid']", timeout=120000)
                    print("✓ WhatsApp Web loaded successfully\n")
                except PlaywrightTimeout:
                    print("✗ Timeout waiting for WhatsApp to load")
                    print("Please make sure you're logged in and try again")
                    browser.close()
                    return

                # Process each file
                for filepath in reply_files:
                    print(f"\n{'='*60}")
                    print(f"Processing: {filepath.name}")
                    print(f"{'='*60}")

                    # Parse file
                    data = self._parse_markdown_file(filepath)
                    if not data:
                        print(f"✗ Failed to parse file: {filepath.name}")
                        self._log_action("PARSE_ERROR", "Unknown", "", "FAILED", "Could not parse file")
                        continue

                    chat_name = data['chat_name']
                    reply_text = data['reply_text']

                    print(f"\nChat Name: {chat_name}")
                    print(f"Message Preview: {reply_text[:100]}...")

                    if self.dry_run:
                        print("\n[DRY_RUN] Would send message to:", chat_name)
                        print("[DRY_RUN] Message:", reply_text)
                        self._log_action("SEND_MESSAGE", chat_name, reply_text, "DRY_RUN")
                        self._move_to_done(filepath)
                        print("✓ DRY_RUN completed")
                        continue

                    # LIVE MODE - Manual chat opening
                    print(f"\n{'='*60}")
                    print(f"📱 MANUAL STEP REQUIRED")
                    print(f"{'='*60}")
                    print(f"\n1. Go to WhatsApp Web browser window")
                    print(f"2. Manually open the chat: {chat_name}")
                    print(f"3. Make sure the correct chat is open")
                    print(f"4. Come back here and press ENTER")
                    print(f"\n⚠️  WARNING: Make sure you open the EXACT chat: {chat_name}")

                    # Wait for user to open chat manually
                    input("\nPress ENTER when you have opened the correct chat... ")

                    # Send message
                    print("\nVerifying chat and sending message...")
                    if self._send_message_to_open_chat(page, chat_name, reply_text):
                        self._log_action("SEND_MESSAGE", chat_name, reply_text, "SUCCESS")
                        self._move_to_done(filepath)
                        print(f"\n✓ Successfully sent message to: {chat_name}")
                    else:
                        self._log_action("SEND_MESSAGE", chat_name, reply_text, "FAILED", "Verification failed or could not send")
                        print(f"\n✗ Failed to send message")

                        # Ask if user wants to retry
                        retry = input("\nDo you want to retry? (y/n): ").lower()
                        if retry == 'y':
                            print("\nRetrying... Make sure correct chat is open.")
                            input("Press ENTER when ready... ")
                            if self._send_message_to_open_chat(page, chat_name, reply_text):
                                self._log_action("SEND_MESSAGE", chat_name, reply_text, "SUCCESS")
                                self._move_to_done(filepath)
                                print(f"\n✓ Successfully sent message to: {chat_name}")
                            else:
                                print(f"\n✗ Retry failed. Skipping this message.")

                    # Wait between messages
                    time.sleep(2)

                browser.close()
                print("\n✓ Browser closed")
                print("\n" + "="*60)
                print("Processing complete")
                print("="*60)

            except Exception as e:
                print(f"\n✗ Fatal error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    # Set to False for LIVE mode (actually send messages)
    # Set to True for DRY_RUN mode (test without sending)
    DRY_RUN = False

    sender = WhatsAppSenderFixed(
        approved_dir="AI_Employee_Vault/Approved",
        done_dir="AI_Employee_Vault/Done",
        log_file="AI_Employee_Vault/System_Log.md",
        dry_run=DRY_RUN
    )

    sender.process_approved_messages()

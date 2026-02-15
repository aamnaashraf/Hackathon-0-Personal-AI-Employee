#!/usr/bin/env python3
"""
WhatsApp Sender - Sends approved messages via WhatsApp Web
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class WhatsAppSender:
    def __init__(
        self,
        session_dir="whatsapp_session",
        approved_dir="Approved",
        done_dir="Done",
        log_file="System_Log.md",
        dry_run=True
    ):
        self.session_dir = Path(session_dir).resolve()
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

            # Format 1: "## Draft Reply" section (most common)
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

    def _verify_and_send_message(self, page, expected_chat_name, message_text):
        """Verify correct chat is open and send message"""
        try:
            print(f"\n{'='*60}")
            print(f"Expected chat: {expected_chat_name}")
            print(f"Message to send: {message_text}")
            print(f"{'='*60}")

            # Get currently open chat name from header
            print("\nReading currently open chat name...")

            current_chat_name = None
            header_selectors = [
                'header span[dir="auto"]',
                'header [data-testid="conversation-info-header"]',
                'header span[title]'
            ]

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
                print("Make sure a chat is open!")
                return False

            # Verify chat name matches (flexible matching)
            # Clean up both names: remove trailing dots, spaces, and normalize
            expected_clean = expected_chat_name.lower().strip().rstrip('.')
            current_clean = current_chat_name.lower().strip().rstrip('.')

            # Check if names match (exact, starts with, or contains)
            names_match = (
                expected_clean == current_clean or
                current_clean.startswith(expected_clean) or
                expected_clean.startswith(current_clean) or
                expected_clean in current_clean or
                current_clean in expected_clean
            )

            if not names_match:
                print(f"\n⚠️  WARNING: Wrong chat is open!")
                print(f"   Expected: {expected_chat_name}")
                print(f"   Current:  {current_chat_name}")
                print(f"\n   Please open the correct chat and try again.")
                return False

            print(f"✓ Correct chat is open: {current_chat_name}")

            # Now send the message
            print("\nSending message...")
            time.sleep(0.5)

            # Find message box in footer
            message_box = None
            input_selectors = [
                '[data-testid="conversation-compose-box-input"]',
                'footer div[contenteditable="true"]',
                'div[contenteditable="true"][data-tab="10"]'
            ]

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

            # Click and focus on message box
            message_box.click()
            time.sleep(0.3)

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

            # Send using Enter key (most reliable)
            print("Sending with Enter key...")
            page.keyboard.press('Enter')
            time.sleep(1.5)

            print("✓ Message sent successfully!")
            return True

        except Exception as e:
            print(f"✗ Error: {e}")
            return False
        """Search for a chat and open it"""
        try:
            print(f"Searching for: {chat_name}")

            # Find and click search box
            search_selectors = [
                '[data-testid="chat-list-search"]',
                'div[contenteditable="true"][data-tab="3"]',
                '[title="Search input textbox"]'
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = page.wait_for_selector(selector, timeout=3000)
                    if search_box:
                        break
                except:
                    continue

            if not search_box:
                print("✗ Could not find search box")
                return False

            # Click and type chat name
            search_box.click()
            time.sleep(0.5)
            search_box.fill(chat_name)
            print(f"Typed '{chat_name}' in search box")
            time.sleep(2)  # Wait longer for results

            # Wait for search results to appear
            page.wait_for_timeout(1500)

            # Try to click on the chat using multiple methods
            clicked = False

            # Method 1: Use JavaScript to find and click the chat row
            try:
                clicked = page.evaluate(f'''() => {{
                    const titleSpan = document.querySelector('span[title="{chat_name}"]');
                    if (titleSpan) {{
                        let current = titleSpan;
                        while (current && current.getAttribute('role') !== 'row') {{
                            current = current.parentElement;
                        }}
                        if (current) {{
                            current.click();
                            return true;
                        }}
                    }}
                    return false;
                }}''')
                if clicked:
                    print(f"✓ Clicked on chat (Method 1 - JavaScript)")
            except Exception as e:
                print(f"Method 1 failed: {e}")

            # Method 2: Click first search result using JavaScript
            if not clicked:
                try:
                    clicked = page.evaluate('''() => {
                        const results = document.querySelectorAll('div[role="listitem"]');
                        if (results.length > 0) {
                            results[0].click();
                            return true;
                        }
                        return false;
                    }''')
                    if clicked:
                        print(f"✓ Clicked on chat (Method 2 - JavaScript)")
                except Exception as e:
                    print(f"Method 2 failed: {e}")

            # Method 3: Use Playwright's click on first result
            if not clicked:
                try:
                    results = page.query_selector_all('div[role="listitem"]')
                    if results and len(results) > 0:
                        results[0].click()
                        clicked = True
                        print(f"✓ Clicked on chat (Method 3 - Playwright)")
                except Exception as e:
                    print(f"Method 3 failed: {e}")

            if not clicked:
                print(f"✗ Could not click on chat: {chat_name}")
                return False

            # Wait for chat to open
            print("Waiting for chat to open...")
            time.sleep(3)  # Increased wait time

            # Verify chat is open by checking for message input
            # Try multiple selectors
            message_box = None
            message_selectors = [
                '[data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][role="textbox"]',
                'footer div[contenteditable="true"]'
            ]

            for selector in message_selectors:
                try:
                    message_box = page.query_selector(selector)
                    if message_box:
                        print(f"✓ Found message box with selector: {selector}")
                        break
                except:
                    continue

            if not message_box:
                print("✗ Chat did not open properly - message box not found")
                print("Trying to clear search and retry...")

                # Try clearing search
                try:
                    page.keyboard.press('Escape')
                    time.sleep(0.5)
                    page.keyboard.press('Escape')
                    time.sleep(0.5)
                    print("✓ Cleared search box")
                except:
                    pass

                # Check again
                time.sleep(2)
                for selector in message_selectors:
                    try:
                        message_box = page.query_selector(selector)
                        if message_box:
                            print(f"✓ Found message box on retry: {selector}")
                            break
                    except:
                        continue

                if not message_box:
                    return False

            print(f"✓ Chat opened successfully: {chat_name}")
            return True

        except Exception as e:
            print(f"✗ Error searching/opening chat: {e}")
            return False

    def _send_message(self, page, message_text):
        """Type and send a message"""
        try:
            print(f"Preparing to send message: {message_text[:50]}...")

            # FIRST: Clear search box completely to remove focus
            print("Clearing search box...")
            try:
                page.keyboard.press('Escape')
                time.sleep(0.3)
                page.keyboard.press('Escape')
                time.sleep(0.5)
                print("✓ Search box cleared")
            except:
                pass

            # Find message input box - use ONLY specific selectors for compose box
            input_selectors = [
                '[data-testid="conversation-compose-box-input"]',  # Most specific
                'footer div[contenteditable="true"]',              # In footer only
                'div[contenteditable="true"][data-tab="10"]'       # Compose tab
            ]

            message_box = None
            for selector in input_selectors:
                try:
                    message_box = page.wait_for_selector(selector, timeout=3000)
                    if message_box:
                        print(f"✓ Found message box with selector: {selector}")
                        break
                except:
                    continue

            if not message_box:
                print("✗ Could not find message input box")
                return False

            # Click on message box multiple times to ensure focus
            print("Clicking on message box...")
            message_box.click()
            time.sleep(0.3)
            message_box.click()
            time.sleep(0.3)

            # Use JavaScript to force focus on FOOTER message box only
            try:
                page.evaluate('''() => {
                    // Clear search first
                    const searchBox = document.querySelector('div[contenteditable="true"][data-tab="3"]');
                    if (searchBox) {
                        searchBox.blur();
                        searchBox.textContent = '';
                    }

                    // Focus on message box in footer
                    const messageBox = document.querySelector('footer div[contenteditable="true"]') ||
                                      document.querySelector('[data-testid="conversation-compose-box-input"]');
                    if (messageBox) {
                        messageBox.focus();
                        messageBox.click();
                    }
                }''')
                print("✓ Focused message box using JavaScript")
            except Exception as e:
                print(f"JavaScript focus warning: {e}")

            time.sleep(0.5)

            # Type message using page.keyboard (types in focused element)
            print("Typing message...")

            # Handle multi-line messages (replace \n with Shift+Enter)
            lines = message_text.split('\n')
            for i, line in enumerate(lines):
                page.keyboard.type(line, delay=50)  # Add delay between keystrokes
                if i < len(lines) - 1:
                    page.keyboard.press('Shift+Enter')
                    time.sleep(0.1)

            print("✓ Message typed successfully")
            time.sleep(0.5)

            # Find and click send button - use multiple selectors
            send_selectors = [
                '[data-testid="send"]',
                'button[aria-label="Send"]',
                'span[data-icon="send"]',
                'footer button[aria-label*="Send"]'
            ]

            send_button = None
            for selector in send_selectors:
                try:
                    send_button = page.query_selector(selector)
                    if send_button:
                        print(f"✓ Found send button with selector: {selector}")
                        break
                except:
                    continue

            if not send_button:
                print("✗ Could not find send button")
                print("Trying to send with Enter key...")
                try:
                    page.keyboard.press('Enter')
                    time.sleep(1.5)
                    print("✓ Message sent using Enter key")
                    return True
                except:
                    return False

            # Click send button
            print("Clicking send button...")
            send_button.click()
            time.sleep(1.5)

            print("✓ Message sent successfully")
            return True

        except Exception as e:
            print(f"✗ Error sending message: {e}")
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
        print("WhatsApp Sender")
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

        with sync_playwright() as p:
            try:
                # Launch browser with persistent context
                print("Launching browser with existing session...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_dir),
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )

                # Get or create page
                if len(browser.pages) > 0:
                    page = browser.pages[0]
                else:
                    page = browser.new_page()

                # Navigate to WhatsApp Web
                print("Navigating to WhatsApp Web...")
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

                # Wait for WhatsApp to load (using same selector as watcher)
                try:
                    print("Waiting for WhatsApp to load...")
                    page.wait_for_selector("div[role='grid']", timeout=60000)
                    print("✓ WhatsApp Web loaded successfully\n")

                except PlaywrightTimeout:
                    print("✗ Timeout waiting for WhatsApp to load")
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
                    print(f"Message: {reply_text}")

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

                    # Verify and send message
                    print("\nVerifying chat and sending message...")
                    if self._verify_and_send_message(page, chat_name, reply_text):
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
                            if self._verify_and_send_message(page, chat_name, reply_text):
                                self._log_action("SEND_MESSAGE", chat_name, reply_text, "SUCCESS")
                                self._move_to_done(filepath)
                                print(f"\n✓ Successfully sent message to: {chat_name}")
                            else:
                                print(f"\n✗ Retry failed. Skipping this message.")

                    # Wait between messages
                    time.sleep(1)

                browser.close()
                print("\n✓ Browser closed")
                print("\n" + "="*60)
                print("Processing complete")
                print("="*60)

            except Exception as e:
                print(f"\n✗ Fatal error: {e}")


if __name__ == "__main__":
    # DRY_RUN = True means no messages will be sent (safe mode)
    # DRY_RUN = False means messages WILL be sent (live mode)
    DRY_RUN = False  # CHANGED TO FALSE - LIVE MODE

    sender = WhatsAppSender(
        session_dir="whatsapp_session",
        approved_dir="AI_Employee_Vault/Approved",
        done_dir="AI_Employee_Vault/Done",
        log_file="AI_Employee_Vault/System_Log.md",
        dry_run=DRY_RUN
    )

    sender.process_approved_messages()
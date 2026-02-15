#!/usr/bin/env python3
"""
WhatsApp Done Folder Sender - Monitors Done folder and sends WhatsApp messages automatically
Works exactly like the email workflow: Approved → Done → Auto-send
"""

import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT = Path("AI_Employee_Vault")
SESSION_DIR = Path("whatsapp_session")
DONE = VAULT / "Done"
LOGS = VAULT / "Logs"

DONE.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)


class WhatsAppDoneFolderHandler(FileSystemEventHandler):
    """Handles WhatsApp message sending when files are moved to Done folder"""

    def __init__(self, page):
        self.page = page
        self.processed_files = set()

    def on_created(self, event):
        """Triggered when a file is created/moved to Done folder"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's a WhatsApp reply file
        if not file_path.name.startswith('WHATSAPP_REPLY_') or not file_path.name.endswith('.md'):
            return

        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return

        print(f"\n{'='*70}")
        print(f"[NEW FILE] {file_path.name}")
        print(f"[ACTION] Sending WhatsApp message automatically...")
        print(f"{'='*70}\n")

        # Wait a moment for file to be fully written
        time.sleep(0.5)

        # Process the WhatsApp message
        self.send_whatsapp_message(file_path)

        # Mark as processed
        self.processed_files.add(str(file_path))

    def send_whatsapp_message(self, file_path):
        """Extract message details and send via WhatsApp"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract chat name and message
            chat_name = ""
            message = ""
            in_reply = False

            for line in content.split('\n'):
                if line.startswith("chat_name:"):
                    chat_name = line.split(":", 1)[1].strip()
                if "## Draft Reply" in line or "Reply:" in line:
                    in_reply = True
                    continue
                if in_reply and line.strip() and not line.startswith('#') and not line.startswith('---'):
                    message += line + "\n"

            message = message.strip()

            if not chat_name or not message:
                print(f"[ERROR] Could not extract chat_name or message from {file_path.name}")
                return

            print(f"[TO] {chat_name}")
            print(f"[MESSAGE] {message[:100]}...")

            # Send message via WhatsApp
            success = self.send_message(chat_name, message)

            if success:
                print(f"[SUCCESS] Message sent to {chat_name}")
                self.log_action(file_path.name, chat_name, message, "sent")
            else:
                print(f"[ERROR] Failed to send message to {chat_name}")
                self.log_action(file_path.name, chat_name, message, "failed")

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}")
            self.log_action(file_path.name, "unknown", "unknown", "error", str(e))

    def send_message(self, chat_name, message):
        """Send a WhatsApp message"""
        try:
            # Search for chat
            search_box = self.page.query_selector("div[contenteditable='true'][data-tab='3']")
            if not search_box:
                print("[ERROR] Could not find search box")
                return False

            search_box.click()
            time.sleep(0.5)
            search_box.fill("")
            time.sleep(0.3)
            search_box.fill(chat_name)
            time.sleep(2)

            # Click first result
            first_chat = self.page.query_selector("div[role='row']")
            if not first_chat:
                print("[ERROR] Could not find chat in search results")
                return False

            first_chat.click()
            time.sleep(1)

            # Type and send message
            message_box = self.page.query_selector("div[contenteditable='true'][data-tab='10']")
            if not message_box:
                print("[ERROR] Could not find message box")
                return False

            message_box.click()
            time.sleep(0.3)
            message_box.fill(message)
            time.sleep(0.5)
            self.page.keyboard.press("Enter")
            time.sleep(1)

            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False

    def log_action(self, filename, chat_name, message, status, error=None):
        """Log WhatsApp sending actions"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = LOGS / f'{today}_whatsapp_sender.log'

        log_entry = f"[{datetime.now().isoformat()}] {filename} | To: {chat_name} | Status: {status}"
        if error:
            log_entry += f" | Error: {error}"
        log_entry += "\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def main():
    """Main function to start the WhatsApp Done folder watcher"""
    print("\n" + "="*70)
    print(" " * 20 + "WhatsApp Done Folder Sender")
    print("="*70)
    print("\nWatching Done folder for WhatsApp replies...")
    print("When you move approved messages to Done, they will be sent automatically")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")

    print("[BROWSER] Launching WhatsApp Web...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://web.whatsapp.com")

        print("[WHATSAPP] Waiting for WhatsApp to load...")
        try:
            page.wait_for_selector("div[role='grid']", timeout=60000)
            print("[WHATSAPP] ✓ WhatsApp Ready\n")
        except:
            print("[ERROR] WhatsApp did not load. Please scan QR code if needed.")
            return

        print(f"[WATCHING] {DONE}\n")

        # Setup file watcher
        event_handler = WhatsAppDoneFolderHandler(page)
        observer = Observer()
        observer.schedule(event_handler, str(DONE), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[STOPPING] Shutting down WhatsApp sender...")
            observer.stop()

        observer.join()
        browser.close()
        print("[STOPPED] WhatsApp sender stopped")


if __name__ == "__main__":
    main()

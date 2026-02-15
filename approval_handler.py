#!/usr/bin/env python3
"""
Unified Approval Handler - Monitors Approved folder and triggers appropriate actions
Supports: Instagram, Facebook, LinkedIn, WhatsApp, Email, and other social media posts
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import subprocess

load_dotenv()


class ApprovalHandler:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.vault_path = Path(os.getenv('VAULT_PATH', self.base_dir / 'AI_Employee_Vault'))
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'

        # Create directories
        for dir_path in [self.approved_dir, self.done_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Track processed files to avoid duplicates
        self.processed_files = set()

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print(" " * 20 + "Approval Handler")
        print("="*70)
        print("\nMonitoring Approved folder for:")
        print("  [INSTA] Instagram posts (INSTA_POST_*.md)")
        print("  [FB] Facebook posts (FB_POST_*.md)")
        print("  [LINKEDIN] LinkedIn posts (LINKEDIN_POST_*.md)")
        print("  [WHATSAPP] WhatsApp replies (WHATSAPP_REPLY_*.md)")
        print("  [EMAIL] Email replies (REPLY_APPROVED_*.md)")
        print("\nPress Ctrl+C to stop monitoring")
        print("="*70 + "\n")

    def scan_approved_folder(self):
        """Scan Approved folder for new files"""
        if not self.approved_dir.exists():
            return []

        all_files = list(self.approved_dir.glob("*.md"))

        # Filter out already processed files
        new_files = [f for f in all_files if str(f) not in self.processed_files]

        return new_files

    def detect_file_type(self, file_path):
        """Detect the type of approved file"""
        filename = file_path.name.upper()

        if filename.startswith("INSTA_POST_"):
            return "instagram_post"
        elif filename.startswith("FB_POST_"):
            return "facebook_post"
        elif filename.startswith("LINKEDIN_POST_"):
            return "linkedin_post"
        elif filename.startswith("WHATSAPP_REPLY_"):
            return "whatsapp_reply"
        elif filename.startswith("REPLY_APPROVED_"):
            return "email_reply"
        else:
            return "unknown"

    def process_instagram_post(self, file_path):
        """Process Instagram post using instagram_personal_poster"""
        print(f"\n[INSTAGRAM] Processing: {file_path.name}")

        try:
            # Import and run Instagram poster
            from instagram_personal_poster import InstagramPersonalPoster

            poster = InstagramPersonalPoster()

            # Read post content
            post_content = poster.read_post_draft(file_path)
            if not post_content:
                print(f"[ERROR] Could not read post content")
                return False

            # Extract media path if specified
            media_path = poster.extract_media_path(file_path)

            print(f"[CONTENT] Caption preview: {post_content[:100]}...")
            if media_path:
                print(f"[MEDIA] Media file: {media_path}")

            # Start browser and post
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                print("[BROWSER] Launching browser...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(poster.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720},
                    args=['--start-maximized']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Login
                if not poster.login_to_instagram(page):
                    print("[ERROR] Failed to login to Instagram")
                    browser.close()
                    return False

                # Post
                success = poster.post_to_profile(page, post_content, media_path)

                if success:
                    print("[SUCCESS] Posted to Instagram!")

                    # Move to Done
                    done_file = self.done_dir / file_path.name
                    file_path.rename(done_file)
                    print(f"[DONE] Moved to: {done_file.name}")

                    # Update dashboard
                    poster.update_dashboard(file_path.name, post_content)

                    # Log action
                    self.log_action("instagram_post", file_path.name, "success")

                time.sleep(5)
                browser.close()

                return success

        except Exception as e:
            print(f"[ERROR] Instagram posting failed: {e}")
            self.log_action("instagram_post", file_path.name, "failed", str(e))
            return False

    def process_facebook_post(self, file_path):
        """Process Facebook post using facebook_personal_poster"""
        print(f"\n[FACEBOOK] Processing: {file_path.name}")

        try:
            # Import and run Facebook poster
            from facebook_personal_poster import FacebookPersonalPoster

            poster = FacebookPersonalPoster()

            # Read post content
            post_content = poster.read_post_draft(file_path)
            if not post_content:
                print(f"[ERROR] Could not read post content")
                return False

            print(f"[CONTENT] Post preview: {post_content[:100]}...")

            # Start browser and post
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                print("[BROWSER] Launching browser...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(poster.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720},
                    args=['--start-maximized']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Login
                if not poster.login_to_facebook(page):
                    print("[ERROR] Failed to login to Facebook")
                    browser.close()
                    return False

                # Post
                success = poster.post_to_profile(page, post_content)

                if success:
                    print("[SUCCESS] Posted to Facebook!")

                    # Move to Done
                    done_file = self.done_dir / file_path.name
                    file_path.rename(done_file)
                    print(f"[DONE] Moved to: {done_file.name}")

                    # Update dashboard
                    poster.update_dashboard(file_path.name, post_content)

                    # Log action
                    self.log_action("facebook_post", file_path.name, "success")

                time.sleep(5)
                browser.close()

                return success

        except Exception as e:
            print(f"[ERROR] Facebook posting failed: {e}")
            self.log_action("facebook_post", file_path.name, "failed", str(e))
            return False

    def process_linkedin_post(self, file_path):
        """Process LinkedIn post"""
        print(f"\n[LINKEDIN] Processing: {file_path.name}")

        try:
            # Use existing LinkedIn processor
            result = subprocess.run(
                [sys.executable, "complete_linkedin_tasks.py"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("[SUCCESS] LinkedIn post processed!")
                self.log_action("linkedin_post", file_path.name, "success")
                return True
            else:
                print(f"[ERROR] LinkedIn posting failed: {result.stderr}")
                self.log_action("linkedin_post", file_path.name, "failed", result.stderr)
                return False

        except Exception as e:
            print(f"[ERROR] LinkedIn posting failed: {e}")
            self.log_action("linkedin_post", file_path.name, "failed", str(e))
            return False

    def process_whatsapp_reply(self, file_path):
        """Process WhatsApp reply"""
        print(f"\n[WHATSAPP] Processing: {file_path.name}")
        print("[INFO] WhatsApp replies require manual sending via whatsapp_sender.py")

        # Log for tracking
        self.log_action("whatsapp_reply", file_path.name, "pending_manual")
        return False

    def process_email_reply(self, file_path):
        """Process email reply"""
        print(f"\n[EMAIL] Processing: {file_path.name}")
        print("[INFO] Email replies require manual sending via email_mcp.py")

        # Log for tracking
        self.log_action("email_reply", file_path.name, "pending_manual")
        return False

    def process_file(self, file_path):
        """Process a single approved file"""
        file_type = self.detect_file_type(file_path)

        print(f"\n{'='*70}")
        print(f"[NEW FILE] {file_path.name}")
        print(f"[TYPE] {file_type}")
        print(f"{'='*70}")

        success = False

        if file_type == "instagram_post":
            success = self.process_instagram_post(file_path)
        elif file_type == "facebook_post":
            success = self.process_facebook_post(file_path)
        elif file_type == "linkedin_post":
            success = self.process_linkedin_post(file_path)
        elif file_type == "whatsapp_reply":
            success = self.process_whatsapp_reply(file_path)
        elif file_type == "email_reply":
            success = self.process_email_reply(file_path)
        else:
            print(f"[WARNING] Unknown file type: {file_path.name}")
            self.log_action("unknown", file_path.name, "skipped")

        # Mark as processed
        self.processed_files.add(str(file_path))

        return success

    def log_action(self, action_type, filename, status, error=None):
        """Log approval handler actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'filename': filename,
            'status': status,
            'error': error
        }

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_approval_handler.json'

        # Read existing logs
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def run_once(self):
        """Run a single scan and process all approved files"""
        print("[SCAN] Checking Approved folder...")

        new_files = self.scan_approved_folder()

        if not new_files:
            print("[INFO] No new files to process")
            return

        print(f"[FOUND] {len(new_files)} new file(s)")

        for file_path in new_files:
            self.process_file(file_path)

    def run_continuous(self, interval=30):
        """Run continuous monitoring"""
        self.print_banner()

        print(f"[START] Monitoring every {interval} seconds...")
        print(f"[FOLDER] {self.approved_dir}\n")

        try:
            while True:
                new_files = self.scan_approved_folder()

                if new_files:
                    print(f"\n[SCAN] Found {len(new_files)} new file(s)")

                    for file_path in new_files:
                        self.process_file(file_path)

                # Wait before next scan
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n[STOP] Approval handler stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Approval handler crashed: {e}")


if __name__ == "__main__":
    handler = ApprovalHandler()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        handler.run_once()
    else:
        # Run continuous monitoring
        handler.run_continuous(interval=30)

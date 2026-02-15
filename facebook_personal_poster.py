#!/usr/bin/env python3
"""
Facebook Personal Profile Poster - Uses Playwright to post to personal Facebook profile
Since Meta Graph API only supports Pages, this uses browser automation for personal profiles.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

load_dotenv()


class FacebookPersonalPoster:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.vault_path = Path(os.getenv('VAULT_PATH', self.base_dir / 'AI_Employee_Vault'))
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'

        # Facebook session (no credentials needed - manual login only)
        self.session_path = Path(os.getenv('FACEBOOK_SESSION_PATH', './facebook_session'))

        # Create directories
        for dir_path in [self.needs_action_dir, self.pending_approval_dir,
                         self.approved_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.session_path.mkdir(parents=True, exist_ok=True)

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print(" " * 15 + "Facebook Personal Profile Poster")
        print("="*70)
        print("\nThis tool posts to your PERSONAL Facebook profile using browser automation.")
        print("(Meta Graph API only supports Pages, not personal profiles)")
        print("\nWorkflow:")
        print("  1. Read draft from Approved folder")
        print("  2. Open Facebook in browser (visible mode)")
        print("  3. Login (using saved session or manual)")
        print("  4. Post to your personal profile")
        print("  5. Move completed post to Done folder")
        print("="*70 + "\n")

    def login_to_facebook(self, page):
        """Login to Facebook using saved session or manual browser login"""
        print("\n[LOGIN] Navigating to Facebook...")
        page.goto("https://www.facebook.com", wait_until="domcontentloaded", timeout=60000)

        # Wait a bit to see if we're already logged in
        time.sleep(3)

        # Check if already logged in by looking for profile or home feed
        if self._is_logged_in(page):
            print("[LOGIN] ✓ Already logged in (using saved session)")
            return True

        print("[LOGIN] Not logged in. Please login manually in the browser window...")
        print("[LOGIN] Your session will be saved for next time.")
        print("[LOGIN] Press Enter after you've logged in manually...")
        input()

        if self._is_logged_in(page):
            print("[LOGIN] ✓ Manual login successful - session saved!")
            return True
        else:
            print("[LOGIN] ✗ Login verification failed")
            return False

    def _is_logged_in(self, page):
        """Check if user is logged in to Facebook"""
        try:
            # Look for common elements that appear when logged in
            # Check for the "What's on your mind" post box or profile icon
            selectors = [
                'div[role="main"]',  # Main feed
                'a[aria-label*="Profile"]',  # Profile link
                'div[aria-label="Create a post"]',  # Post creation box
                'span:has-text("What\'s on your mind")',  # Post prompt
            ]

            for selector in selectors:
                try:
                    if page.locator(selector).is_visible(timeout=3000):
                        return True
                except:
                    continue

            return False
        except:
            return False

    def post_to_profile(self, page, post_content, media_path=None):
        """Post content to personal Facebook profile"""
        print("\n[POST] Starting post creation...")

        try:
            # Navigate to home/feed if not already there
            if "facebook.com" not in page.url or "/home" not in page.url:
                print("[POST] Navigating to Facebook home...")
                page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

            # Find and click the "What's on your mind" box to open post composer
            print("[POST] Looking for post creation box...")

            # Try multiple selectors for the post box
            post_box_selectors = [
                'div[aria-label="Create a post"]',
                'span:has-text("What\'s on your mind")',
                'div[role="button"]:has-text("What\'s on your mind")',
                'div.x1i10hfl:has-text("What\'s on your mind")',
            ]

            clicked = False
            for selector in post_box_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        element.click()
                        print(f"[POST] Clicked post box using selector: {selector}")
                        clicked = True
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("[POST] ⚠️  Could not find post box automatically")
                print("[POST] Please click 'What's on your mind' manually...")
                input("Press Enter after clicking the post box...")

            # Wait for the post composer modal to appear
            time.sleep(3)

            # Find the text input area in the composer
            print("[POST] Looking for text input area...")

            # Try multiple selectors for the text input
            text_input_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[aria-label*="What\'s on your mind"]',
                'div.notranslate[contenteditable="true"]',
            ]

            text_input = None
            for selector in text_input_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        text_input = element
                        print(f"[POST] Found text input using selector: {selector}")
                        break
                except:
                    continue

            if not text_input:
                print("[POST] ⚠️  Could not find text input automatically")
                print("[POST] Please paste your content manually:")
                print("\n" + "="*70)
                print(post_content)
                print("="*70 + "\n")
                input("Press Enter after pasting the content...")
            else:
                # Type the post content
                print("[POST] Typing post content...")
                text_input.click()
                time.sleep(1)

                # Type content line by line to handle newlines properly
                for line in post_content.split('\n'):
                    text_input.type(line)
                    page.keyboard.press('Shift+Enter')  # Newline in Facebook
                    time.sleep(0.1)

                print("[POST] ✓ Content typed successfully")

            # Handle media attachment if provided
            if media_path and Path(media_path).exists():
                print(f"[POST] Attaching media: {media_path}")
                print("[POST] ⚠️  Please attach the media file manually")
                print(f"[POST] File location: {media_path}")
                input("Press Enter after attaching the media...")

            # Wait a moment before posting
            time.sleep(2)

            # Check if privacy/audience selector needs attention
            print("[POST] Checking privacy settings...")
            try:
                # Look for audience selector - it might need to be set
                audience_selectors = [
                    'div[aria-label*="Select audience"]',
                    'div[aria-label*="Privacy"]',
                    'span:has-text("Friends")',
                    'span:has-text("Public")',
                ]

                for selector in audience_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=2000):
                            print(f"[POST] Found audience selector: {selector}")
                            break
                    except:
                        continue
            except:
                pass

            # Try keyboard shortcut first (most reliable)
            print("[POST] Attempting to post using Ctrl+Enter shortcut...")
            try:
                page.keyboard.press('Control+Enter')
                print("[POST] ✓ Pressed Ctrl+Enter")
                time.sleep(2)
            except Exception as e:
                print(f"[POST] Keyboard shortcut failed: {e}")

            # Also try clicking the Post button as backup
            print("[POST] Looking for Post button...")

            post_button_selectors = [
                'div[aria-label="Post"]',
                'div[role="button"]:has-text("Post")',
                'span:has-text("Post")',
                'div[aria-label="Post"][role="button"]',
            ]

            posted = False
            for selector in post_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        # Check if button is enabled
                        is_disabled = button.get_attribute('aria-disabled')
                        if is_disabled == 'true':
                            print(f"[POST] ⚠️  Post button is disabled: {selector}")
                            continue

                        print(f"[POST] Clicking Post button: {selector}")
                        button.click()
                        posted = True
                        break
                except Exception as e:
                    print(f"[POST] Failed with selector {selector}: {e}")
                    continue

            if not posted:
                print("[POST] ⚠️  Could not click Post button")
                print("[POST] Trying one more time with force click...")
                try:
                    # Force click with JavaScript
                    page.evaluate('''
                        const buttons = document.querySelectorAll('[aria-label="Post"]');
                        if (buttons.length > 0) {
                            buttons[0].click();
                        }
                    ''')
                    print("[POST] ✓ Force clicked Post button")
                except Exception as e:
                    print(f"[POST] Force click failed: {e}")

            # Wait for post to complete
            print("[POST] Waiting for post to complete...")
            time.sleep(3)

            # Verify post was successful by checking if modal closed
            try:
                # Check if the post composer modal is gone (indicates success)
                modal_gone = False
                for i in range(15):  # Check for 15 seconds
                    try:
                        # If we can't find the composer modal, it closed successfully
                        composer = page.locator('div[role="dialog"]').first
                        if not composer.is_visible(timeout=1000):
                            modal_gone = True
                            break
                    except:
                        modal_gone = True
                        break

                    # Also check for success indicators
                    try:
                        # Look for "Your post is now published" or similar messages
                        success_messages = [
                            'text="Your post is now published"',
                            'text="Post published"',
                            'text="Posted"',
                        ]
                        for msg in success_messages:
                            if page.locator(msg).is_visible(timeout=500):
                                print("[POST] ✓ Found success message!")
                                modal_gone = True
                                break
                    except:
                        pass

                    time.sleep(1)
                    print(f"[POST] Still waiting... ({i+1}/15)")

                if modal_gone:
                    print("[POST] ✓ Post composer closed - post successful!")
                    time.sleep(2)  # Give it a moment to fully complete
                    return True
                else:
                    print("[POST] ⚠️  Post composer still open after 15 seconds")
                    print("[POST] This usually means:")
                    print("        - Post button is disabled (check privacy settings)")
                    print("        - Facebook detected automation")
                    print("        - Network issue or error occurred")
                    print("\n[POST] Taking screenshot for debugging...")
                    try:
                        screenshot_path = "facebook_post_debug.png"
                        page.screenshot(path=screenshot_path)
                        print(f"[POST] Screenshot saved: {screenshot_path}")
                    except:
                        pass

                    print("\n[POST] Please complete manually:")
                    print("        1. Check if Post button is clickable")
                    print("        2. Click Post button manually")
                    print("        3. Wait for post to appear")
                    print("        4. Press Enter when done")
                    input()
                    return True  # Assume user completed it
            except Exception as e:
                print(f"[POST] ⚠️  Could not verify post status: {e}")
                print("[POST] Please verify manually if the post was published")
                print("[POST] Press Enter to continue...")
                input()
                return True

        except Exception as e:
            print(f"[POST] ✗ Error during posting: {e}")
            print("[POST] Please complete the post manually if needed...")
            input("Press Enter when done...")
            return False

    def read_post_draft(self, file_path):
        """Read post content from markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract post content from markdown
            # Look for content after frontmatter or headers
            lines = content.split('\n')
            post_lines = []
            in_frontmatter = False
            skip_next = False

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue

                if in_frontmatter:
                    continue

                # Skip headers and instructions
                if line.startswith('#') or 'Approval' in line or 'Instructions' in line:
                    skip_next = True
                    continue

                if skip_next and line.strip() == '':
                    skip_next = False
                    continue

                if not skip_next and line.strip():
                    post_lines.append(line)

            post_content = '\n'.join(post_lines).strip()
            return post_content

        except Exception as e:
            print(f"[ERROR] Failed to read draft: {e}")
            return None

    def process_approved_posts(self):
        """Process all approved Facebook posts"""
        # Look for Facebook post drafts in Approved folder
        fb_posts = list(self.approved_dir.glob("FB_POST_*.md"))

        if not fb_posts:
            print("[INFO] No approved Facebook posts found in Approved folder")
            return

        print(f"[INFO] Found {len(fb_posts)} approved post(s)")

        # Start browser
        with sync_playwright() as p:
            print("\n[BROWSER] Launching browser (visible mode)...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,  # Visible mode for demo
                viewport={'width': 1280, 'height': 720},
                args=['--start-maximized']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Login to Facebook
            if not self.login_to_facebook(page):
                print("[ERROR] Failed to login to Facebook")
                browser.close()
                return

            # Process each post
            for post_file in fb_posts:
                print(f"\n[PROCESS] Processing: {post_file.name}")

                # Read post content
                post_content = self.read_post_draft(post_file)
                if not post_content:
                    print(f"[ERROR] Could not read post content from {post_file.name}")
                    continue

                print(f"[CONTENT] Post preview:\n{post_content[:100]}...")

                # Post to Facebook
                success = self.post_to_profile(page, post_content)

                if success:
                    # Move to Done folder
                    done_file = self.done_dir / post_file.name
                    post_file.rename(done_file)
                    print(f"[DONE] ✓ Moved to Done: {done_file.name}")

                    # Update dashboard
                    self.update_dashboard(post_file.name, post_content)
                else:
                    print(f"[ERROR] Failed to post {post_file.name}")

                # Wait between posts
                if len(fb_posts) > 1:
                    print("\n[WAIT] Waiting 10 seconds before next post...")
                    time.sleep(10)

            print("\n[BROWSER] Keeping browser open for 10 seconds...")
            time.sleep(10)
            browser.close()
            print("[BROWSER] Browser closed")

    def update_dashboard(self, filename, content_preview):
        """Update Dashboard.md with post activity"""
        dashboard_file = self.vault_path / 'Dashboard.md'

        try:
            if dashboard_file.exists():
                dashboard_content = dashboard_file.read_text(encoding='utf-8')
            else:
                dashboard_content = "# AI Employee Dashboard\n\n## Recent Activity\n\n"

            # Add new entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_entry = f"- [{timestamp}] Posted to Facebook: {filename} - {content_preview[:50]}...\n"

            # Insert after "Recent Activity" header
            if "## Recent Activity" in dashboard_content:
                parts = dashboard_content.split("## Recent Activity")
                dashboard_content = parts[0] + "## Recent Activity\n\n" + new_entry + parts[1].lstrip('\n')
            else:
                dashboard_content += f"\n## Recent Activity\n\n{new_entry}"

            dashboard_file.write_text(dashboard_content, encoding='utf-8')
            print(f"[DASHBOARD] Updated Dashboard.md")

        except Exception as e:
            print(f"[WARNING] Could not update dashboard: {e}")

    def run(self):
        """Main execution"""
        self.print_banner()

        print("[INFO] This script uses manual browser login (no credentials needed)")
        print("[INFO] Your session will be saved for future use")
        print(f"[INFO] Session location: {self.session_path}")
        print()

        # Process approved posts
        self.process_approved_posts()

        print("\n[COMPLETE] Facebook posting session complete!")
        print(f"[INFO] Session saved to: {self.session_path}")


if __name__ == "__main__":
    poster = FacebookPersonalPoster()
    poster.run()

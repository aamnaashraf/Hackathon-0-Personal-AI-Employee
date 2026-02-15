#!/usr/bin/env python3
"""
Instagram Personal Profile Poster - Uses Playwright to post to personal Instagram profile
Since Meta Graph API only supports Business accounts, this uses browser automation for personal profiles.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
from instagram_image_generator import generate_instagram_image

load_dotenv()


class InstagramPersonalPoster:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.vault_path = Path(os.getenv('VAULT_PATH', self.base_dir / 'AI_Employee_Vault'))
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'

        # Instagram session (no credentials needed - manual login only)
        self.session_path = Path(os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session'))

        # Create directories
        for dir_path in [self.needs_action_dir, self.pending_approval_dir,
                         self.approved_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.session_path.mkdir(parents=True, exist_ok=True)

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print(" " * 15 + "Instagram Personal Profile Poster")
        print("="*70)
        print("\nThis tool posts to your PERSONAL Instagram profile using browser automation.")
        print("(Meta Graph API only supports Business accounts, not personal profiles)")
        print("\nWorkflow:")
        print("  1. Read draft from Approved folder")
        print("  2. Open Instagram in browser (visible mode)")
        print("  3. Login (using saved session or manual)")
        print("  4. Post to your personal profile")
        print("  5. Move completed post to Done folder")
        print("="*70 + "\n")

    def login_to_instagram(self, page):
        """Login to Instagram using saved session or manual browser login"""
        print("\n[LOGIN] Navigating to Instagram...")
        try:
            page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[LOGIN] Navigation slow, trying again...")
            try:
                page.goto("https://www.instagram.com", timeout=60000)
            except:
                print(f"[LOGIN] Still loading, continuing anyway...")

        # Wait a bit to see if we're already logged in
        time.sleep(3)

        # Check if already logged in
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
        """Check if user is logged in to Instagram"""
        try:
            # Look for common elements that appear when logged in
            selectors = [
                'svg[aria-label="Home"]',  # Home icon
                'svg[aria-label="New post"]',  # Create post icon
                'a[href*="/direct/inbox"]',  # Messages link
                'span:has-text("Create")',  # Create button
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
        """Post content to personal Instagram profile"""
        print("\n[POST] Starting post creation...")

        try:
            # Generate image from text if no media provided
            if not media_path or not Path(media_path).exists():
                print("[POST] No media provided, generating image from text...")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                generated_image = self.base_dir / f"instagram_generated_{timestamp}.jpg"

                try:
                    media_path = generate_instagram_image(post_content, str(generated_image))
                    print(f"[POST] ✓ Generated image: {media_path}")
                except Exception as e:
                    print(f"[POST] ✗ Failed to generate image: {e}")
                    print("[POST] Instagram requires an image. Cannot proceed.")
                    return False

            # Navigate to home if not already there
            if "instagram.com" not in page.url:
                print("[POST] Navigating to Instagram home...")
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

            # Find and click the Create/New Post button
            print("[POST] Looking for Create button...")

            # Try multiple selectors for the create button
            create_button_selectors = [
                'svg[aria-label="New post"]',  # Desktop create icon
                'svg[aria-label="Create"]',  # Alternative label
                'a[href="#"]:has(svg[aria-label="New post"])',  # Link with icon
                'span:has-text("Create")',  # Text button
                'div[role="menuitem"]:has-text("Create")',  # Menu item
            ]

            clicked = False
            for selector in create_button_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        element.click()
                        print(f"[POST] Clicked Create button using selector: {selector}")
                        clicked = True
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("[POST] ⚠️  Could not find Create button automatically")
                print("[POST] Please click the '+' or 'Create' button manually...")
                input("Press Enter after clicking Create...")

            # Wait for create menu to appear
            time.sleep(2)

            # Click "Post" option if menu appears
            print("[POST] Looking for Post option...")
            post_option_selectors = [
                'span:has-text("Post")',
                'div:has-text("Post")',
            ]

            for selector in post_option_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        element.click()
                        print("[POST] Selected Post option")
                        break
                except:
                    continue

            time.sleep(2)

            # Handle media upload (now required for Instagram)
            print(f"[POST] Uploading media: {media_path}")

            # Look for file input
            try:
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(str(Path(media_path).resolve()))
                print("[POST] ✓ Media uploaded successfully")
                time.sleep(3)
            except Exception as e:
                print(f"[POST] ✗ Could not upload media automatically: {e}")
                print(f"[POST] Please select the file manually: {media_path}")
                input("Press Enter after selecting the file...")

            # Click Next button after media selection
            print("[POST] Looking for Next button...")
            next_button_selectors = [
                'button:has-text("Next")',
                'div[role="button"]:has-text("Next")',
            ]

            for selector in next_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=5000):
                        button.click()
                        print("[POST] Clicked Next button (1/2)")
                        time.sleep(2)
                        # May need to click Next again for filters/editing
                        if button.is_visible(timeout=3000):
                            button.click()
                            print("[POST] Clicked Next button (2/2)")
                            time.sleep(2)
                        break
                except:
                    continue

            # Find the caption text area
            print("[POST] Looking for caption input area...")

            # Wait a bit for the post creation dialog to fully load
            time.sleep(3)

            caption_input_selectors = [
                'textarea[aria-label="Write a caption..."]',
                'textarea[placeholder="Write a caption..."]',
                'div[contenteditable="true"][aria-label*="caption"]',
                'div[contenteditable="true"]',  # Generic contenteditable
                'textarea',  # Fallback to any textarea
                'div[role="textbox"]',  # Role-based selector
            ]

            caption_input = None
            for selector in caption_input_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        caption_input = element
                        print(f"[POST] Found caption input using selector: {selector}")
                        break
                except:
                    continue

            if not caption_input:
                print("[POST] ⚠️  Could not find caption input automatically")
                print("[POST] MANUAL MODE: Please complete these steps:")
                print("\n" + "="*70)
                print("1. Paste this caption in the Instagram text box:")
                print("="*70)
                print(post_content)
                print("="*70)
                print("2. Click the 'Share' button")
                print("3. Wait for post to complete")
                print("="*70 + "\n")

                response = input("Did you successfully post? (yes/no): ").lower()
                if response != 'yes':
                    print("[POST] ✗ Post cancelled by user")
                    return False
                else:
                    print("[POST] ✓ Manual post confirmed")
                    return True
            else:
                # Type the caption
                print("[POST] Typing caption...")

                try:
                    # Click to focus the input
                    caption_input.click()
                    time.sleep(2)

                    # Clear any existing content
                    page.keyboard.press('Control+A')
                    page.keyboard.press('Backspace')
                    time.sleep(0.5)

                    # Type the content using keyboard (more reliable than element.type())
                    page.keyboard.type(post_content, delay=10)  # 10ms delay between keystrokes
                    print("[POST] ✓ Caption typed successfully")

                except Exception as e:
                    print(f"[POST] ✗ Auto-typing failed: {e}")
                    print("[POST] MANUAL MODE: Please paste the caption manually")
                    print("\n" + "="*70)
                    print(post_content)
                    print("="*70 + "\n")
                    input("Press Enter after pasting the caption...")

            # Wait a moment before posting
            time.sleep(2)

            # Find and click the Share button
            print("[POST] Looking for Share button...")

            share_button_selectors = [
                'button:has-text("Share")',
                'div[role="button"]:has-text("Share")',
                'button:has-text("Post")',  # Alternative text
                'button[type="button"]:has-text("Share")',
                '//button[contains(text(), "Share")]',  # XPath fallback
                '//div[@role="button" and contains(text(), "Share")]',
            ]

            posted = False
            for selector in share_button_selectors:
                try:
                    if selector.startswith('//'):
                        # XPath selector
                        button = page.locator(f'xpath={selector}').first
                    else:
                        button = page.locator(selector).first

                    if button.is_visible(timeout=5000):
                        print(f"[POST] Found Share button, clicking...")
                        button.click()
                        posted = True
                        break
                except Exception as e:
                    continue

            if not posted:
                print("[POST] ⚠️  Could not find Share button automatically")
                print("[POST] Please click the 'Share' button manually...")
                input("Press Enter after clicking Share...")
                posted = True

            # Wait for post to complete
            print("[POST] Waiting for post to complete...")
            time.sleep(5)

            # Look for success indicators
            success_detected = False
            try:
                success_selectors = [
                    'span:has-text("Post shared")',
                    'span:has-text("Your post has been shared")',
                    'img[alt*="Animated checkmark"]',
                ]
                for selector in success_selectors:
                    if page.locator(selector).is_visible(timeout=3000):
                        print("[POST] ✓ Post shared successfully!")
                        success_detected = True
                        break
            except:
                pass

            if not success_detected:
                # Ask user to confirm
                print("[POST] Could not auto-detect post success")
                response = input("Did the post appear on Instagram? (yes/no): ").lower()
                if response == 'yes':
                    print("[POST] ✓ Post completed!")
                    return True
                else:
                    print("[POST] ✗ Post may have failed")
                    return False

            # Verify post was successful
            print("[POST] ✓ Post completed!")
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

    def extract_media_path(self, file_path):
        """Extract media file path from draft if specified"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Look for media path in frontmatter or content
            for line in content.split('\n'):
                if 'media:' in line.lower() or 'image:' in line.lower() or 'photo:' in line.lower():
                    # Extract path after colon
                    media_path = line.split(':', 1)[1].strip()
                    if media_path and Path(media_path).exists():
                        return media_path

            return None
        except:
            return None

    def process_approved_posts(self):
        """Process all approved Instagram posts"""
        # Look for Instagram post drafts in Approved folder
        insta_posts = list(self.approved_dir.glob("INSTA_POST_*.md"))

        if not insta_posts:
            print("[INFO] No approved Instagram posts found in Approved folder")
            return

        print(f"[INFO] Found {len(insta_posts)} approved post(s)")

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

            # Login to Instagram
            if not self.login_to_instagram(page):
                print("[ERROR] Failed to login to Instagram")
                browser.close()
                return

            # Process each post
            for post_file in insta_posts:
                print(f"\n[PROCESS] Processing: {post_file.name}")

                # Read post content
                post_content = self.read_post_draft(post_file)
                if not post_content:
                    print(f"[ERROR] Could not read post content from {post_file.name}")
                    continue

                # Extract media path if specified
                media_path = self.extract_media_path(post_file)

                print(f"[CONTENT] Caption preview:\n{post_content[:100]}...")
                if media_path:
                    print(f"[MEDIA] Media file: {media_path}")

                # Post to Instagram
                success = self.post_to_profile(page, post_content, media_path)

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
                if len(insta_posts) > 1:
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
            new_entry = f"- [{timestamp}] Posted to Instagram: {filename} - {content_preview[:50]}...\n"

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

        print("\n[COMPLETE] Instagram posting session complete!")
        print(f"[INFO] Session saved to: {self.session_path}")


if __name__ == "__main__":
    poster = InstagramPersonalPoster()
    poster.run()

#!/usr/bin/env python3
"""
Twitter/X MCP Integration - Posts to X/Twitter using API v2
"""

import os
import sys
import json
import requests
from requests_oauthlib import OAuth1
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class TwitterPoster:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.vault_path = Path(os.getenv('VAULT_PATH', self.base_dir / 'AI_Employee_Vault'))
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'

        # Twitter OAuth 1.0a credentials (required for posting)
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            print("[WARNING] Twitter OAuth 1.0a credentials not complete in .env")
            print("[INFO] Running in simulation mode")
            self.simulation_mode = True
        else:
            print("[INFO] Twitter OAuth 1.0a credentials loaded")
            print("[INFO] Running in LIVE mode - will post to Twitter!")
            self.simulation_mode = False

            # Create OAuth1 auth object
            self.auth = OAuth1(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )

    def read_post_content(self, file_path):
        """Extract post content from markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract content between frontmatter and approval instructions
            lines = content.split('\n')
            post_lines = []
            in_frontmatter = False
            in_content = False

            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        in_frontmatter = False
                        in_content = True
                        continue

                if in_frontmatter:
                    continue

                if in_content:
                    # Stop at approval instructions
                    if '## Approval Instructions' in line:
                        break

                    # Skip headers
                    if line.startswith('#'):
                        continue

                    # Collect content
                    if line.strip():
                        post_lines.append(line.strip())

            # Join and clean
            post_content = '\n\n'.join(post_lines)
            return post_content.strip()

        except Exception as e:
            print(f"[ERROR] Failed to read post: {e}")
            return None

    def post_to_twitter(self, content):
        """Post content to Twitter/X using API v2"""
        if self.simulation_mode:
            print("[SIMULATION] Would post to Twitter:")
            print(f"Content: {content}")
            print(f"Character count: {len(content)}")

            # Simulate success
            return {
                'success': True,
                'post_id': 'simulated_' + str(int(datetime.now().timestamp())),
                'url': 'https://twitter.com/user/status/simulated',
                'simulation': True
            }

        # Real Twitter API v2 posting with OAuth 1.0a
        url = "https://api.twitter.com/2/tweets"

        payload = {
            'text': content
        }

        try:
            response = requests.post(url, auth=self.auth, json=payload)

            if response.status_code == 201:
                data = response.json()
                tweet_id = data['data']['id']
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

                print(f"[SUCCESS] Posted to Twitter!")
                print(f"[INFO] Tweet ID: {tweet_id}")
                print(f"[INFO] URL: {tweet_url}")

                return {
                    'success': True,
                    'post_id': tweet_id,
                    'url': tweet_url,
                    'simulation': False
                }
            else:
                print(f"[ERROR] Twitter API error: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }

        except Exception as e:
            print(f"[ERROR] Failed to post to Twitter: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_dashboard(self, filename, post_id, post_url):
        """Update Dashboard with Twitter post"""
        dashboard_file = self.vault_path / 'Dashboard.md'

        try:
            if dashboard_file.exists():
                content = dashboard_file.read_text(encoding='utf-8')
            else:
                content = "# AI Employee Dashboard\n\n## Recent Activity\n\n"

            # Add new entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_entry = f"- [{timestamp}] Posted to X/Twitter: {filename} (Post ID: {post_id}, URL: {post_url})\n"

            # Insert after "Recent Activity" header
            if "## Recent Activity" in content:
                parts = content.split("## Recent Activity")
                content = parts[0] + "## Recent Activity\n\n" + new_entry + parts[1].lstrip('\n')
            else:
                content += f"\n## Recent Activity\n\n{new_entry}"

            dashboard_file.write_text(content, encoding='utf-8')
            print(f"[DASHBOARD] Updated with Twitter post")

        except Exception as e:
            print(f"[WARNING] Could not update dashboard: {e}")

    def log_action(self, filename, status, post_id=None, error=None):
        """Log Twitter posting action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'twitter_post',
            'filename': filename,
            'status': status,
            'post_id': post_id,
            'error': error
        }

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_twitter.json'

        # Read existing logs
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def process_approved_posts(self):
        """Process all approved Twitter posts"""
        # Look for X/Twitter posts in Approved folder
        x_posts = list(self.approved_dir.glob("X_POST_*.md"))

        if not x_posts:
            print("[INFO] No approved X/Twitter posts found")
            return

        print(f"[INFO] Found {len(x_posts)} approved X post(s)")

        for post_file in x_posts:
            print(f"\n[PROCESS] Processing: {post_file.name}")

            # Read post content
            content = self.read_post_content(post_file)
            if not content:
                print(f"[ERROR] Could not read post content")
                continue

            print(f"[CONTENT] Preview: {content[:100].encode('ascii', 'ignore').decode('ascii')}...")
            print(f"[CONTENT] Character count: {len(content)}")

            # Post to Twitter
            result = self.post_to_twitter(content)

            if result['success']:
                print(f"[SUCCESS] Posted to Twitter!")

                # Move to Done
                done_file = self.done_dir / post_file.name
                post_file.rename(done_file)
                print(f"[DONE] Moved to: {done_file.name}")

                # Update dashboard
                self.update_dashboard(
                    post_file.name,
                    result['post_id'],
                    result.get('url', 'N/A')
                )

                # Log action
                self.log_action(
                    post_file.name,
                    'success',
                    post_id=result['post_id']
                )

                if result.get('simulation'):
                    print("[INFO] This was a simulation - no real post created")
                else:
                    print(f"[INFO] Live post URL: {result['url']}")
            else:
                print(f"[ERROR] Failed to post to Twitter")
                self.log_action(
                    post_file.name,
                    'failed',
                    error=result.get('error')
                )

    def run(self):
        """Main execution"""
        print("\n" + "="*70)
        print(" "*20 + "Twitter/X Poster")
        print("="*70)
        print()

        if self.simulation_mode:
            print("[INFO] Running in SIMULATION mode (no Bearer Token)")
            print("[INFO] Posts will be logged but not actually sent")
        else:
            print("[INFO] Running in LIVE mode")
            print("[INFO] Posts will be sent to Twitter/X")

        print()

        self.process_approved_posts()

        print("\n[COMPLETE] Twitter posting session complete!")


if __name__ == "__main__":
    poster = TwitterPoster()
    poster.run()

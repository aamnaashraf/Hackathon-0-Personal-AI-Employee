#!/usr/bin/env python3
"""
Done Folder Email Sender - Watches Done folder and sends emails automatically
When user moves approved email drafts to Done folder, this script sends them via SMTP
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from email_mcp import EmailMCP


class DoneFolderEmailHandler(FileSystemEventHandler):
    """Handles email sending when files are moved to Done folder"""

    def __init__(self, email_mcp):
        self.email_mcp = email_mcp
        self.processed_files = set()

    def on_created(self, event):
        """Triggered when a file is created/moved to Done folder"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's an email draft file
        if not self.is_email_draft(file_path):
            return

        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return

        print(f"\n{'='*70}")
        print(f"[NEW FILE] {file_path.name}")
        print(f"[ACTION] Sending email automatically...")
        print(f"{'='*70}\n")

        # Wait a moment for file to be fully written
        time.sleep(0.5)

        # Process the email
        self.send_email_from_draft(file_path)

        # Mark as processed
        self.processed_files.add(str(file_path))

    def is_email_draft(self, file_path):
        """Check if file is an email draft"""
        filename = file_path.name.upper()
        return (
            filename.startswith('REPLY_DRAFT_') or
            filename.startswith('REPLY_APPROVED_') or
            filename.startswith('EMAIL_DRAFT_')
        ) and filename.endswith('.MD')

    def send_email_from_draft(self, file_path):
        """Extract email details from draft and send"""
        try:
            # Read the draft file
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata from frontmatter
            to_email = self.extract_field(content, 'reply_to')
            if not to_email or 'no-reply' in to_email.lower():
                print(f"[SKIP] No-reply address detected: {to_email}")
                print(f"[INFO] File kept in Done folder for record-keeping")
                return

            # Extract subject
            subject = self.extract_field(content, 'original_subject')
            if subject:
                subject = subject.strip('"').strip("'")
                subject = f"Re: {subject}"
            else:
                subject = "Re: Your inquiry"

            # Extract email body
            email_body = self.extract_email_body(content)

            if not email_body:
                print(f"[ERROR] Could not extract email body from {file_path.name}")
                return

            print(f"[TO] {to_email}")
            print(f"[SUBJECT] {subject}")
            print(f"[BODY] {email_body[:100]}...")

            # Send email
            success, log = self.email_mcp.send_email(
                to_email=to_email,
                subject=subject,
                body=email_body
            )

            if success:
                print(f"[SUCCESS] Email sent to {to_email}")
                self.log_action(file_path.name, to_email, subject, "sent")
            else:
                print(f"[ERROR] Failed to send email: {log.get('error', 'Unknown error')}")
                self.log_action(file_path.name, to_email, subject, "failed", log.get('error'))

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}")
            self.log_action(file_path.name, "unknown", "unknown", "error", str(e))

    def extract_field(self, content, field_name):
        """Extract a field from YAML frontmatter"""
        for line in content.split('\n'):
            if line.startswith(f'{field_name}:'):
                value = line.split(':', 1)[1].strip()
                return value.strip('"').strip("'")
        return None

    def extract_email_body(self, content):
        """Extract email body from markdown content"""
        lines = content.split('\n')
        body_lines = []
        capturing = False

        for line in lines:
            # Start capturing at "Dear" or first line after "## Draft Reply"
            if line.startswith('Dear') or (capturing and line.strip() and not line.startswith('#') and not line.startswith('**')):
                capturing = True

            if capturing:
                # Stop at approval instructions or end markers
                if '## Approval Instructions' in line or line.startswith('---') and len(body_lines) > 0:
                    break

                # Skip markdown headers and metadata lines
                if line.startswith('##') or line.startswith('**To**:') or line.startswith('**Subject**:'):
                    continue

                body_lines.append(line)

        return '\n'.join(body_lines).strip()

    def log_action(self, filename, to_email, subject, status, error=None):
        """Log email sending actions"""
        vault_path = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
        logs_dir = vault_path / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f'{today}_email_sender.log'

        log_entry = f"[{datetime.now().isoformat()}] {filename} | To: {to_email} | Subject: {subject} | Status: {status}"
        if error:
            log_entry += f" | Error: {error}"
        log_entry += "\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def main():
    """Main function to start the Done folder watcher"""
    print("\n" + "="*70)
    print(" " * 20 + "Done Folder Email Sender")
    print("="*70)
    print("\nWatching Done folder for email drafts...")
    print("When you move approved emails to Done, they will be sent automatically")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")

    # Setup email MCP
    config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': os.getenv('GMAIL_USERNAME'),
        'password': os.getenv('GMAIL_PASSWORD')
    }

    if not config['username'] or not config['password']:
        print("[ERROR] Gmail credentials not found in .env file")
        print("Please set GMAIL_USERNAME and GMAIL_PASSWORD")
        sys.exit(1)

    print(f"[CONFIG] Using email: {config['username']}")

    email_mcp = EmailMCP(config)

    # Setup file watcher
    vault_path = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
    done_dir = vault_path / 'Done'
    done_dir.mkdir(parents=True, exist_ok=True)

    print(f"[WATCHING] {done_dir}\n")

    event_handler = DoneFolderEmailHandler(email_mcp)
    observer = Observer()
    observer.schedule(event_handler, str(done_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[STOPPING] Shutting down email sender...")
        observer.stop()

    observer.join()
    print("[STOPPED] Email sender stopped")


if __name__ == "__main__":
    main()

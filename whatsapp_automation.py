#!/usr/bin/env python3
"""
WhatsApp Automation Master - Orchestrates the complete WhatsApp workflow
"""

import os
import sys
import time
import subprocess
from pathlib import Path


class WhatsAppAutomation:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.watcher_script = self.base_dir / "whatsapp_watcher.py"
        self.assistant_script = self.base_dir / "whatsapp_assistant.py"
        self.sender_script = self.base_dir / "whatsapp_sender.py"

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print(" " * 15 + "WhatsApp Automation System")
        print("="*70)
        print("\nWorkflow:")
        print("  1. Watcher   → Monitors WhatsApp for unread messages")
        print("  2. Assistant → Drafts replies for incoming messages")
        print("  3. Sender    → Sends approved replies back to WhatsApp")
        print("\nDirectories:")
        print("  • AI_Employee_Vault/Needs_Action      → Incoming messages (from Watcher)")
        print("  • AI_Employee_Vault/Pending_Approval  → Drafted replies (from Assistant)")
        print("  • AI_Employee_Vault/Approved          → Approved replies ready to send")
        print("  • AI_Employee_Vault/Done              → Sent messages (from Sender)")
        print("="*70 + "\n")

    def print_menu(self):
        """Print main menu"""
        print("\nSelect an option:")
        print("  1. Run Watcher (Monitor WhatsApp for new messages)")
        print("  2. Run Assistant (Draft replies for messages)")
        print("  3. Run Sender - DRY RUN (Test sending without actually sending)")
        print("  4. Run Sender - LIVE MODE (Actually send messages)")
        print("  5. Run Full Workflow (Watcher → Assistant → Sender DRY RUN)")
        print("  6. Check Status (View pending messages and replies)")
        print("  7. Exit")
        print()

    def check_status(self):
        """Check status of all directories"""
        print("\n" + "="*70)
        print("System Status")
        print("="*70)

        dirs = {
            "AI_Employee_Vault/Needs_Action": "Messages waiting for reply drafts",
            "AI_Employee_Vault/Pending_Approval": "Drafted replies waiting for approval",
            "AI_Employee_Vault/Approved": "Approved replies ready to send",
            "AI_Employee_Vault/Done": "Sent messages"
        }

        for dir_name, description in dirs.items():
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                whatsapp_files = list(dir_path.glob("WHATSAPP*.md"))
                count = len(whatsapp_files)
                print(f"\n{dir_name}:")
                print(f"  {description}")
                print(f"  Files: {count}")
                if count > 0 and count <= 5:
                    for f in whatsapp_files:
                        print(f"    - {f.name}")
                elif count > 5:
                    for f in whatsapp_files[:3]:
                        print(f"    - {f.name}")
                    print(f"    ... and {count - 3} more")
            else:
                print(f"\n{dir_name}:")
                print(f"  {description}")
                print(f"  Directory does not exist yet")

        print("\n" + "="*70)

    def run_watcher(self):
        """Run the WhatsApp watcher"""
        print("\n" + "="*70)
        print("Starting WhatsApp Watcher...")
        print("Press Ctrl+C to stop")
        print("="*70 + "\n")

        try:
            subprocess.run([sys.executable, str(self.watcher_script)])
        except KeyboardInterrupt:
            print("\n\nWatcher stopped by user")
        except Exception as e:
            print(f"\n✗ Error running watcher: {e}")

    def run_assistant(self):
        """Run the reply assistant"""
        print("\n" + "="*70)
        print("Starting Reply Assistant...")
        print("="*70 + "\n")

        try:
            subprocess.run([sys.executable, str(self.assistant_script)])
        except Exception as e:
            print(f"\n✗ Error running assistant: {e}")

        input("\nPress Enter to continue...")

    def run_sender(self, dry_run=True):
        """Run the message sender"""
        mode = "DRY RUN" if dry_run else "LIVE MODE"
        print("\n" + "="*70)
        print(f"Starting Message Sender - {mode}")
        if not dry_run:
            print("\n⚠️  WARNING: This will ACTUALLY SEND messages to WhatsApp!")
            confirm = input("Type 'YES' to confirm: ")
            if confirm != "YES":
                print("Cancelled.")
                input("\nPress Enter to continue...")
                return
        print("="*70 + "\n")

        try:
            # Modify the sender script to use the dry_run parameter
            env = os.environ.copy()
            env['WHATSAPP_DRY_RUN'] = 'true' if dry_run else 'false'
            subprocess.run([sys.executable, str(self.sender_script)], env=env)
        except Exception as e:
            print(f"\n✗ Error running sender: {e}")

        input("\nPress Enter to continue...")

    def run_full_workflow(self):
        """Run the complete workflow"""
        print("\n" + "="*70)
        print("Running Full Workflow")
        print("="*70)

        # Step 1: Check for messages
        print("\n[Step 1/3] Checking for new messages...")
        needs_action = self.base_dir / "AI_Employee_Vault" / "Needs_Action"
        if needs_action.exists():
            message_count = len(list(needs_action.glob("WHATSAPP_*.md")))
            print(f"Found {message_count} message(s) in Needs_Action")
        else:
            print("No messages found. Run the Watcher first.")
            input("\nPress Enter to continue...")
            return

        # Step 2: Draft replies
        print("\n[Step 2/3] Drafting replies...")
        self.run_assistant()

        # Step 3: Show pending approvals
        print("\n[Step 3/3] Checking drafted replies...")
        pending = self.base_dir / "AI_Employee_Vault" / "Pending_Approval"
        if pending.exists():
            reply_count = len(list(pending.glob("WHATSAPP_REPLY_*.md")))
            print(f"\n✓ {reply_count} reply(ies) drafted and waiting in Pending_Approval")
            print("\nNext steps:")
            print("  1. Review the drafted replies in Pending_Approval/")
            print("  2. Move approved replies to Approved/")
            print("  3. Run Sender to send the approved messages")
        else:
            print("No replies were drafted.")

        input("\nPress Enter to continue...")

    def run(self):
        """Main run loop"""
        self.print_banner()

        while True:
            self.print_menu()

            try:
                choice = input("Enter your choice (1-7): ").strip()

                if choice == "1":
                    self.run_watcher()
                elif choice == "2":
                    self.run_assistant()
                elif choice == "3":
                    self.run_sender(dry_run=True)
                elif choice == "4":
                    self.run_sender(dry_run=False)
                elif choice == "5":
                    self.run_full_workflow()
                elif choice == "6":
                    self.check_status()
                    input("\nPress Enter to continue...")
                elif choice == "7":
                    print("\nGoodbye!")
                    break
                else:
                    print("\n✗ Invalid choice. Please enter 1-7.")
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")
                time.sleep(2)


if __name__ == "__main__":
    automation = WhatsAppAutomation()
    automation.run()
#!/usr/bin/env python3
"""
WhatsApp Reply Assistant - Drafts replies for incoming WhatsApp messages
"""

import os
import re
from datetime import datetime
from pathlib import Path


class WhatsAppReplyAssistant:
    def __init__(
        self,
        needs_action_dir="AI_Employee_Vault/Needs_Action",
        pending_approval_dir="AI_Employee_Vault/Pending_Approval"
    ):
        self.needs_action_dir = Path(needs_action_dir).resolve()
        self.pending_approval_dir = Path(pending_approval_dir).resolve()

        # Create directories if they don't exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

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

            # Extract message text
            message_match = re.search(r'Message:\s*\n(.+)', body, re.DOTALL)
            if message_match:
                message_text = message_match.group(1).strip()
            else:
                message_text = body

            return {
                'chat_name': metadata.get('chat_name', ''),
                'chat_id': metadata.get('chat_id', ''),
                'message_text': message_text,
                'metadata': metadata
            }

        except Exception as e:
            print(f"✗ Error parsing file {filepath}: {e}")
            return None

    def _draft_reply(self, chat_name, message_text):
        """Draft a reply based on the message content"""
        message_lower = message_text.lower()

        # Greeting patterns
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return f"Hello! Thank you for reaching out. How can I assist you today?"

        # Question patterns
        if '?' in message_text:
            return f"Thank you for your question. I'll look into this and get back to you shortly."

        # Request patterns
        if any(word in message_lower for word in ['please', 'can you', 'could you', 'would you', 'need', 'want']):
            return f"Thank you for your request. I'll review this and respond as soon as possible."

        # Urgent patterns
        if any(word in message_lower for word in ['urgent', 'asap', 'immediately', 'emergency']):
            return f"I understand this is urgent. I'm looking into it now and will respond shortly."

        # Thank you patterns
        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return f"You're welcome! Let me know if you need anything else."

        # Payment/Invoice patterns
        if any(word in message_lower for word in ['payment', 'invoice', 'bill', 'paid', 'pay']):
            return f"Thank you for your message regarding payment. I'll check the details and get back to you soon."

        # Meeting/Schedule patterns
        if any(word in message_lower for word in ['meeting', 'schedule', 'appointment', 'call', 'discuss']):
            return f"Thank you for reaching out. I'd be happy to schedule a time to discuss this. What time works best for you?"

        # Price/Quote patterns
        if any(word in message_lower for word in ['price', 'cost', 'quote', 'how much']):
            return f"Thank you for your interest. I'll prepare the pricing information and send it to you shortly."

        # Help patterns
        if any(word in message_lower for word in ['help', 'support', 'issue', 'problem']):
            return f"I'm here to help. Could you please provide more details about the issue so I can assist you better?"

        # Default response
        return f"Thank you for your message. I've received it and will respond shortly."

    def _create_reply_file(self, original_file, chat_name, chat_id, reply_text):
        """Create a reply file in Pending_Approval"""
        try:
            # Extract the unique ID from the original filename
            # Format: WHATSAPP_<unique_id>.md
            match = re.match(r'WHATSAPP_(.+)\.md', original_file.name)
            if match:
                unique_id = match.group(1)
            else:
                unique_id = datetime.now().strftime('%Y%m%d%H%M%S')

            filename = f"WHATSAPP_REPLY_{unique_id}.md"
            filepath = self.pending_approval_dir / filename

            content = f"""---
type: whatsapp_reply
chat_name: {chat_name}
chat_id: {chat_id}
status: pending_approval
---

Reply:
{reply_text}
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Created reply: {filename}")
            return True

        except Exception as e:
            print(f"✗ Error creating reply file: {e}")
            return False

    def process_messages(self):
        """Process all WhatsApp messages in Needs_Action"""
        print("=" * 60)
        print("WhatsApp Reply Assistant")
        print("=" * 60)
        print(f"Needs Action directory: {self.needs_action_dir}")
        print(f"Pending Approval directory: {self.pending_approval_dir}")
        print("=" * 60)

        # Find all WHATSAPP_*.md files
        message_files = sorted(self.needs_action_dir.glob("WHATSAPP_*.md"))

        # Exclude reply files
        message_files = [f for f in message_files if not f.name.startswith("WHATSAPP_REPLY_")]

        if not message_files:
            print("\n✓ No messages to process in Needs_Action folder")
            return

        print(f"\nFound {len(message_files)} message(s) to process\n")

        processed_count = 0
        failed_count = 0

        for filepath in message_files:
            print(f"\n{'='*60}")
            print(f"Processing: {filepath.name}")
            print(f"{'='*60}")

            # Parse file
            data = self._parse_markdown_file(filepath)
            if not data:
                print(f"✗ Failed to parse file: {filepath.name}")
                failed_count += 1
                continue

            chat_name = data['chat_name']
            chat_id = data['chat_id']
            message_text = data['message_text']

            print(f"From: {chat_name}")
            print(f"Message: {message_text[:100]}..." if len(message_text) > 100 else f"Message: {message_text}")

            # Draft reply
            reply_text = self._draft_reply(chat_name, message_text)
            print(f"\nDrafted reply: {reply_text}")

            # Create reply file
            if self._create_reply_file(filepath, chat_name, chat_id, reply_text):
                processed_count += 1
                print(f"✓ Reply drafted for: {chat_name}")
            else:
                failed_count += 1
                print(f"✗ Failed to draft reply for: {chat_name}")

        print("\n" + "="*60)
        print(f"Processing complete: {processed_count} succeeded, {failed_count} failed")
        print("="*60)


if __name__ == "__main__":
    assistant = WhatsAppReplyAssistant(
        needs_action_dir="AI_Employee_Vault/Needs_Action",
        pending_approval_dir="AI_Employee_Vault/Pending_Approval"
    )

    assistant.process_messages()
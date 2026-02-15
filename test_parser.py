#!/usr/bin/env python3
"""Test the WhatsApp parser fix"""
import re
from pathlib import Path

def parse_markdown_file(filepath):
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
        print(f"Error: {e}")
        return None

# Test the parser
result = parse_markdown_file('test_whatsapp_parse.md')
if result:
    print("="*60)
    print("PARSER TEST RESULT")
    print("="*60)
    print(f"Chat Name: {result['chat_name']}")
    print(f"Chat ID: {result['chat_id']}")
    print(f"\nExtracted Reply Text:")
    print("-"*60)
    print(result['reply_text'])
    print("-"*60)
    print(f"\nLength: {len(result['reply_text'])} characters")
    print("\n✓ Parser working correctly!")
else:
    print("✗ Parser failed")

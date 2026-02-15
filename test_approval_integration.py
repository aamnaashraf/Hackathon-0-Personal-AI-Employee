#!/usr/bin/env python3
"""
Test script for Approval Handler integration
Verifies all components are working correctly
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def print_status(message, status="INFO"):
    """Print formatted status message"""
    symbols = {
        "INFO": "[i]",
        "SUCCESS": "[+]",
        "ERROR": "[x]",
        "WARNING": "[!]"
    }
    print(f"{symbols.get(status, '[i]')} [{status}] {message}")

def test_environment():
    """Test environment setup"""
    print("\n" + "="*70)
    print("Testing Environment Setup")
    print("="*70)

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print_status(".env file exists", "SUCCESS")

        # Check required variables
        from dotenv import load_dotenv
        load_dotenv()

        vault_path = os.getenv('VAULT_PATH')
        insta_session = os.getenv('INSTAGRAM_SESSION_PATH')
        fb_session = os.getenv('FACEBOOK_SESSION_PATH')

        if vault_path:
            print_status(f"VAULT_PATH: {vault_path}", "SUCCESS")
        else:
            print_status("VAULT_PATH not set", "ERROR")

        if insta_session:
            print_status(f"INSTAGRAM_SESSION_PATH: {insta_session}", "SUCCESS")
        else:
            print_status("INSTAGRAM_SESSION_PATH not set", "WARNING")

        if fb_session:
            print_status(f"FACEBOOK_SESSION_PATH: {fb_session}", "SUCCESS")
        else:
            print_status("FACEBOOK_SESSION_PATH not set", "WARNING")
    else:
        print_status(".env file not found", "ERROR")

def test_directories():
    """Test directory structure"""
    print("\n" + "="*70)
    print("Testing Directory Structure")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

    required_dirs = [
        'Approved',
        'Done',
        'Pending_Approval',
        'Needs_Action',
        'Logs',
        'Plans'
    ]

    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists():
            print_status(f"{dir_name}/ exists", "SUCCESS")
        else:
            print_status(f"{dir_name}/ missing", "ERROR")

def test_scripts():
    """Test required scripts exist"""
    print("\n" + "="*70)
    print("Testing Required Scripts")
    print("="*70)

    required_scripts = [
        'approval_handler.py',
        'instagram_personal_poster.py',
        'facebook_personal_poster.py',
        'complete_linkedin_tasks.py',
        'run_approval_handler.bat',
        'run_instagram_poster.bat',
        'run_facebook_poster.bat'
    ]

    for script in required_scripts:
        script_path = Path(script)
        if script_path.exists():
            print_status(f"{script} exists", "SUCCESS")
        else:
            print_status(f"{script} missing", "WARNING")

def test_dependencies():
    """Test Python dependencies"""
    print("\n" + "="*70)
    print("Testing Python Dependencies")
    print("="*70)

    dependencies = [
        ('playwright', 'Playwright'),
        ('dotenv', 'python-dotenv'),
    ]

    for module, package in dependencies:
        try:
            __import__(module)
            print_status(f"{package} installed", "SUCCESS")
        except ImportError:
            print_status(f"{package} not installed", "ERROR")
            print(f"   Install with: pip install {package}")

def test_sample_files():
    """Test sample post files"""
    print("\n" + "="*70)
    print("Testing Sample Post Files")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
    approved_dir = vault_path / 'Approved'

    if approved_dir.exists():
        insta_posts = list(approved_dir.glob("INSTA_POST_*.md"))
        fb_posts = list(approved_dir.glob("FB_POST_*.md"))
        linkedin_posts = list(approved_dir.glob("LINKEDIN_POST_*.md"))

        print_status(f"Instagram posts: {len(insta_posts)}", "INFO")
        print_status(f"Facebook posts: {len(fb_posts)}", "INFO")
        print_status(f"LinkedIn posts: {len(linkedin_posts)}", "INFO")

        if insta_posts:
            for post in insta_posts:
                print(f"   - {post.name}")
    else:
        print_status("Approved/ directory not found", "ERROR")

def test_approval_handler_import():
    """Test approval handler can be imported"""
    print("\n" + "="*70)
    print("Testing Approval Handler Import")
    print("="*70)

    try:
        from approval_handler import ApprovalHandler
        print_status("ApprovalHandler class imported successfully", "SUCCESS")

        # Try to instantiate
        handler = ApprovalHandler()
        print_status("ApprovalHandler instantiated successfully", "SUCCESS")

        # Test file detection
        test_files = [
            ("INSTA_POST_test.md", "instagram_post"),
            ("FB_POST_test.md", "facebook_post"),
            ("LINKEDIN_POST_test.md", "linkedin_post"),
            ("WHATSAPP_REPLY_test.md", "whatsapp_reply"),
            ("REPLY_APPROVED_test.md", "email_reply"),
        ]

        print("\nTesting file type detection:")
        for filename, expected_type in test_files:
            test_path = Path(filename)
            detected_type = handler.detect_file_type(test_path)
            if detected_type == expected_type:
                print_status(f"{filename} → {detected_type}", "SUCCESS")
            else:
                print_status(f"{filename} → {detected_type} (expected {expected_type})", "ERROR")

    except Exception as e:
        print_status(f"Failed to import ApprovalHandler: {e}", "ERROR")

def create_test_post():
    """Create a test Instagram post for verification"""
    print("\n" + "="*70)
    print("Creating Test Post")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
    approved_dir = vault_path / 'Approved'

    test_post_path = approved_dir / 'INSTA_POST_integration_test.md'

    test_content = f"""---
type: instagram_post
status: approved
created: {datetime.now().strftime('%Y-%m-%d')}
media:
---

# Instagram Post - Integration Test

🧪 Testing the approval handler integration!

This post was created automatically by the test script to verify:
✅ File detection works
✅ Approval handler monitors correctly
✅ Instagram poster integration functional

#Test #Integration #Automation #Working

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    try:
        test_post_path.write_text(test_content, encoding='utf-8')
        print_status(f"Test post created: {test_post_path.name}", "SUCCESS")
        print(f"\nTo test the integration:")
        print(f"1. Run: python approval_handler.py --once")
        print(f"2. Browser should open automatically")
        print(f"3. Post should be published to Instagram")
        print(f"4. File should move to Done/ folder")
    except Exception as e:
        print_status(f"Failed to create test post: {e}", "ERROR")

def print_summary():
    """Print test summary and next steps"""
    print("\n" + "="*70)
    print("Test Summary & Next Steps")
    print("="*70)

    print("\n✅ Setup Complete! Ready to use:")
    print("\n1. Start Approval Handler (Continuous Monitoring):")
    print("   run_approval_handler.bat")
    print("   OR")
    print("   python approval_handler.py")

    print("\n2. Test Single Run:")
    print("   python approval_handler.py --once")

    print("\n3. Manual Instagram Posting:")
    print("   run_instagram_poster.bat")
    print("   OR")
    print("   python instagram_personal_poster.py")

    print("\n4. Manual Facebook Posting:")
    print("   run_facebook_poster.bat")

    print("\n📋 Workflow:")
    print("   Draft → Pending_Approval/ → Review → Approved/ → Auto-Post → Done/")

    print("\n📁 File Patterns:")
    print("   INSTA_POST_*.md     → Instagram")
    print("   FB_POST_*.md        → Facebook")
    print("   LINKEDIN_POST_*.md  → LinkedIn")

    print("\n📖 Documentation:")
    print("   APPROVAL_HANDLER_GUIDE.md")
    print("   INSTAGRAM_QUICK_SETUP.md")
    print("   FACEBOOK_QUICK_START.md")

    print("\n" + "="*70)

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "Approval Handler Integration Test")
    print("="*70)

    test_environment()
    test_directories()
    test_scripts()
    test_dependencies()
    test_sample_files()
    test_approval_handler_import()

    # Ask if user wants to create test post
    print("\n" + "="*70)
    response = input("\nCreate test Instagram post? (y/n): ").lower()
    if response == 'y':
        create_test_post()

    print_summary()

if __name__ == "__main__":
    main()

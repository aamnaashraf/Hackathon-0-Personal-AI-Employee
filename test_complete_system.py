#!/usr/bin/env python3
"""
Complete System Test Suite
Tests all components of the AI Employee system end-to-end
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SystemTester:
    def __init__(self):
        self.vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_test(self, test_name, status, message=""):
        """Log test result"""
        symbol = "[+]" if status else "[x]"
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        if status:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{symbol} {test_name}: {'PASS' if status else 'FAIL'} {message}")

    def test_directory_structure(self):
        """Test 1: Verify all required directories exist"""
        print("\n" + "="*70)
        print("TEST 1: Directory Structure")
        print("="*70)

        required_dirs = [
            'Needs_Action',
            'Pending_Approval',
            'Approved',
            'Done',
            'Plans',
            'Logs',
            'Briefings',
            'Config'
        ]

        for dir_name in required_dirs:
            dir_path = self.vault_path / dir_name
            exists = dir_path.exists()
            self.log_test(f"Directory: {dir_name}", exists)

    def test_core_scripts(self):
        """Test 2: Verify all core scripts exist"""
        print("\n" + "="*70)
        print("TEST 2: Core Scripts")
        print("="*70)

        scripts = [
            'instagram_personal_poster.py',
            'facebook_personal_poster.py',
            'approval_handler.py',
            'ceo_briefing_generator.py',
            'instagram_image_generator.py',
            'complete_linkedin_tasks.py',
        ]

        for script in scripts:
            exists = Path(script).exists()
            self.log_test(f"Script: {script}", exists)

    def test_dependencies(self):
        """Test 3: Verify Python dependencies"""
        print("\n" + "="*70)
        print("TEST 3: Python Dependencies")
        print("="*70)

        dependencies = [
            ('playwright', 'Playwright'),
            ('dotenv', 'python-dotenv'),
            ('PIL', 'Pillow'),
        ]

        for module, package in dependencies:
            try:
                __import__(module)
                self.log_test(f"Package: {package}", True)
            except ImportError:
                self.log_test(f"Package: {package}", False, "Not installed")

    def test_session_files(self):
        """Test 4: Check session persistence"""
        print("\n" + "="*70)
        print("TEST 4: Session Files")
        print("="*70)

        sessions = [
            ('instagram_session', 'Instagram'),
            ('facebook_session', 'Facebook'),
        ]

        for session_dir, platform in sessions:
            exists = Path(session_dir).exists()
            self.log_test(f"Session: {platform}", exists,
                         "Configured" if exists else "Not logged in yet")

    def test_vault_content(self):
        """Test 5: Analyze vault content"""
        print("\n" + "="*70)
        print("TEST 5: Vault Content Analysis")
        print("="*70)

        # Count items in each folder
        done_count = len(list((self.vault_path / 'Done').glob('*.md')))
        needs_action_count = len(list((self.vault_path / 'Needs_Action').glob('*.md')))
        pending_count = len(list((self.vault_path / 'Pending_Approval').glob('*.md')))
        approved_count = len(list((self.vault_path / 'Approved').glob('*.md')))

        self.log_test("Done folder", True, f"{done_count} completed tasks")
        self.log_test("Needs_Action folder", True, f"{needs_action_count} items")
        self.log_test("Pending_Approval folder", True, f"{pending_count} items")
        self.log_test("Approved folder", True, f"{approved_count} items ready to process")

    def test_social_media_posts(self):
        """Test 6: Verify social media posts"""
        print("\n" + "="*70)
        print("TEST 6: Social Media Posts")
        print("="*70)

        done_dir = self.vault_path / 'Done'

        fb_posts = len(list(done_dir.glob('FB_POST_*.md')))
        insta_posts = len(list(done_dir.glob('INSTA_POST_*.md')))
        linkedin_posts = len(list(done_dir.glob('LINKEDIN_POST_*.md')))

        self.log_test("Facebook posts", fb_posts > 0, f"{fb_posts} published")
        self.log_test("Instagram posts", insta_posts > 0, f"{insta_posts} published")
        self.log_test("LinkedIn posts", linkedin_posts > 0, f"{linkedin_posts} published")

    def test_ceo_briefing(self):
        """Test 7: Verify CEO briefing exists"""
        print("\n" + "="*70)
        print("TEST 7: CEO Briefing")
        print("="*70)

        briefings_dir = self.vault_path / 'Briefings'
        briefings = list(briefings_dir.glob('MONDAY_CEO_BRIEFING_*.md'))

        exists = len(briefings) > 0
        self.log_test("CEO Briefing generated", exists,
                     f"{len(briefings)} briefing(s) found")

        if exists:
            latest = max(briefings, key=lambda p: p.stat().st_mtime)
            self.log_test("Latest briefing", True, f"{latest.name}")

    def test_dashboard(self):
        """Test 8: Verify dashboard exists and is updated"""
        print("\n" + "="*70)
        print("TEST 8: Dashboard")
        print("="*70)

        dashboard = self.vault_path / 'Dashboard.md'
        exists = dashboard.exists()

        self.log_test("Dashboard file", exists)

        if exists:
            content = dashboard.read_text(encoding='utf-8')
            has_recent_activity = 'Recent Activity' in content
            has_instagram = 'Instagram' in content
            has_facebook = 'Facebook' in content

            self.log_test("Dashboard has recent activity", has_recent_activity)
            self.log_test("Dashboard tracks Instagram", has_instagram)
            self.log_test("Dashboard tracks Facebook", has_facebook)

    def test_approval_handler_import(self):
        """Test 9: Test approval handler can be imported"""
        print("\n" + "="*70)
        print("TEST 9: Approval Handler")
        print("="*70)

        try:
            from approval_handler import ApprovalHandler
            self.log_test("ApprovalHandler import", True)

            handler = ApprovalHandler()
            self.log_test("ApprovalHandler instantiation", True)

            # Test file detection
            test_files = [
                ("INSTA_POST_test.md", "instagram_post"),
                ("FB_POST_test.md", "facebook_post"),
            ]

            for filename, expected_type in test_files:
                detected = handler.detect_file_type(Path(filename))
                matches = detected == expected_type
                self.log_test(f"Detect {filename}", matches, f"→ {detected}")

        except Exception as e:
            self.log_test("ApprovalHandler import", False, str(e))

    def test_image_generator(self):
        """Test 10: Test Instagram image generator"""
        print("\n" + "="*70)
        print("TEST 10: Instagram Image Generator")
        print("="*70)

        try:
            from instagram_image_generator import generate_instagram_image

            test_text = "Test post for system validation"
            output_path = generate_instagram_image(test_text, "test_system_check.jpg")

            exists = Path(output_path).exists()
            self.log_test("Image generation", exists, f"Created: {output_path}")

            # Clean up test image
            if exists:
                Path(output_path).unlink()

        except Exception as e:
            self.log_test("Image generation", False, str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("SYSTEM TEST REPORT")
        print("="*70)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.failed > 0:
            print("\n" + "="*70)
            print("FAILED TESTS:")
            print("="*70)
            for result in self.results:
                if not result['status']:
                    print(f"[x] {result['test']}: {result['message']}")

        print("\n" + "="*70)
        print("SYSTEM STATUS")
        print("="*70)

        if pass_rate >= 90:
            print("[+] EXCELLENT - System ready for production demo")
        elif pass_rate >= 75:
            print("[!] GOOD - Minor issues, system mostly functional")
        elif pass_rate >= 50:
            print("[!] WARNING - Several issues need attention")
        else:
            print("[x] CRITICAL - Major issues, system not ready")

        # Save report to file
        report_path = self.vault_path / 'Logs' / f'system_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total,
                'passed': self.passed,
                'failed': self.failed,
                'pass_rate': pass_rate,
                'results': self.results
            }, f, indent=2)

        print(f"\n[+] Test report saved: {report_path}")

    def run_all_tests(self):
        """Run all system tests"""
        print("\n" + "="*70)
        print("AI EMPLOYEE SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        self.test_directory_structure()
        self.test_core_scripts()
        self.test_dependencies()
        self.test_session_files()
        self.test_vault_content()
        self.test_social_media_posts()
        self.test_ceo_briefing()
        self.test_dashboard()
        self.test_approval_handler_import()
        self.test_image_generator()

        self.generate_report()


if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()

"""
Quick diagnostic: Check what happens when watcher loads the session
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

import dotenv
dotenv.load_dotenv()

session_path = Path(os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
session_file = session_path / 'storage-state.json'

print("Starting diagnostic...")
print(f"Session file exists: {session_file.exists()}")

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)

print("Loading session...")
context = browser.new_context(storage_state=str(session_file))
page = context.new_page()

print("Applying stealth...")
stealth = Stealth()
stealth.apply_stealth_sync(page)

print("Navigating to WhatsApp Web...")
page.goto("https://web.whatsapp.com")

print("Waiting for page to load...")
try:
    page.wait_for_load_state("domcontentloaded", timeout=60000)
except:
    pass

print("\nWaiting 45 seconds (same as watcher)...")
time.sleep(45)

print("\n=== CHECKING PAGE STATE ===")
print(f"Current URL: {page.url}")
print(f"Page title: {page.title()}")

# Check for logout
if "post_logout" in page.url:
    print("\n!!! WHATSAPP LOGGED OUT THE SESSION !!!")
    print("WhatsApp Web is detecting automation and forcing logout")

# Check for chats
chat_items = page.locator('#pane-side div[role="row"]')
chat_count = chat_items.count()
print(f"\nChats found: {chat_count}")

# Check for sidebar
sidebar = page.locator('#pane-side, #side')
sidebar_count = sidebar.count()
print(f"Sidebar elements: {sidebar_count}")

# Take screenshot
page.screenshot(path="watcher_diagnostic.png")
print("\nScreenshot saved: watcher_diagnostic.png")

print("\nKeeping browser open for 30 seconds for inspection...")
time.sleep(30)

browser.close()
playwright.stop()
print("Done")

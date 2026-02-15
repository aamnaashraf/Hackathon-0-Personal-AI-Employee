from playwright.sync_api import sync_playwright
from pathlib import Path
import time

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR.resolve()),
        headless=False   # 👈 pehle false rakho
    )

    page = context.new_page()
    page.goto("https://web.whatsapp.com")
    time.sleep(15)

    if page.locator("text=Search").count() > 0 or page.locator("#pane-side").count() > 0:
        print("✅ WhatsApp authenticated (session reused)")
    else:
        print("❌ Still not authenticated")

    context.close()
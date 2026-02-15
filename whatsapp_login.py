from playwright.sync_api import sync_playwright
from pathlib import Path
import time

SESSION_DIR = Path(__file__).parent / "whatsapp_session"
SESSION_DIR.mkdir(exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR.resolve()),  # 🔑 ABSOLUTE PATH
        headless=False
    )

    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")

    print("📱 QR scan karo (phone se)")
    print("⏳ Login ke baad 30 seconds wait karein...")

    # VERY IMPORTANT: time do session ko disk pe save hone ka
    time.sleep(30)

    print("✅ Assuming login complete. Closing browser safely.")
    context.close()
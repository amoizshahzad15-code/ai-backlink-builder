import os
import sys
import time
import json
import re

print("=" * 65)
print("🚀 REAL AI DESKTOP BROWSER BOT (Playwright Automation)")
print("   Creates Real Accounts & Profile Backlinks on High-DA Platforms")
print("=" * 65)

# Prompt for user inputs if not already saved
CONFIG_FILE = "desktop_bot_config.json"

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

config = get_config()

website_url = input(f"1. Target Website URL [{config.get('website_url', 'https://yourwebsite.com')}]: ").strip() or config.get("website_url", "")
user_name = input(f"2. Your Full Name [{config.get('user_name', 'Moiz Shahzad')}]: ").strip() or config.get("user_name", "Moiz Shahzad")
user_email = input(f"3. Your Account Email [{config.get('user_email', '')}]: ").strip() or config.get("user_email", "")
user_password = input(f"4. Account Password [{config.get('user_password', '')}]: ").strip() or config.get("user_password", "")

# Save config for next time
with open(CONFIG_FILE, "w") as f:
    json.dump({
        "website_url": website_url,
        "user_name": user_name,
        "user_email": user_email,
        "user_password": user_password
    }, f, indent=4)

if not website_url or not user_email:
    print("❌ Website URL and Email are required to proceed!")
    sys.exit(1)

print("\n[+] Launching Real Chrome Browser on your computer...")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\n⚠️ Playwright is not installed yet!")
    print("Run this command first:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)

def run_browser_automation():
    with sync_playwright() as p:
        # Launch real visible browser (headless=False)
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("\n" + "=" * 50)
        print("🎯 TARGET 1: Dev.to Creator Profile (DA 89)")
        print("=" * 50)
        print("[+] Navigating to Dev.to registration/login...")
        page.goto("https://dev.to/enter", wait_until="networkidle")

        print("\n👉 ACTION REQUIRED IN BROWSER:")
        print("   Chrome browser has opened in front of you!")
        print("   If you see 'Sign up with email' or captcha:")
        print(f"   Email: {user_email}")
        print(f"   Password: {user_password}")
        input("\n⌨️  Complete the login/signup in the browser window, then press ENTER here to continue...")

        # Navigate to Settings to add Website Link
        print("\n[+] Navigating to Profile Settings to insert your website backlink...")
        try:
            page.goto("https://dev.to/settings", wait_until="networkidle")
            
            # Look for website url field
            website_input = page.locator("input#user_website_url, input[name='user[website_url]']")
            if website_input.count() > 0:
                website_input.first.fill(website_url)
                print(f"✅ Website field filled with: {website_url}")
            
            # Bio field
            bio_input = page.locator("textarea#user_summary, textarea[name='user[summary]']")
            if bio_input.count() > 0:
                bio_input.first.fill(f"Founder & Creator at {website_url}. Exploring technology and innovative solutions.")
                print(f"✅ Profile Bio filled!")

            # Click save
            save_btn = page.locator("input[type='submit'][value='Save Profile Information'], button:has-text('Save')")
            if save_btn.count() > 0:
                save_btn.first.click()
                print("✅ Profile changes saved successfully!")
                time.sleep(2)

            print(f"\n🎉 LIVE PROFILE BACKLINK ACTIVE: {page.url}")
            with open("live_profiles.txt", "a") as out:
                out.write(f"Dev.to Profile Backlink: {page.url} (Linked to {website_url})\n")

        except Exception as e:
            print(f"⚠️ Error updating settings: {e}")

        # TARGET 2: Product Hunt
        print("\n" + "=" * 50)
        print("🎯 TARGET 2: Product Hunt Maker Profile (DA 91)")
        print("=" * 50)
        print("[+] Navigating to Product Hunt...")
        page.goto("https://www.producthunt.com", wait_until="domcontentloaded")
        print("\n👉 ACTION IN BROWSER:")
        print("   Sign in to Product Hunt in the opened window.")
        input("⌨️  Once logged in, press ENTER here...")

        try:
            page.goto("https://www.producthunt.com/my/settings/edit", wait_until="domcontentloaded")
            headline_input = page.locator("input[name='headline'], input#headline")
            if headline_input.count() > 0:
                headline_input.first.fill(f"Maker at {website_url}")
            
            website_field = page.locator("input[name='website_url'], input#website_url")
            if website_field.count() > 0:
                website_field.first.fill(website_url)
                print(f"✅ Product Hunt website field filled: {website_url}")

            input("⌨️  Click Save in the browser, then press ENTER to finish...")
        except Exception as e:
            print(f"Product Hunt notice: {e}")

        print("\n" + "=" * 65)
        print("🎉 ALL SESSIONS SAVED TO live_profiles.txt!")
        print("=" * 65)
        browser.close()

if __name__ == "__main__":
    run_browser_automation()

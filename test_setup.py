"""
Run this file FIRST after setup to check everything works.
Command: python test_setup.py
"""

print("=" * 50)
print("Checking your setup...")
print("=" * 50)

errors = []

# 1. Check all imports
try:
    from playwright.sync_api import sync_playwright
    print("[OK] Playwright installed")
except ImportError:
    print("[FAIL] Playwright not installed — run: pip install playwright")
    errors.append("playwright")

try:
    import gspread
    print("[OK] gspread installed")
except ImportError:
    print("[FAIL] gspread not installed — run: pip install gspread")
    errors.append("gspread")

try:
    import sib_api_v3_sdk
    print("[OK] Brevo SDK installed")
except ImportError:
    print("[FAIL] Brevo SDK not installed — run: pip install sib-api-v3-sdk")
    errors.append("brevo")

try:
    import pandas
    print("[OK] pandas installed")
except ImportError:
    print("[FAIL] pandas not installed")
    errors.append("pandas")

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv installed")
except ImportError:
    print("[FAIL] python-dotenv not installed")
    errors.append("dotenv")

# 2. Check .env file exists
import os
if os.path.exists(".env"):
    print("[OK] .env file found")
else:
    print("[WARN] .env file not found — copy .env.example to .env and fill in your values")

# 3. Check credentials.json exists
if os.path.exists("credentials.json"):
    print("[OK] credentials.json found (Google Sheets)")
else:
    print("[WARN] credentials.json not found — needed for Google Sheets (Step 2)")

# 4. Check config loads
try:
    import config
    print("[OK] config.py loaded successfully")
except Exception as e:
    print(f"[FAIL] config.py error: {e}")
    errors.append("config")

# 5. Check folders exist
for folder in ["scraper", "emailer", "sheets", "utils", "data", "logs"]:
    if os.path.isdir(folder):
        print(f"[OK] /{folder} folder exists")
    else:
        os.makedirs(folder, exist_ok=True)
        print(f"[CREATED] /{folder} folder created")

print("=" * 50)
if errors:
    print(f"Issues found: {', '.join(errors)}")
    print("Fix the errors above then run this again.")
else:
    print("All good! Ready to move to Step 2.")
print("=" * 50)

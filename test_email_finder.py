"""
test_email_finder.py
Tests email finding on your existing leads WITHOUT modifying Sheets.
Just prints what emails it would find.
Command: python test_email_finder.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time, random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from storage.mongo_db import get_leads_missing_email
from scraper.email_finder import find_on_website, google_search_email
from utils.logger import get_logger

logger = get_logger("test_email_finder")

all_leads = get_leads_missing_email()

# Only check first 5 leads to keep test fast
to_check = [lead for lead in all_leads][:5]

print(f"\nChecking {len(to_check)} leads for emails (test — not saving to Sheets)\n")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for lead in to_check:
        name    = lead.get("Business Name", "")
        website = lead.get("Website", "").strip()
        city    = lead.get("City", "")
        print(f"Business: {name}")

        email = ""

        if website:
            print(f"  Checking website: {website}")
            email = find_on_website(page, website)

        if not email:
            print(f"  Trying Google search...")
            email = google_search_email(page, name, city)

        if email:
            print(f"  FOUND: {email}")
        else:
            print(f"  Not found — use phone: {lead.get('Phone', '')}")
        print()
        time.sleep(random.uniform(1, 2))

    browser.close()

print("=" * 60)
print("To save emails run:")
print("  python scraper/email_finder.py")

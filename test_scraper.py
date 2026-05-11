"""
test_scraper.py — run from project root to test scraping
Command: python test_scraper.py
Custom:  python test_scraper.py Jaipur restaurants
"""

import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scraper.justdial_scraper import scrape_justdial
from config import TARGET_CITY, TARGET_BUSINESS

city     = sys.argv[1] if len(sys.argv) > 1 else TARGET_CITY
business = sys.argv[2] if len(sys.argv) > 2 else TARGET_BUSINESS

print(f"\nScraping: {business} in {city}")
print("=" * 60)

leads = scrape_justdial(city, business, max_leads=10)

if not leads:
    print("\nNo leads found.")
    print("  1. JustDial may have blocked — wait 10 min and retry")
    print("  2. Check data/justdial_debug.html to see what was returned")
    print("  3. Try different spelling: 'Mumbai' not 'mumbai'")
else:
    print(f"\nFound {len(leads)} leads:\n")
    for i, lead in enumerate(leads, 1):
        print(f"--- Lead {i} ---")
        print(f"  Name:    {lead['Business Name']}")
        print(f"  Phone:   {lead['Phone']}")
        print(f"  Email:   {lead['Email'] or '(not on listing)'}")
        print(f"  Website: {lead['Website'] or '(not listed)'}")
        print(f"  Notes:   {lead['Notes']}")
        print()
    print("=" * 60)
    print(f"Total: {len(leads)} leads")
    print("Looks good? Save to SQLite:")
    print("  python scraper/justdial_scraper.py")
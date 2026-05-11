"""
test_email.py
Tests Brevo connection by sending a test email to yourself.
Run this BEFORE sending to real leads.
Command: python test_email.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emailer.brevo_sender import test_brevo_connection
from emailer.templates import get_template
from config import FROM_EMAIL, YOUR_NAME

print("=" * 50)
print("Step 1: Testing Brevo API connection...")
print("=" * 50)

ok = test_brevo_connection()

if ok:
    print()
    print("=" * 50)
    print("Step 2: Previewing email template...")
    print("=" * 50)
    template = get_template(0, "Demo Restaurant", "Jaipur")
    print(f"\nSUBJECT: {template['subject']}")
    print(f"\nBODY:\n{template['body']}")
    print()
    print("=" * 50)
    print(f"Check your inbox at {FROM_EMAIL}")
    print("If test email arrived → ready for Step 5 (GitHub Actions)")
    print("=" * 50)
else:
    print()
    print("FAILED. Check:")
    print("  1. BREVO_API_KEY is set correctly in .env")
    print("  2. FROM_EMAIL is set in .env")
    print("  3. You verified your sender email in Brevo dashboard")
    print("     → brevo.com → Senders & IP → Add a sender email → verify it")

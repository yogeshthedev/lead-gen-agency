"""
test_sheets.py — Run this to verify Google Sheets connection works.
Command: python test_sheets.py
"""

print("Testing Google Sheets connection...")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from config import GOOGLE_SHEET_ID, CREDENTIALS_FILE, SHEET_HEADERS
    import os

    # Check credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[FAIL] {CREDENTIALS_FILE} not found in project folder.")
        print("  → Download it from Google Cloud Console → Service Accounts → Keys")
        exit(1)

    # Check Sheet ID is set
    if not GOOGLE_SHEET_ID or GOOGLE_SHEET_ID == "your_google_sheet_id_here":
        print("[FAIL] GOOGLE_SHEET_ID not set in .env file.")
        print("  → Copy the ID from your Google Sheet URL and paste it in .env")
        exit(1)

    # Connect
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    print("[OK] Credentials loaded")

    # Open sheet
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    print(f"[OK] Sheet opened: '{sheet.spreadsheet.title}'")

    # Write headers if empty
    existing = sheet.row_values(1)
    if not existing:
        sheet.append_row(SHEET_HEADERS)
        print("[OK] Headers written to sheet")
    else:
        print(f"[OK] Sheet already has data — first cell: '{existing[0]}'")

    # Write a test lead row
    test_lead = ["" for _ in SHEET_HEADERS]
    test_lead[0] = "TEST BUSINESS"
    test_lead[1] = "Test Owner"
    test_lead[2] = "test@example.com"
    test_lead[3] = "9876543210"
    test_lead[4] = "https://testbusiness.com"
    test_lead[6] = "Jaipur"
    test_lead[7] = "Restaurant"
    test_lead[8] = "manual_test"
    test_lead[9] = "2024-01-01"
    test_lead[10] = "not_sent"
    test_lead[13] = "This is a test row — delete me"
    sheet.append_row(test_lead)
    print("[OK] Test row written to sheet successfully")
    print()
    print("=" * 50)
    print("Google Sheets connection working!")
    print("Open your Sheet and delete the TEST row.")
    print("Ready for Step 3 — building the scraper.")
    print("=" * 50)

except gspread.exceptions.APIError as e:
    print(f"[FAIL] Google Sheets API error: {e}")
    print("  → Make sure you shared the sheet with your service account email")
except Exception as e:
    print(f"[FAIL] Unexpected error: {e}")

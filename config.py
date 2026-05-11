import os
from dotenv import load_dotenv
load_dotenv()

# ── Brevo ─────────────────────────────────────
BREVO_API_KEY    = os.getenv("BREVO_API_KEY")
FROM_EMAIL       = os.getenv("FROM_EMAIL")
FROM_NAME        = os.getenv("FROM_NAME")

# ── Google Sheets ─────────────────────────────
GOOGLE_SHEET_ID  = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = "credentials.json"

# ── Storage ───────────────────────────────────
DB_PATH = os.getenv("DB_PATH", os.path.join("data", "leads.db"))
EXPORT_TO_SHEETS = os.getenv("EXPORT_TO_SHEETS", "1").strip() not in ("0", "false", "False")

# ── Your details ─────────────────────────────
YOUR_NAME        = os.getenv("YOUR_NAME",     "Your Name")
YOUR_CAL_LINK    = os.getenv("YOUR_CAL_LINK", "https://cal.com/yourname")
YOUR_WEBSITE     = os.getenv("YOUR_WEBSITE",  "https://yourwebsite.com")

# ── Scraping ──────────────────────────────────
TARGET_CITY      = os.getenv("TARGET_CITY",     "Jaipur")
TARGET_BUSINESS  = os.getenv("TARGET_BUSINESS", "chartered accountants")
SCRAPE_DELAY_MIN = 2
SCRAPE_DELAY_MAX = 5

# ── Email follow-up schedule (days) ──────────
FOLLOWUP_DAYS    = [3, 7, 14]

# ── Sheet columns (14 base + 3 WhatsApp + 5 scoring) ─────
SHEET_HEADERS = [
    "Business Name",    # A - col 1
    "Owner / Contact",  # B - col 2
    "Email",            # C - col 3
    "Phone",            # D - col 4
    "Website",          # E - col 5
    "Maps URL",         # F - col 6
    "City",             # G - col 7
    "Category",         # H - col 8
    "Source",           # I - col 9
    "Date Scraped",     # J - col 10
    "Email Status",     # K - col 11
    "Last Email Date",  # L - col 12
    "Follow Up Count",  # M - col 13
    "Notes",            # N - col 14
    "WhatsApp Status",  # O - col 15
    "WhatsApp Date",    # P - col 16
    "WhatsApp Count",   # Q - col 17
    "Rating",           # R - col 18
    "Review Count",     # S - col 19
    "Has Website",      # T - col 20
    "Website Quality",  # U - col 21
    "Lead Score",       # V - col 22
    "Response",         # W - col 23
]

# Column numbers (1-based, for gspread update_cell)
COL_EMAIL_STATUS  = 11  # K
COL_LAST_DATE     = 12  # L
COL_FOLLOWUP      = 13  # M
COL_WA_STATUS     = 15  # O
COL_WA_DATE       = 16  # P
COL_WA_COUNT      = 17  # Q
# ── MongoDB (replaces SQLite) ──────────────────
MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb+srv://user:password@cluster.mongodb.net/leadgen")

# ── Google Credentials (for Sheets sync) ──────
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")

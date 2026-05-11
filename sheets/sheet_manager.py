"""
sheets/sheet_manager.py
All Google Sheets read/write operations.
Single source of truth for sheet interactions.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gspread
from google.oauth2.service_account import Credentials
from config import (
    GOOGLE_SHEET_ID, CREDENTIALS_FILE, SHEET_HEADERS,
    COL_EMAIL_STATUS, COL_LAST_DATE, COL_FOLLOWUP,
    COL_WA_STATUS, COL_WA_DATE, COL_WA_COUNT
)
from storage.mongo_db import export_rows
from utils.logger import get_logger
from utils.helpers import today_str

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet():
    """Connect and return sheet1."""
    creds  = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID).sheet1


def export_db_to_sheet():
    """Replace sheet contents with current SQLite data."""
    try:
        sheet = get_sheet()
    except Exception as e:
        logger.warning("Sheets export skipped: %s", e)
        return False

    try:
        setup_headers(sheet)
        sheet.clear()
        sheet.append_row(SHEET_HEADERS)

        rows = export_rows()
        if not rows:
            logger.info("Sheets export complete: no rows")
            return True

        chunk = 200
        for i in range(0, len(rows), chunk):
            sheet.append_rows(rows[i:i + chunk])
        logger.info("Sheets export complete: %s rows", len(rows))
        return True
    except Exception as e:
        logger.warning("Sheets export failed: %s", e)
        return False


def setup_headers(sheet):
    """Write headers if sheet is empty."""
    if not sheet.row_values(1):
        sheet.append_row(SHEET_HEADERS)
        logger.info("Headers written to sheet.")
    else:
        existing = sheet.row_values(1)

        def ensure_headers(headers):
            nonlocal existing
            for h in headers:
                if h not in existing:
                    sheet.update_cell(1, len(existing) + 1, h)
                    existing.append(h)

        # Add WhatsApp columns if missing
        ensure_headers(["WhatsApp Status", "WhatsApp Date", "WhatsApp Count"])
        # Add scoring/quality columns if missing
        ensure_headers(["Rating", "Review Count", "Has Website", "Website Quality", "Lead Score"])


def get_all_leads(sheet) -> list:
    """Return all rows as list of dicts. Handles empty/duplicate headers."""
    try:
        records = sheet.get_all_records(default_blank="")
    except Exception:
        # Fallback: manual parse if headers have duplicates or empty cols
        all_values = sheet.get_all_values()
        if not all_values:
            return []
        headers = all_values[0]
        records = []
        for row in all_values[1:]:
            record = {}
            for i, header in enumerate(headers):
                if header and header not in record:  # skip empty/duplicate headers
                    record[header] = row[i] if i < len(row) else ""
            records.append(record)
    logger.info(f"Fetched {len(records)} leads.")
    return records


def lead_already_exists(sheet, email: str, phone: str, name: str = "") -> bool:
    """Check by phone OR email OR name — prevents duplicates across sources."""
    all_data = sheet.get_all_values()
    name_clean = name.strip().lower()[:30] if name else ""

    for row in all_data[1:]:
        row_email = row[2].strip().lower() if len(row) > 2 else ""
        row_phone = row[3].strip()         if len(row) > 3 else ""
        row_name  = row[0].strip().lower()[:30] if len(row) > 0 else ""

        # Phone match (most reliable)
        if phone and len(phone) >= 8 and row_phone and row_phone == phone:
            return True
        # Email match
        if email and row_email and row_email == email.lower():
            return True
        # Name match — catches same business from different sources
        if name_clean and len(name_clean) >= 5 and row_name:
            if name_clean == row_name:
                return True
            # Fuzzy: if first 20 chars match
            if len(name_clean) >= 10 and name_clean[:20] == row_name[:20]:
                return True
    return False


def add_lead(sheet, lead: dict) -> bool:
    """Add a new lead. Returns False if duplicate."""
    email = lead.get("Email", "").strip()
    phone = lead.get("Phone", "").strip()

    name = lead.get("Business Name", "").strip()
    if lead_already_exists(sheet, email, phone, name):
        logger.info(f"Skipped duplicate: {lead.get('Business Name')}")
        return False

    row = [
        lead.get("Business Name",   ""),
        lead.get("Owner / Contact", ""),
        lead.get("Email",           ""),
        lead.get("Phone",           ""),
        lead.get("Website",         ""),
        lead.get("Maps URL",        ""),
        lead.get("City",            ""),
        lead.get("Category",        ""),
        lead.get("Source",          ""),
        lead.get("Date Scraped",    today_str()),
        lead.get("Email Status",    "not_sent"),
        lead.get("Last Email Date", ""),
        lead.get("Follow Up Count", 0),
        lead.get("Notes",           ""),
        "",  # WhatsApp Status
        "",  # WhatsApp Date
        0,   # WhatsApp Count
        lead.get("Rating", ""),
        lead.get("Review Count", ""),
        lead.get("Has Website", ""),
        lead.get("Website Quality", ""),
        lead.get("Lead Score", ""),
    ]
    sheet.append_row(row)
    logger.info(f"Added: {lead.get('Business Name')} | {email or phone}")
    return True


def update_email_status(sheet, row_index: int, status: str, followup_count: int = None):
    """Update email status columns."""
    sheet.update_cell(row_index, COL_EMAIL_STATUS, status)
    sheet.update_cell(row_index, COL_LAST_DATE,    today_str())
    if followup_count is not None:
        sheet.update_cell(row_index, COL_FOLLOWUP, followup_count)
    logger.info(f"Row {row_index} email status: {status}")


def update_wa_status(sheet, row_index: int, status: str, count: int):
    """Update WhatsApp status columns."""
    sheet.update_cell(row_index, COL_WA_STATUS, status)
    sheet.update_cell(row_index, COL_WA_DATE,   today_str())
    sheet.update_cell(row_index, COL_WA_COUNT,  count)
    logger.info(f"Row {row_index} WhatsApp status: {status} (count: {count})")


def get_leads_to_email(sheet) -> list:
    """Leads with email, status = not_sent."""
    records = sheet.get_all_records()
    result  = [
        (i + 2, r) for i, r in enumerate(records)
        if r.get("Email Status") == "not_sent"
        and r.get("Email", "").strip()
    ]
    logger.info(f"{len(result)} leads ready to email.")
    return result


def get_leads_for_followup(sheet, days_ago: int) -> list:
    """Leads due for follow-up on day N."""
    from datetime import datetime, timedelta
    records     = sheet.get_all_records()
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    result      = []

    for i, r in enumerate(records):
        if (
            r.get("Email Status") in ("sent", "follow_up")
            and r.get("Last Email Date") == target_date
            and int(r.get("Follow Up Count", 0) or 0) < 3
            and r.get("Email", "").strip()
        ):
            result.append((i + 2, r))

    logger.info(f"Day-{days_ago} follow-up: {len(result)} leads")
    return result


def get_leads_for_whatsapp(sheet) -> list:
    """Leads with phone, not yet messaged on WhatsApp."""
    from datetime import datetime, timedelta
    records = sheet.get_all_records()
    result  = []

    for i, r in enumerate(records):
        phone    = r.get("Phone", "").strip()
        name     = r.get("Business Name", "").strip()
        wa_status = r.get("WhatsApp Status", "").strip()
        wa_date   = r.get("WhatsApp Date", "").strip()
        wa_count  = int(r.get("WhatsApp Count", 0) or 0)

        if not phone or not name:
            continue
        if wa_status == "wa_done":
            continue

        # First message
        if not wa_status:
            result.append((i + 2, r, 0))
            continue

        # Follow-up — check days since last message
        if wa_status == "wa_sent" and wa_date:
            try:
                days_since = (datetime.now() - datetime.strptime(wa_date, "%Y-%m-%d")).days
                followup_schedule = {1: 4, 2: 8}  # count → days to wait
                if wa_count in followup_schedule and days_since >= followup_schedule[wa_count]:
                    result.append((i + 2, r, wa_count))
            except:
                pass

    logger.info(f"{len(result)} leads ready for WhatsApp.")
    return result


def get_stats(sheet) -> dict:
    """Return summary stats for dashboard."""
    records = sheet.get_all_records()
    stats = {
        "total":       len(records),
        "has_email":   0,
        "no_email":    0,
        "not_sent":    0,
        "interested":  0,
        "not_interested": 0,
        "closed":      0,
        "sent":        0,
        "follow_up":   0,
        "replied":     0,
        "failed":      0,
        "wa_pending":  0,
        "wa_sent":     0,
        "wa_done":     0,
        "by_source":   {},
        "by_category": {},
        "by_day":      {},
    }

    for r in records:
        email     = r.get("Email", "").strip()
        status    = r.get("Email Status", "not_sent")
        wa_status = r.get("WhatsApp Status", "")
        source    = r.get("Source", "unknown")
        category  = r.get("Category", "unknown")
        date      = r.get("Date Scraped", "")

        stats["has_email"] += 1 if email else 0
        stats["no_email"]  += 0 if email else 1
        stats[status]       = stats.get(status, 0) + 1

        if not wa_status:          stats["wa_pending"] += 1
        elif wa_status == "wa_sent": stats["wa_sent"]  += 1
        elif wa_status == "wa_done": stats["wa_done"]  += 1

        stats["by_source"][source]     = stats["by_source"].get(source, 0) + 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        if date:
            stats["by_day"][date] = stats["by_day"].get(date, 0) + 1

    return stats

    # Alias for backwards compatibility
def update_lead_status(sheet, row_index: int, status: str, followup_count: int = None):
    """Alias for update_email_status."""
    return update_email_status(sheet, row_index, status, followup_count)
"""
storage/db.py
SQLite storage for leads (source of truth).
"""

import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from config import DB_PATH, SHEET_HEADERS
from utils.logger import get_logger
from utils.helpers import today_str

logger = get_logger(__name__)


def _db_path() -> str:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH


def _connect():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


DB_COLUMNS = [
    "business_name",
    "owner_contact",
    "email",
    "phone",
    "website",
    "maps_url",
    "city",
    "category",
    "source",
    "date_scraped",
    "email_status",
    "last_email_date",
    "follow_up_count",
    "notes",
    "wa_status",
    "wa_date",
    "wa_count",
    "rating",
    "review_count",
    "has_website",
    "website_quality",
    "lead_score",
    "response",
    "normalized_name",
]


SHEET_TO_DB = {
    "Business Name": "business_name",
    "Owner / Contact": "owner_contact",
    "Email": "email",
    "Phone": "phone",
    "Website": "website",
    "Maps URL": "maps_url",
    "City": "city",
    "Category": "category",
    "Source": "source",
    "Date Scraped": "date_scraped",
    "Email Status": "email_status",
    "Last Email Date": "last_email_date",
    "Follow Up Count": "follow_up_count",
    "Notes": "notes",
    "WhatsApp Status": "wa_status",
    "WhatsApp Date": "wa_date",
    "WhatsApp Count": "wa_count",
    "Rating": "rating",
    "Review Count": "review_count",
    "Has Website": "has_website",
    "Website Quality": "website_quality",
    "Lead Score": "lead_score",
    "Response": "response",
}

DB_TO_SHEET = {v: k for k, v in SHEET_TO_DB.items()}


def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT,
            owner_contact TEXT,
            email TEXT,
            phone TEXT,
            website TEXT,
            maps_url TEXT,
            city TEXT,
            category TEXT,
            source TEXT,
            date_scraped TEXT,
            email_status TEXT,
            last_email_date TEXT,
            follow_up_count INTEGER,
            notes TEXT,
            wa_status TEXT,
            wa_date TEXT,
            wa_count INTEGER,
            rating TEXT,
            review_count TEXT,
            has_website TEXT,
            website_quality TEXT,
            lead_score TEXT,
            response TEXT DEFAULT '',
            normalized_name TEXT
        )
        """
    )
    # Migrate: add response column if missing (existing DBs)
    try:
        cur.execute("SELECT response FROM leads LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE leads ADD COLUMN response TEXT DEFAULT ''")
        logger.info("Migrated: added 'response' column")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_norm_name ON leads(normalized_name)")
    conn.commit()
    conn.close()


def _normalize_name(name: str) -> str:
    return (name or "").strip().lower()[:30]


def _lead_value(lead: Dict, key: str) -> str:
    return str(lead.get(key, "") or "").strip()


def _lead_to_db_row(lead: Dict) -> Dict:
    row = {k: "" for k in DB_COLUMNS}
    for sheet_key, db_key in SHEET_TO_DB.items():
        row[db_key] = _lead_value(lead, sheet_key)
    row["normalized_name"] = _normalize_name(row.get("business_name", ""))
    return row


def lead_exists(conn, email: str, phone: str, name: str) -> bool:
    email = (email or "").strip().lower()
    phone = (phone or "").strip()
    name_norm = _normalize_name(name)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT id FROM leads
        WHERE
            (? != '' AND phone = ?)
            OR (? != '' AND lower(email) = ?)
            OR (? != '' AND normalized_name = ?)
        LIMIT 1
        """,
        (phone, phone, email, email, name_norm, name_norm),
    )
    return cur.fetchone() is not None


def add_lead(lead: Dict) -> bool:
    init_db()
    row = _lead_to_db_row(lead)
    conn = _connect()
    try:
        if lead_exists(conn, row.get("email"), row.get("phone"), row.get("business_name")):
            logger.info("Skipped duplicate: %s", row.get("business_name"))
            return False
        cols = [c for c in DB_COLUMNS if c != "normalized_name"] + ["normalized_name"]
        vals = [row.get(c, "") for c in cols]
        placeholders = ",".join(["?"] * len(cols))
        conn.execute(
            f"INSERT INTO leads ({','.join(cols)}) VALUES ({placeholders})",
            vals,
        )
        conn.commit()
        logger.info("Added: %s | %s", row.get("business_name"), row.get("email") or row.get("phone"))
        return True
    finally:
        conn.close()


def _row_to_lead(row: sqlite3.Row) -> Dict:
    lead = {DB_TO_SHEET.get(k, k): row[k] for k in row.keys() if k in DB_TO_SHEET}
    lead["id"] = row["id"]
    return lead


def get_all_leads() -> List[Dict]:
    init_db()
    conn = _connect()
    try:
        cur = conn.execute("SELECT * FROM leads ORDER BY id ASC")
        return [_row_to_lead(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_leads_to_email() -> List[Dict]:
    init_db()
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT * FROM leads WHERE email_status = 'not_sent' AND email != '' ORDER BY id ASC"
        )
        return [_row_to_lead(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_leads_missing_email() -> List[Dict]:
    init_db()
    conn = _connect()
    try:
        cur = conn.execute("SELECT * FROM leads WHERE email = '' OR email IS NULL ORDER BY id ASC")
        return [_row_to_lead(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_email_status(lead_id: int, status: str, followup_count: Optional[int] = None):
    init_db()
    conn = _connect()
    try:
        conn.execute(
            "UPDATE leads SET email_status = ?, last_email_date = ? WHERE id = ?",
            (status, today_str(), lead_id),
        )
        if followup_count is not None:
            conn.execute(
                "UPDATE leads SET follow_up_count = ? WHERE id = ?",
                (int(followup_count), lead_id),
            )
        conn.commit()
        logger.info("Lead %s email status: %s", lead_id, status)
    finally:
        conn.close()


def update_lead_fields(lead_id: int, fields: Dict):
    if not fields:
        return
    init_db()
    conn = _connect()
    try:
        db_fields = {}
        for sheet_key, value in fields.items():
            db_key = SHEET_TO_DB.get(sheet_key, sheet_key)
            if db_key in DB_COLUMNS:
                db_fields[db_key] = value
        if not db_fields:
            return
        if "business_name" in db_fields:
            db_fields["normalized_name"] = _normalize_name(db_fields["business_name"])
        sets = ",".join([f"{k} = ?" for k in db_fields.keys()])
        values = list(db_fields.values()) + [lead_id]
        conn.execute(f"UPDATE leads SET {sets} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def get_leads_for_followup(days_ago: int) -> List[Dict]:
    init_db()
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT * FROM leads
            WHERE email_status IN ('sent','follow_up')
              AND last_email_date = ?
              AND email != ''
            ORDER BY id ASC
            """,
            (target_date,),
        )
        results = []
        for row in cur.fetchall():
            followup_count = int(row["follow_up_count"] or 0)
            if followup_count < 3:
                results.append(_row_to_lead(row))
        return results
    finally:
        conn.close()


def get_leads_for_whatsapp() -> List[Dict]:
    init_db()
    conn = _connect()
    try:
        cur = conn.execute("SELECT * FROM leads ORDER BY id ASC")
        leads = [_row_to_lead(r) for r in cur.fetchall()]
    finally:
        conn.close()

    from datetime import datetime as _dt
    result = []
    for lead in leads:
        phone = str(lead.get("Phone", "")).strip()
        name = str(lead.get("Business Name", "")).strip()
        wa_status = str(lead.get("WhatsApp Status", "")).strip()
        wa_date = str(lead.get("WhatsApp Date", "")).strip()
        wa_count = int(lead.get("WhatsApp Count", 0) or 0)

        if not phone or not name:
            continue
        if wa_status == "wa_done":
            continue

        if not wa_status:
            result.append((lead, 0))
            continue

        if wa_status == "wa_sent" and wa_date:
            try:
                days_since = (_dt.now() - _dt.strptime(wa_date, "%Y-%m-%d")).days
                followup_schedule = {1: 4, 2: 8}
                if wa_count in followup_schedule and days_since >= followup_schedule[wa_count]:
                    result.append((lead, wa_count))
            except Exception:
                pass

    return result


def update_wa_status(lead_id: int, status: str, count: int):
    init_db()
    conn = _connect()
    try:
        conn.execute(
            "UPDATE leads SET wa_status = ?, wa_date = ?, wa_count = ? WHERE id = ?",
            (status, today_str(), int(count), lead_id),
        )
        conn.commit()
        logger.info("Lead %s WhatsApp status: %s (count: %s)", lead_id, status, count)
    finally:
        conn.close()


def get_stats() -> Dict:
    leads = get_all_leads()
    stats = {
        "total": len(leads),
        "has_email": 0,
        "no_email": 0,
        "not_sent": 0,
        "interested": 0,
        "not_interested": 0,
        "closed": 0,
        "sent": 0,
        "follow_up": 0,
        "replied": 0,
        "failed": 0,
        "wa_pending": 0,
        "wa_sent": 0,
        "wa_done": 0,
        "by_source": {},
        "by_category": {},
        "by_day": {},
    }

    for r in leads:
        email = str(r.get("Email", "")).strip()
        status = r.get("Email Status", "not_sent")
        wa_status = r.get("WhatsApp Status", "")
        source = r.get("Source", "unknown")
        category = r.get("Category", "unknown")
        date = r.get("Date Scraped", "")

        stats["has_email"] += 1 if email else 0
        stats["no_email"] += 0 if email else 1
        stats[status] = stats.get(status, 0) + 1

        if not wa_status:
            stats["wa_pending"] += 1
        elif wa_status == "wa_sent":
            stats["wa_sent"] += 1
        elif wa_status == "wa_done":
            stats["wa_done"] += 1

        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        if date:
            stats["by_day"][date] = stats["by_day"].get(date, 0) + 1

    return stats


def export_rows() -> List[List[str]]:
    leads = get_all_leads()
    rows = []
    for lead in leads:
        row = []
        for header in SHEET_HEADERS:
            row.append(str(lead.get(header, "") or ""))
        rows.append(row)
    return rows

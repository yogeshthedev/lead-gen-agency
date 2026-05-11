"""
migrate_sheet_to_db.py
One-time migration: Google Sheets -> SQLite.
Command: python migrate_sheet_to_db.py
"""

import sys
sys.path.insert(0, ".")

from sheets.sheet_manager import get_sheet, get_all_leads
from storage.mongo_db import add_lead, init_db


def main():
    init_db()
    sheet = get_sheet()
    leads = get_all_leads(sheet)
    added = 0
    skipped = 0

    for lead in leads:
        if add_lead(lead):
            added += 1
        else:
            skipped += 1

    print(f"Imported: {added}, skipped duplicates: {skipped}")


if __name__ == "__main__":
    main()

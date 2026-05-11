import os
import sys

# Change to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH
from storage.mongo_db import init_db
from sheets.sheet_manager import export_db_to_sheet

def main():
    db_file = os.path.abspath(DB_PATH)
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Deleted database file: {db_file}")
        except Exception as e:
            print(f"Error deleting database file (it might be in use): {e}")
            return
    else:
        print(f"Database file not found: {db_file}")
    
    # Re-initialize the empty database
    init_db()
    print("Re-initialized empty database.")
    
    # Export the empty database to Google Sheets (clears old data)
    print("Syncing empty database to Google Sheets...")
    if export_db_to_sheet():
        print("Successfully cleared Google Sheet.")
    else:
        print("Failed to sync to Google Sheet. Please check credentials.")

if __name__ == "__main__":
    main()

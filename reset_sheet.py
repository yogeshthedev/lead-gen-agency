import sys
sys.path.insert(0, '.')
from sheets.sheet_manager import export_db_to_sheet

if export_db_to_sheet():
	print('Sheet synced from SQLite.')
else:
	print('Sheet sync failed. Check Google Sheets credentials.')
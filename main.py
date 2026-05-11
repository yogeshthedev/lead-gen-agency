"""
main.py — Master pipeline
Scrape (JustDial + Maps) → Find emails → Send emails → Follow-ups
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.logger import get_logger
logger = get_logger("main")
from config import EXPORT_TO_SHEETS
from sheets.sheet_manager import export_db_to_sheet

def run_justdial():
    logger.info("--- STEP 1a: JustDial scraper ---")
    try:
        from scraper.justdial_scraper import scrape_and_save
        scrape_and_save()
    except Exception as e:
        logger.error(f"JustDial failed: {e}")

def run_maps():
    logger.info("--- STEP 1b: Google Maps scraper ---")
    try:
        from scraper.maps_scraper import scrape_maps_and_save
        scrape_maps_and_save()
    except Exception as e:
        logger.error(f"Maps scraper failed: {e}")

def run_email_finder():
    logger.info("--- STEP 2: Finding emails ---")
    try:
        from scraper.email_finder import enrich_leads_with_emails
        enrich_leads_with_emails()
    except Exception as e:
        logger.error(f"Email finder failed: {e}")

def run_emailer():
    logger.info("--- STEP 3: Sending cold emails ---")
    try:
        from emailer.send_emails import send_to_new_leads
        send_to_new_leads()
    except Exception as e:
        logger.error(f"Emailer failed: {e}")

def run_followups():
    logger.info("--- STEP 4: Follow-ups ---")
    try:
        from emailer.followup import run_followups as do_followups
        do_followups()
    except Exception as e:
        logger.error(f"Follow-ups failed: {e}")

if __name__ == "__main__":
    logger.info("========== Pipeline start ==========")
    run_justdial()
    run_maps()
    run_email_finder()
    run_emailer()
    run_followups()
    if EXPORT_TO_SHEETS:
        export_db_to_sheet()
    logger.info("========== Pipeline complete ==========")

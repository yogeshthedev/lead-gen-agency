"""
emailer/send_emails.py
Sends first cold email to all leads with status = 'not_sent' and a valid email.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
from storage.mongo_db import get_leads_to_email, update_email_status as update_lead_status
from emailer.brevo_sender import send_email
from emailer.templates import get_template
from utils.logger import get_logger

logger = get_logger(__name__)

DELAY_BETWEEN_EMAILS = (30, 60)  # seconds — looks human, avoids spam flags


def send_to_new_leads(limit: int = 50):
    """
    Send first cold email to leads that haven't been contacted yet.
    limit = max emails to send in one run (stay under 300/day Brevo limit)
    """
    leads_to_email = get_leads_to_email()

    if not leads_to_email:
        logger.info("No new leads to email today.")
        return 0

    # Cap at limit to stay within daily Brevo quota
    leads_to_email = leads_to_email[:limit]
    logger.info(f"Sending first email to {len(leads_to_email)} leads...")

    sent    = 0
    failed  = 0

    for lead in leads_to_email:
        lead_id = int(lead.get("id"))
        name     = lead.get("Business Name", "")
        email    = lead.get("Email", "").strip()
        city     = lead.get("City", "")

        if not email:
            logger.warning(f"Skipping {name} — no email address")
            continue

        # Get email template (follow_up_count=0 = first email)
        template = get_template(
            follow_up_count=0,
            business_name=name,
            city=city
        )

        logger.info(f"Emailing: {name} <{email}>")
        success = send_email(
            to_email=email,
            to_name=name,
            subject=template["subject"],
            body=template["body"]
        )

        if success:
            update_lead_status(lead_id, status="sent", followup_count=0)
            sent += 1
        else:
            update_lead_status(lead_id, status="failed", followup_count=0)
            failed += 1

        # Random delay between emails — critical to avoid spam detection
        delay = random.uniform(*DELAY_BETWEEN_EMAILS)
        logger.info(f"Waiting {delay:.0f}s before next email...")
        time.sleep(delay)

    logger.info(f"First emails done — Sent: {sent} | Failed: {failed}")
    return sent

"""
emailer/followup.py
Sends follow-up emails on Day 3, Day 7, Day 14 to leads that haven't replied.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
from storage.mongo_db import get_leads_for_followup, update_email_status as update_lead_status
from emailer.brevo_sender import send_email
from emailer.templates import get_template
from utils.logger import get_logger

logger = get_logger(__name__)

FOLLOWUP_SCHEDULE = [3, 7, 14]   # days after first email
DELAY_BETWEEN_EMAILS = (30, 60)  # seconds between sends


def run_followups():
    """Run all follow-up sequences for today."""
    total_sent = 0

    for days in FOLLOWUP_SCHEDULE:
        leads = get_leads_for_followup(days_ago=days)

        if not leads:
            continue

        # follow_up_count: day3=1, day7=2, day14=3
        followup_num = FOLLOWUP_SCHEDULE.index(days) + 1

        logger.info(f"Sending day-{days} follow-ups to {len(leads)} leads...")

        for lead in leads:
            lead_id = int(lead.get("id"))
            name  = lead.get("Business Name", "")
            email = lead.get("Email", "").strip()
            city  = lead.get("City", "")

            template = get_template(
                follow_up_count=followup_num,
                business_name=name,
                city=city
            )

            logger.info(f"Follow-up #{followup_num} → {name} <{email}>")
            success = send_email(
                to_email=email,
                to_name=name,
                subject=template["subject"],
                body=template["body"]
            )

            if success:
                update_lead_status(lead_id, status="follow_up", followup_count=followup_num)
                total_sent += 1
            else:
                logger.warning(f"Failed to send follow-up to {email}")

            delay = random.uniform(*DELAY_BETWEEN_EMAILS)
            logger.info(f"Waiting {delay:.0f}s...")
            time.sleep(delay)

    logger.info(f"All follow-ups done. Total sent today: {total_sent}")
    return total_sent

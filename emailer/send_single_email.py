import sys
import os
import argparse
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo_db import get_lead_by_id, update_email_status, add_email_record
from emailer.gmail_sender import send_email
from emailer.templates import get_template
from utils.logger import get_logger

logger = get_logger("send_single_email")

def main():
    parser = argparse.ArgumentParser(description="Send a single email to a lead.")
    parser.add_argument("--lead-id", required=True, help="MongoDB ObjectId of the lead")
    parser.add_argument("--template-index", type=int, default=0, help="0=cold, 1..3=followups")
    parser.add_argument("--custom-subject", help="Override template subject")
    parser.add_argument("--custom-body", help="Override template body")
    
    args = parser.parse_args()
    
    lead = get_lead_by_id(args.lead_id)
    if not lead:
        logger.error(f"Lead {args.lead_id} not found.")
        sys.exit(1)
        
    name = lead.get("Business Name", "")
    email = str(lead.get("Email", "")).strip()
    city = lead.get("City", "")
    
    if not email:
        logger.error(f"Lead {name} has no email address.")
        sys.exit(1)
        
    # Get template if custom strings are not provided
    template = get_template(
        follow_up_count=args.template_index,
        business_name=name,
        city=city
    )
    
    subject = args.custom_subject if args.custom_subject else template["subject"]
    body = args.custom_body if args.custom_body else template["body"]
    
    email_type = "cold" if args.template_index == 0 else "followup"
    
    logger.info(f"Sending {email_type} email to {name} <{email}>")
    
    # We send text as html_body by replacing newlines with <br> to make it look nicer, 
    # or just send plain text if we want. The original sent plain text.
    success = send_email(
        to_email=email,
        to_name=name,
        subject=subject,
        body=body,
        html_body=body.replace('\n', '<br>')
    )
    
    if success:
        # Update lead status
        new_status = "sent" if args.template_index == 0 else "follow_up"
        update_email_status(args.lead_id, status=new_status, followup_count=args.template_index)
        
        # Add to history
        add_email_record(args.lead_id, subject, body, email_type, "sent")
        
        logger.info("Email sent and recorded successfully.")
        sys.exit(0)
    else:
        logger.error("Failed to send email.")
        sys.exit(1)

if __name__ == "__main__":
    main()

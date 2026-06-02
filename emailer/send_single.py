import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo_db import get_lead_by_id, update_email_status
from emailer.brevo_sender import send_email
from emailer.templates import get_template
from utils.logger import get_logger

logger = get_logger("send_single")

def send_single(lead_id):
    lead = get_lead_by_id(lead_id)
    if not lead:
        logger.error(f"Lead with id {lead_id} not found.")
        sys.exit(1)
        
    name = lead.get("Business Name", "")
    email = str(lead.get("Email", "")).strip()
    city = lead.get("City", "")
    current_status = lead.get("Email Status", "not_sent")
    
    if not email:
        logger.error(f"Lead {name} has no email address.")
        sys.exit(1)
        
    # Determine follow-up count
    follow_up_count = 0
    if current_status in ["sent", "follow_up"]:
        # if it was already sent, this is a follow up
        follow_up_count = int(lead.get("Follow Up Count") or 0) + 1
        
    template = get_template(
        follow_up_count=follow_up_count,
        business_name=name,
        city=city
    )
    
    logger.info(f"Sending {'follow-up #' + str(follow_up_count) if follow_up_count > 0 else 'first email'} to: {name} <{email}>")
    success = send_email(
        to_email=email,
        to_name=name,
        subject=template["subject"],
        body=template["body"]
    )
    
    if success:
        new_status = "sent" if follow_up_count == 0 else "follow_up"
        update_email_status(lead_id, status=new_status, followup_count=follow_up_count)
        logger.info(f"Successfully sent email to {email}.")
        sys.exit(0)
    else:
        logger.error(f"Failed to send email to {email}.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_single.py <lead_id>")
        sys.exit(1)
        
    send_single(sys.argv[1])

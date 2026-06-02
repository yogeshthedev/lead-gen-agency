import os
import sys
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.mongo_db import get_all_leads, update_lead_fields

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def check_gmail_replies():
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Error: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
        sys.exit(1)

    print("Logging into Gmail IMAP...")
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(GMAIL_USER, GMAIL_PASSWORD)
        
        status, messages = imap.select("INBOX")
        if status != "OK":
            print("Could not select INBOX")
            sys.exit(1)

        print("Fetching leads from MongoDB...")
        leads = get_all_leads()
        lead_emails = {lead.get("email"): lead for lead in leads if lead.get("email")}

        print(f"Tracking {len(lead_emails)} lead email addresses.")

        # Search for all unread emails, or all emails from a specific timeframe.
        # To avoid scanning the whole inbox, let's just search for messages.
        status, message_numbers = imap.search(None, "ALL")
        if status != "OK":
            print("Error searching emails.")
            sys.exit(1)

        email_ids = message_numbers[0].split()
        # Process the last 50 emails for speed
        recent_ids = email_ids[-50:]
        
        found_replies = 0

        for e_id in recent_ids:
            res, msg_data = imap.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract Sender
                    from_header = msg.get("From", "")
                    # Extract email address between < >
                    sender_email = from_header
                    if "<" in from_header and ">" in from_header:
                        sender_email = from_header.split("<")[1].split(">")[0]
                    
                    sender_email = sender_email.strip().lower()

                    if sender_email in lead_emails:
                        lead = lead_emails[sender_email]
                        # Update lead status
                        if lead.get("email_status") != "replied":
                            print(f"Reply detected from {sender_email}! Updating lead: {lead.get('business_name')}")
                            update_lead_fields(str(lead.get("_id")), {
                                "email_status": "replied",
                                "response": "interested"
                            })
                            found_replies += 1

        print(f"Done! Found {found_replies} new replies.")
        imap.logout()

    except Exception as e:
        print(f"IMAP Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_gmail_replies()

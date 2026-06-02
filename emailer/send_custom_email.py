import sys
import json
import os
from gmail_sender import send_email
from storage.mongo_db import add_email_record

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing temp file argument"}))
        return

    temp_file = sys.argv[1]
    if not os.path.exists(temp_file):
        print(json.dumps({"error": "Temp file not found"}))
        return

    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        to_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        lead_id = data.get('lead_id')

        # Send email
        success = send_email(to_email, subject, body)
        
        if success:
            add_email_record(lead_id, subject, body, "custom_follow_up")
            print(json.dumps({"ok": True}))
        else:
            print(json.dumps({"error": "Failed to send email via SMTP"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()

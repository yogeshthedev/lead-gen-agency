import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_email(to_email: str, to_name: str, subject: str, body: str, html_body: str = None) -> bool:
    """
    Sends an email using Gmail SMTP.
    Returns True if successful, False otherwise.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_USER or GMAIL_APP_PASSWORD not set in environment.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{os.getenv('FROM_NAME', 'Your Agency')} <{GMAIL_USER}>"
        # If to_name is provided, format it
        if to_name:
            msg["To"] = f"{to_name} <{to_email}>"
        else:
            msg["To"] = to_email

        # Attach plain text body
        part1 = MIMEText(body, "plain")
        msg.attach(part1)

        # Attach HTML body if provided
        if html_body:
            part2 = MIMEText(html_body, "html")
            msg.attach(part2)

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send email
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

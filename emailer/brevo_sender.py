"""
emailer/brevo_sender.py
Handles all email sending via Brevo API.
Single responsibility: take a to/subject/body and send it.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config import BREVO_API_KEY, FROM_EMAIL, FROM_NAME
from utils.logger import get_logger

logger = get_logger(__name__)


def get_brevo_client():
    """Returns configured Brevo API client."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY
    return sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )


def send_email(to_email: str, to_name: str, subject: str, body: str) -> bool:
    """
    Send a single email via Brevo.
    Returns True if sent, False if failed.
    """
    if not to_email or "@" not in to_email:
        logger.warning(f"Invalid email address: {to_email}")
        return False

    if not BREVO_API_KEY or BREVO_API_KEY == "your_brevo_api_key_here":
        logger.error("BREVO_API_KEY not set in .env file!")
        return False

    try:
        client = get_brevo_client()

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": to_name or to_email}],
            sender={"email": FROM_EMAIL, "name": FROM_NAME},
            subject=subject,
            text_content=body,   # plain text — better deliverability than HTML
        )

        response = client.send_transac_email(send_smtp_email)
        logger.info(f"Sent to {to_email} | Message ID: {response.message_id}")
        return True

    except ApiException as e:
        logger.error(f"Brevo API error for {to_email}: {e.status} — {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to {to_email}: {e}")
        return False


def test_brevo_connection() -> bool:
    """Quick test — sends a test email to yourself to verify Brevo works."""
    logger.info("Testing Brevo connection...")
    result = send_email(
        to_email=FROM_EMAIL,
        to_name="Test",
        subject="Brevo test — lead gen system",
        body="This is a test email from your lead gen automation system. If you see this, Brevo is working correctly!"
    )
    if result:
        logger.info(f"Test email sent to {FROM_EMAIL} — check your inbox!")
    else:
        logger.error("Test email failed — check your BREVO_API_KEY in .env")
    return result

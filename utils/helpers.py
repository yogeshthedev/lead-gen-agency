import re
import time
import random
from datetime import datetime
from config import SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX


def random_delay():
    """Wait a random amount between requests — avoids bot detection."""
    delay = random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX)
    time.sleep(delay)


def clean_phone(phone: str) -> str:
    """Remove spaces, dashes, brackets from phone numbers."""
    if not phone:
        return ""
    return re.sub(r"[\s\-\(\)\+]", "", phone).strip()


def clean_email(email: str) -> str:
    """Extract and clean a valid email address from text."""
    if not email:
        return ""
    email = email.strip().lower()
    # Extract just the email part — remove anything after a valid TLD
    match = re.match(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', email)
    if match:
        return match.group(0)
    return email


def clean_text(text: str) -> str:
    """Remove extra whitespace from any text field."""
    if not text:
        return ""
    return " ".join(text.split()).strip()


def extract_emails_from_text(text: str) -> list:
    """Pull all email addresses found in a block of text."""
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(pattern, text)


def is_valid_email(email: str) -> bool:
    """Basic email format check."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def today_str() -> str:
    """Returns today's date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


def is_old_website(url: str) -> bool:
    """
    Very basic check — if the site uses old tech keywords in the URL
    or has no https, it may need a redesign. Use for lead scoring.
    """
    if not url:
        return True
    old_signals = ["wix.com", "blogspot", "weebly", "wordpress.com", "jimdo"]
    return any(signal in url.lower() for signal in old_signals)


def website_quality(url: str) -> str:
    """
    Classify website quality for lead scoring.
    Returns: missing | weak | ok
    """
    if not url:
        return "missing"
    if not url.startswith("https://"):
        return "weak"
    if is_old_website(url):
        return "weak"
    return "ok"
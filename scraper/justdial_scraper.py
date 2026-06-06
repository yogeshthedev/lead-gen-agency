"""
scraper/justdial_scraper.py
Scrapes business leads from JustDial and saves to Google Sheets.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from config import TARGET_CITY, TARGET_BUSINESS
from utils.logger import get_logger
from utils.helpers import clean_phone, clean_email, clean_text, extract_emails_from_text, today_str, website_quality
from storage.mongo_db import add_lead, init_db

logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

def build_url(city, business):
    city_fmt     = city.strip().replace(" ", "-")
    business_fmt = business.strip().replace(" ", "-")
    return f"https://www.justdial.com/{city_fmt}/{business_fmt}"

def random_delay(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))

def scrape_justdial(city, business, max_leads=30):
    url = build_url(city, business)
    logger.info(f"Scraping: {url}")
    leads = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.new_page()

        try:
            logger.info("Visiting homepage first...")
            page.goto("https://www.justdial.com", timeout=30000, wait_until="domcontentloaded")
            random_delay(2, 3)

            logger.info(f"Navigating to search...")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            random_delay(3, 5)

            # scroll to load all listings
            for _ in range(6):
                page.mouse.wheel(0, 900)
                random_delay(1, 2)

            html = page.content()
            logger.info(f"Page loaded. HTML size: {len(html)} chars")

        except Exception as e:
            logger.error(f"Browser error: {e}")
            try:
                html = page.content()
            except:
                browser.close()
                return []

        browser.close()

    os.makedirs("data", exist_ok=True)
    with open("data/justdial_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    listings = soup.select("div.resultbox_info")

    if not listings:
        logger.warning("No listings found — check data/justdial_debug.html")
        return []

    logger.info(f"Found {len(listings)} listings")

    for listing in listings[:max_leads]:
        try:
            lead = parse_listing(listing, city, business)
            if lead:
                leads.append(lead)
                logger.info(f"Parsed: {lead['Business Name']} | {lead['Phone']}")
        except Exception as e:
            logger.warning(f"Parse error: {e}")

    logger.info(f"Total leads: {len(leads)}")
    return leads


def parse_listing(listing, city, business):
    """Extract all fields from one JustDial result card."""

    # --- Business name ---
    name = ""
    for sel in [
        "span.lng_lst_Name", "span[class*='lng_lst_Name']",
        "p.store-name", "h2", "h3", "a.store-name"
    ]:
        el = listing.select_one(sel)
        if el:
            name = clean_text(el.get_text())
            break

    if not name:
        return None

    # --- Phone ---
    phone = ""
    for sel in [
        "p.contact-info span", "span.contact-info",
        "p[class*='phno']", "span[class*='phno']",
        "a[href^='tel']", "span.callcontent",
        "p.resultbox_contact_name"
    ]:
        el = listing.select_one(sel)
        if el:
            raw = el.get("href", "") or el.get_text()
            cleaned = clean_phone(raw.replace("tel:", ""))
            if cleaned and len(cleaned) >= 7:
                phone = cleaned
                break

    # --- Address ---
    address = ""
    for sel in [
        "span.jd_address", "p.resultbox_address",
        "span[class*='address']", "p[class*='address']",
        "span.cont_sw_addr", "p.store-address"
    ]:
        el = listing.select_one(sel)
        if el:
            address = clean_text(el.get_text())
            if address:
                break

    # --- Rating ---
    rating = ""
    for sel in [
        "span.green-box", "span[class*='green']",
        "span[class*='rating']", "div[class*='rating']",
        "span.resultbox_ratingwrap"
    ]:
        el = listing.select_one(sel)
        if el:
            rating = clean_text(el.get_text())
            if rating:
                break

    # --- Category / type ---
    category_detail = ""
    for sel in ["p.resultbox_type", "span[class*='category']", "p[class*='catname']"]:
        el = listing.select_one(sel)
        if el:
            category_detail = clean_text(el.get_text())
            break

    # --- Website (rare on JustDial, we'll find via email_finder later) ---
    website = ""
    for a in listing.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") and "justdial" not in href and "jdmagicbox" not in href:
            website = href
            break

    # --- Email (rarely on listing, email_finder.py will get these) ---
    email = ""
    found = extract_emails_from_text(listing.get_text())
    if found:
        email = clean_email(found[0])

    notes = []
    if rating:
        notes.append(f"Rating: {rating}")
    if address:
        notes.append(f"Address: {address}")
    if category_detail:
        notes.append(f"Type: {category_detail}")

    # Build a Google Maps search URL so you can click to view it
    maps_search = f"https://www.google.com/maps/search/{name.replace(' ', '+')}+{city.replace(' ', '+')}"

    return {
        "Business Name":   name,
        "Owner / Contact": "",
        "Email":           email,
        "Phone":           phone,
        "Website":         website,
        "Maps URL":        maps_search,
        "City":            city,
        "Category":        business,
        "Source":          "justdial",
        "Date Scraped":    today_str(),
        "Email Status":    "not_sent",
        "Last Email Date": "",
        "Follow Up Count": 0,
        "Notes":           "",
        "Rating":          rating,
        "Review Count":    "",
        "Has Website":     "yes" if website else "no",
        "Website Quality": website_quality(website),
        "Lead Score":      "",
    }


def scrape_and_save(city=None, business=None, max_leads=30, website_filter="all"):
    city     = city or TARGET_CITY
    business = business or TARGET_BUSINESS
    logger.info(f"Starting: {business} in {city}")

    leads = scrape_justdial(city, business, max_leads)
    if not leads:
        logger.warning("No leads to save.")
        return 0

    # Apply website filter before saving
    if website_filter == "with_website":
        leads = [l for l in leads if l.get("Has Website") == "yes"]
        logger.info(f"Website filter: keeping only leads WITH website ({len(leads)} leads)")
    elif website_filter == "without_website":
        leads = [l for l in leads if l.get("Has Website") != "yes"]
        logger.info(f"Website filter: keeping only leads WITHOUT website ({len(leads)} leads)")

    if not leads:
        logger.warning("No leads remaining after website filter.")
        return 0

    init_db()

    saved, skipped = 0, 0
    for lead in leads:
        if add_lead(lead):
            saved += 1
        else:
            skipped += 1
        random_delay(0.3, 0.8)

    logger.info(f"Done — Saved: {saved} | Skipped (duplicates): {skipped}")
    return saved


if __name__ == "__main__":
    city     = sys.argv[1] if len(sys.argv) > 1 else TARGET_CITY
    business = sys.argv[2] if len(sys.argv) > 2 else TARGET_BUSINESS
    scrape_and_save(city, business)
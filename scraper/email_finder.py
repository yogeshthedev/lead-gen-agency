"""
scraper/email_finder.py
Finds emails for leads. Fast and clean.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re, time, random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils.logger import get_logger
from utils.helpers import extract_emails_from_text, is_valid_email, website_quality
from storage.mongo_db import get_leads_missing_email, update_lead_fields, init_db

logger = get_logger(__name__)

# Emails to skip
BAD_EMAILS = [
    "example.com","test.com","noreply","no-reply","support@wix",
    "sentry","privacy","legal","abuse","spam","donotreply",
    "gov.in","gov.com","rajasthan.gov","nic.in",
]

# Domains to skip when extracting website from Maps
BAD_DOMAINS = [
    "google.","ggpht.","googleuser","gstatic","googleapis",
    "goo.gl","fbcdn","instagram","facebook","twitter","youtube",
    "whatsapp","apple.","microsoft.","amazonaws","cloudfront",
    "schema.org","w3.org","docs.google","maps.google","play.google",
]

def good_email(email: str) -> bool:
    if not email or "@" not in email: return False
    if not is_valid_email(email): return False
    return not any(b in email.lower() for b in BAD_EMAILS)

def good_website(url: str) -> bool:
    if not url or not url.startswith("http"): return False
    url_lower = url.lower()
    return not any(b in url_lower for b in BAD_DOMAINS)

def clean_email(raw: str) -> str:
    """Extract just the email from raw text."""
    m = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', raw)
    return m.group(0).lower() if m else ""

def get_emails_from_html(html: str) -> list:
    """Get all valid emails from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    found = []
    # mailto links first
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            e = clean_email(a["href"].replace("mailto:","").split("?")[0])
            if e and good_email(e): found.append(e)
    # regex in text
    for e in extract_emails_from_text(soup.get_text(" ")):
        e = clean_email(e)
        if e and good_email(e) and e not in found:
            found.append(e)
    return found

def get_socials_from_html(html: str) -> list:
    """Get Instagram/Facebook/LinkedIn from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    found = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(x in href for x in ["instagram.com", "facebook.com", "linkedin.com"]):
            if not any(j in href for j in ["/share", "sharer", "/post", "/status"]):
                found.add(a["href"])
    return list(found)

def find_on_website(page, url: str) -> tuple:
    """Check a website for contact email and social links."""
    if not good_website(url): return ("", [])
    base = url.rstrip("/")
    best_email = ""
    all_socials = set()
    
    for path in ["", "/contact", "/contact-us", "/about", "/contact.html", "/about-us", "/support"]:
        try:
            page.goto(base + path, timeout=10000, wait_until="domcontentloaded")
            time.sleep(0.8)
            html = page.content()
            
            emails = get_emails_from_html(html)
            if emails and not best_email:
                best_email = emails[0]
                logger.info(f"  Found on {path or '/'}: {best_email}")
                
            socials = get_socials_from_html(html)
            for s in socials: all_socials.add(s)
                
            if best_email and len(all_socials) > 0:
                break # Found enough info
        except: continue
        
    return (best_email, list(all_socials))

def get_website_from_maps(page, maps_url: str) -> str:
    """Visit Maps profile and get the business website URL."""
    if not maps_url or "google.com/maps" not in maps_url: return ""
    try:
        page.goto(maps_url, timeout=12000, wait_until="domcontentloaded")
        time.sleep(1.5)
        # Look for website button/link in Maps
        html = page.content()
        urls = re.findall(r'href="(https?://[^"]{10,100})"', html)
        for url in urls:
            if good_website(url) and len(url) > 20:
                return url
    except: pass
    return ""

def google_search_email(page, name: str, city: str) -> str:
    """Search Google for business email."""
    # Use short name only
    short = name.split("|")[0].split("-")[0].strip()[:50]
    # Strict footprint for emails
    query = f'"{short}" "{city}" ("@gmail.com" OR "@yahoo.com" OR "contact@")'.replace(" ", "+")
    try:
        page.goto(f"https://www.google.com/search?q={query}",
                  timeout=10000, wait_until="domcontentloaded")
        time.sleep(1.2)
        emails = get_emails_from_html(page.content())
        for e in emails:
            if good_email(e):
                logger.info(f"  Found via Google: {e}")
                return e
    except: pass
    return ""

def enrich_leads_with_emails():
    init_db()
    all_leads = get_leads_missing_email()

    def update_field(lead_id, field, value):
        update_lead_fields(lead_id, {field: value})

    JUNK = ["results","rating","hours","filters","showing results",
            "search instead","overview","reviews","photos","menu"]

    to_enrich = [
        lead for lead in all_leads
        if len(str(lead.get("Business Name","")).strip()) >= 5
        and not any(j in str(lead.get("Business Name","")).lower() for j in JUNK)
        and not any(ord(c) > 8000 for c in str(lead.get("Business Name","")))
    ]

    if not to_enrich:
        logger.info("All leads have emails already.")
        return 0

    logger.info(f"Finding emails for {len(to_enrich)} leads...")
    found = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox","--disable-blink-features=AutomationControlled"]
        )
        ctx  = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()

        for lead in to_enrich:
            lead_id = int(lead.get("id"))
            name     = str(lead.get("Business Name","")).strip()
            website  = str(lead.get("Website","")).strip()
            maps_url = str(lead.get("Maps URL","")).strip()
            city     = str(lead.get("City","")).strip()
            email    = ""

            logger.info(f"[{lead_id}] {name}")

            # 1. Website already in sheet
            if website and not email:
                update_field(lead_id, "Has Website", "yes")
                update_field(lead_id, "Website Quality", website_quality(website))
                email, socials = find_on_website(page, website)
                if socials:
                    update_field(lead_id, "Social Links", ",".join(socials))

            # 2. Get website from Maps profile → check it
            if maps_url and not email:
                site = get_website_from_maps(page, maps_url)
                if site and good_website(site):
                    logger.info(f"  Maps site: {site}")
                    update_lead_fields(lead_id, {"Website": site})
                    update_field(lead_id, "Has Website", "yes")
                    update_field(lead_id, "Website Quality", website_quality(site))
                    email, socials = find_on_website(page, site)
                    if socials:
                        update_field(lead_id, "Social Links", ",".join(socials))

            # 3. Google search
            if not email:
                email = google_search_email(page, name, city)

            if email:
                update_lead_fields(lead_id, {"Email": email})
                logger.info(f"  Saved: {email}")
                found += 1
            else:
                logger.info(f"  Not found")

            time.sleep(random.uniform(1, 2))

        browser.close()

    logger.info(f"Done: {found}/{len(to_enrich)} emails found.")
    return found

if __name__ == "__main__":
    enrich_leads_with_emails()
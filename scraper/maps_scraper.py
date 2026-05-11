"""
scraper/maps_scraper.py
Scrapes Google Maps. Extracts name from aria-label, full details from feed containers.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time, random, re
from playwright.sync_api import sync_playwright
from config import TARGET_CITY, TARGET_BUSINESS
from utils.logger import get_logger
from utils.helpers import clean_phone, clean_text, today_str
from storage.mongo_db import add_lead, init_db

logger = get_logger(__name__)

BAD_URL_PARTS = [
    "google.", "gstatic.", "ggpht.", "maps.google", "googleusercontent",
    "facebook.", "instagram.", "youtube.", "twitter.", "whatsapp.",
]


def parse_container_text(text: str) -> dict:
    """
    Parse a feed container's inner text into structured fields.
    Example text:
      'CA B K Goyal & Co\n4.8\nCA firm · 109 Fortune Heights\nOpens soon · 9 am · 099717 82649\nWebsite\nDirections'
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    name    = lines[0] if lines else ""
    rating  = ""
    reviews = ""
    address = ""
    phone   = ""
    has_website = False

    for line in lines[1:]:
        # Rating + review count in one line like "4.8 (123)"
        if not rating or not reviews:
            m = re.search(r'(\d\.\d)\s*\((\d[\d,]*)\)', line)
            if m:
                if not rating:
                    rating = m.group(1)
                if not reviews:
                    reviews = m.group(2).replace(",", "")
                continue

        # Rating line — contains a decimal number like 4.8
        if re.match(r'^\d\.\d', line) and not rating:
            rating = re.search(r'(\d\.\d)', line).group(1)
            continue

        # Reviews line — like "123 reviews"
        if not reviews:
            rm = re.search(r'(\d[\d,]*)\s*reviews?', line, re.I)
            if rm:
                reviews = rm.group(1).replace(",", "")
                continue

        # Phone — line with digits that looks like Indian mobile/landline
        elif re.search(r'\d{5}\s?\d{5}|\d{10}|\d{3,5}[\s\-]\d{6,8}', line) and not phone:
            # Extract just the number part
            nums = re.findall(r'[\d\s]{8,}', line)
            if nums:
                phone = clean_phone(nums[-1])  # last number in line = phone

        # Website indicator
        elif "website" in line.lower():
            has_website = True

        # Address — longer line with location info, not a phone
        elif len(line) > 10 and not re.search(r'^\d{5,}', line) and not address:
            # Skip lines that are just categories like "Certified public accountant"
            if any(c.isdigit() for c in line) or len(line) > 30:
                address = line

    return {
        "name":        clean_text(name.split("|")[0].split("-")[0].strip()[:80]),
        "rating":      rating,
        "reviews":     reviews,
        "address":     address,
        "phone":       phone,
        "has_website": has_website,
    }


def _is_real_url(url: str) -> bool:
    if not url or not url.startswith("http"):
        return False
    url_lower = url.lower()
    return not any(b in url_lower for b in BAD_URL_PARTS)


def _extract_phone_from_text(text: str) -> str:
    if not text:
        return ""
    nums = re.findall(r"\+?\d[\d\s\-\(\)]{7,}", text)
    if not nums:
        return ""
    return clean_phone(nums[0])


def _extract_details_from_panel(page) -> dict:
    details = {"phone": "", "website": "", "rating": "", "reviews": "", "address": ""}

    # Phone
    phone_el = page.query_selector('button[data-item-id*="phone"], button[aria-label^="Phone"], button[aria-label*="Phone"], div[data-item-id*="phone"]')
    if phone_el:
        phone_text = phone_el.get_attribute("aria-label") or phone_el.inner_text() or ""
        details["phone"] = _extract_phone_from_text(phone_text)

    # Website
    site_el = page.query_selector('a[data-item-id="authority"], a[aria-label^="Website"], a[aria-label*="Website"]')
    if site_el:
        href = site_el.get_attribute("href") or ""
        if _is_real_url(href):
            details["website"] = href

    # Rating and reviews from aria-labels
    rating_el = page.query_selector('span[aria-label*="stars"], div[aria-label*="stars"]')
    if rating_el:
        aria = rating_el.get_attribute("aria-label") or ""
        m = re.search(r"(\d\.\d)", aria)
        if m:
            details["rating"] = m.group(1)

    reviews_el = page.query_selector('button[aria-label*="review"], span[aria-label*="review"]')
    if reviews_el:
        aria = reviews_el.get_attribute("aria-label") or reviews_el.inner_text() or ""
        m = re.search(r"(\d[\d,]*)\s*reviews?", aria, re.I)
        if m:
            details["reviews"] = m.group(1).replace(",", "")

    # Address
    addr_el = page.query_selector('button[data-item-id="address"], div[data-item-id="address"]')
    if addr_el:
        details["address"] = (addr_el.get_attribute("aria-label") or addr_el.inner_text() or "").strip()

    # Fallback: scan panel text for phone/website
    if not details["phone"] or not details["website"]:
        panel = page.query_selector("div[role='main']")
        if panel:
            panel_text = panel.inner_text()
            if not details["phone"]:
                details["phone"] = _extract_phone_from_text(panel_text)
            if not details["website"]:
                urls = re.findall(r"https?://[^\s\)\]]{10,200}", panel_text)
                for url in urls:
                    if _is_real_url(url):
                        details["website"] = url
                        break

    return details


def scrape_google_maps(city: str, business: str, max_leads: int = 30) -> list:
    query = f"{business} in {city} India"
    url   = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    logger.info(f"Google Maps: {url}")
    leads = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 5))

            # Scroll feed to load more results and parse progressively
            logger.info("Scrolling to load listings...")
            seen = set()
            no_new_rounds = 0
            max_rounds = max(8, int(max_leads / 4) + 6)

            for _ in range(max_rounds):
                page.evaluate("""
                    var feed = document.querySelector('div[role="feed"]');
                    if (feed) { feed.scrollTop = feed.scrollTop + 700; }
                """)
                time.sleep(random.uniform(1.0, 1.7))

                # Build a map of name → maps_url from aria-label links
                links = page.query_selector_all('a[href*="/maps/place/"]')
                url_map = {}
                for link in links:
                    aria = link.get_attribute("aria-label") or ""
                    href = link.get_attribute("href") or ""
                    if aria and href:
                        url_map[aria.lower().strip()] = href

                containers = page.query_selector_all('div[role="feed"] > div')
                new_added = 0

                for container in containers:
                    try:
                        text = container.inner_text().strip()
                        if not text or len(text) < 5:
                            continue

                        parsed = parse_container_text(text)
                        name   = parsed["name"]

                        if not name or len(name) < 3:
                            continue

                        # Skip UI junk
                        has_special = any(ord(c) > 8000 for c in name)
                        skip_phrases = [
                            "showing results", "search instead", "ratinghours",
                            "all filters", "results", "open now", "closes soon",
                        ]
                        is_junk = any(p in name.lower() for p in skip_phrases)
                        is_ui = name.strip().lower() in ["results", "rating", "hours", "filters", "share", "directions", "website", "menu", "overview", "reviews", "photos"]
                        if has_special or is_junk or is_ui or len(name) < 5:
                            continue

                        if name.lower().strip() in seen:
                            continue

                        # Find Maps URL by matching name
                        maps_url = ""
                        name_lower = name.lower()
                        for key, val in url_map.items():
                            if name_lower in key or key.startswith(name_lower[:15].lower()):
                                maps_url = val
                                break

                        # Open listing panel to capture phone/website if missing
                        needs_details = not parsed["phone"] or not parsed["has_website"]
                        if needs_details:
                            try:
                                link = container.query_selector('a[href*="/maps/place/"]')
                                if link:
                                    link.click()
                                else:
                                    container.click()
                                page.wait_for_timeout(1200)
                                page.wait_for_selector('h1', timeout=6000)
                                details = _extract_details_from_panel(page)
                                if details.get("phone"):
                                    parsed["phone"] = details["phone"]
                                if details.get("website"):
                                    parsed["has_website"] = True
                                    parsed_site = details["website"]
                                else:
                                    parsed_site = ""
                                if details.get("rating") and not parsed.get("rating"):
                                    parsed["rating"] = details["rating"]
                                if details.get("reviews") and not parsed.get("reviews"):
                                    parsed["reviews"] = details["reviews"]
                                if details.get("address") and not parsed.get("address"):
                                    parsed["address"] = details["address"]
                            except Exception:
                                parsed_site = ""
                        else:
                            parsed_site = ""

                        lead = {
                            "Business Name":   name,
                            "Owner / Contact": "",
                            "Email":           "",
                            "Phone":           parsed["phone"],
                            "Website":         parsed_site,
                            "Maps URL":        maps_url,
                            "City":            city,
                            "Category":        business,
                            "Source":          "google_maps",
                            "Date Scraped":    today_str(),
                            "Email Status":    "not_sent",
                            "Last Email Date": "",
                            "Follow Up Count": 0,
                            "Notes":           "",
                            "Rating":          parsed["rating"],
                            "Review Count":    parsed["reviews"],
                            "Has Website":     "yes" if parsed["has_website"] else "no",
                            "Website Quality": "unknown" if parsed["has_website"] else "missing",
                            "Lead Score":      "",
                        }
                        leads.append(lead)
                        seen.add(name.lower().strip())
                        new_added += 1
                        logger.info(f"Parsed: {name} | Phone: {parsed['phone']} | Rating: {parsed['rating']}")

                        if len(leads) >= max_leads:
                            break

                    except Exception as e:
                        logger.warning(f"Container parse error: {e}")
                        continue

                if len(leads) >= max_leads:
                    break

                if new_added == 0:
                    no_new_rounds += 1
                else:
                    no_new_rounds = 0

                if no_new_rounds >= 3:
                    break

        except Exception as e:
            logger.error(f"Maps error: {e}")

        browser.close()

    # Deduplicate by name
    seen_names = set()
    unique_leads = []
    for lead in leads:
        n = lead["Business Name"].lower().strip()
        if n not in seen_names and len(n) > 3:
            seen_names.add(n)
            unique_leads.append(lead)

    logger.info(f"Total leads after dedup: {len(unique_leads)}")
    return unique_leads


def scrape_maps_and_save(city=None, business=None, max_leads=30):
    city     = city or TARGET_CITY
    business = business or TARGET_BUSINESS

    leads = scrape_google_maps(city, business, max_leads)
    if not leads:
        logger.warning("No leads from Google Maps.")
        return 0

    init_db()

    saved, skipped = 0, 0
    for lead in leads:
        if add_lead(lead):
            saved += 1
        else:
            skipped += 1
        time.sleep(random.uniform(0.3, 0.8))

    logger.info(f"Maps done — Saved: {saved} | Skipped: {skipped}")
    return saved


if __name__ == "__main__":
    city     = sys.argv[1] if len(sys.argv) > 1 else TARGET_CITY
    business = sys.argv[2] if len(sys.argv) > 2 else TARGET_BUSINESS
    scrape_maps_and_save(city, business)
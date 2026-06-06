"""
scraper/run_scrapers.py
Master controller script to run scrapers from UI.
Usage: python run_scrapers.py [city] [business] [source] [max_leads] [website_filter]
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import get_logger

logger = get_logger("run_scrapers")

def main():
    if len(sys.argv) < 5:
        logger.error("Usage: python run_scrapers.py <city> <business> <source: maps|justdial|both> <max_leads> [website_filter: all|with_website|without_website]")
        sys.exit(1)

    city = sys.argv[1]
    business = sys.argv[2]
    source = sys.argv[3].lower()
    
    try:
        max_leads = int(sys.argv[4])
    except ValueError:
        max_leads = 30

    website_filter = sys.argv[5] if len(sys.argv) > 5 else "all"

    logger.info(f"Starting scrape job: {business} in {city} (Source: {source}, Max: {max_leads}, Website: {website_filter})")

    if source in ["maps", "both"]:
        logger.info("--- Running Google Maps Scraper ---")
        try:
            from scraper.maps_scraper import scrape_maps_and_save
            scrape_maps_and_save(city, business, max_leads, website_filter)
        except Exception as e:
            logger.error(f"Maps scraper failed: {e}")

    if source in ["justdial", "both"]:
        logger.info("--- Running JustDial Scraper ---")
        try:
            from scraper.justdial_scraper import scrape_and_save
            scrape_and_save(city, business, max_leads, website_filter)
        except Exception as e:
            logger.error(f"JustDial scraper failed: {e}")

    logger.info("--- Running Email & Social Finder ---")
    try:
        from scraper.email_finder import enrich_leads_with_emails
        enrich_leads_with_emails()
    except Exception as e:
        logger.error(f"Email finder failed: {e}")

    logger.info("--- Scraping Job Complete ---")

if __name__ == "__main__":
    main()


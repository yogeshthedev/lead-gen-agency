import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright

query = "chartered accountants in Jaipur India"
url   = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="en-IN",
    )
    page = context.new_page()
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(4)

    # Fixed scroll — no compound assignment in JS
    for _ in range(6):
        page.evaluate("""
            var feed = document.querySelector('div[role="feed"]');
            if (feed) { feed.scrollTop = feed.scrollTop + 600; }
        """)
        time.sleep(1)

    # Save HTML
    html = page.content()
    os.makedirs("data", exist_ok=True)
    with open("data/maps_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML: {len(html)} chars")

    # Inspect place links
    links = page.query_selector_all('a[href*="/maps/place/"]')
    print(f"Total place links: {len(links)}")
    print("\n--- First 5 links ---")
    for i, link in enumerate(links[:5]):
        href  = link.get_attribute("href") or ""
        text  = link.inner_text().strip()
        aria  = link.get_attribute("aria-label") or ""
        print(f"\nLink {i+1}:")
        print(f"  href:       {href[:80]}")
        print(f"  inner_text: {repr(text[:120])}")
        print(f"  aria-label: {repr(aria[:120])}")

    # Inspect feed containers
    print("\n--- Feed containers (first 3) ---")
    containers = page.query_selector_all('div[role="feed"] > div')
    print(f"Total: {len(containers)}")
    for i, c in enumerate(containers[:3]):
        print(f"\nContainer {i+1}: {repr(c.inner_text().strip()[:300])}")

    browser.close()
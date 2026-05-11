from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
    page.on("pageerror", lambda err: print(f"ERROR: {err}"))
    page.goto("http://localhost:5000")
    page.wait_for_selector("#n-leads")
    page.click("#n-leads")
    page.wait_for_timeout(1000)
    print("Selecting new in Response filter...")
    page.select_option("#rf", "new")
    page.wait_for_timeout(1000)
    lcount = page.locator("#lcount").inner_text()
    print(f"Lead count after filter: {lcount}")
    browser.close()

"""
emailer/templates.py
Templates for every business category.
Add new categories at the bottom following the same pattern.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import YOUR_NAME, YOUR_CAL_LINK, YOUR_WEBSITE

# ─────────────────────────────────────────────
# CATEGORY TEMPLATES
# Each category has 4 emails: day1, day3, day7, day14
# ─────────────────────────────────────────────

TEMPLATES = {

    # ── Restaurants ──────────────────────────
    "restaurants": [
        {   # Day 1
            "subject": "Quick question about {name}'s website",
            "body": """Hi,

I was looking up {name} online and noticed your restaurant doesn't have a modern website yet.

Most customers in {city} search on Google before deciding where to eat. If you're not showing up with a clean, fast website — you're losing them to competitors.

I build restaurant websites in 7 days with menu, photos, and Google Maps integration. Starting at Rs. 8,000.

Free 10-min call: {cal_link}

Best,
{your_name}"""
        },
        {   # Day 3
            "subject": "Re: {name} — online visibility",
            "body": """Hi,

Just following up.

Did you know restaurants with a proper website get 35% more calls from Google than those without?

I can set that up for {name} in one week — menu, photos, contact page, Google-ready.

Rs. 8,000. Free call to discuss: {cal_link}

Best,
{your_name}"""
        },
        {   # Day 7
            "subject": "How restaurants in {city} are getting more customers online",
            "body": """Hi,

One last follow-up.

I recently helped a restaurant in {city} build their website. They started getting 3-4 new table bookings per week just from people finding them on Google.

If you'd like the same for {name}, I have one slot this week.

Book here: {cal_link}

Best,
{your_name}
{website}"""
        },
        {   # Day 14
            "subject": "Last email — {name}",
            "body": """Hi,

Last email from me — promise!

If {name} ever needs a website, I'm here. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

    # ── Chartered Accountants ─────────────────
    "chartered accountants": [
        {
            "subject": "Your website — {name}",
            "body": """Hi,

I came across {name} while researching CA firms in {city}.

Potential clients judge a CA firm's credibility by their website before calling. An outdated or missing website means losing clients to firms that look more professional online.

I build clean, professional websites for CA firms — service pages, team section, client enquiry forms — in 7 days.

Free 10-min call: {cal_link}

Best,
{your_name}

P.S. Starting at Rs. 8,000."""
        },
        {
            "subject": "Re: {name} — client acquisition online",
            "body": """Hi,

Following up on my last email.

When someone searches "{name} {city}" on Google — what do they find? If the answer is nothing or an outdated site, you're losing clients every day.

I can fix that in one week for Rs. 8,000.

Free call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "CA firms getting clients from Google — {city}",
            "body": """Hi,

Last follow-up from my side.

A CA firm in Rajasthan I worked with recently started getting 4-5 new client enquiries per week from Google alone — just from having a well-structured website with clear service pages.

One slot open this week for {name}.

Book: {cal_link}

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Last email — {name}",
            "body": """Hi,

Last email — I don't want to crowd your inbox.

If {name} ever needs a professional website, happy to help. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

    # ── Clinics / Doctors ─────────────────────
    "clinics": [
        {
            "subject": "Quick question about {name}'s website",
            "body": """Hi,

I was looking for clinics in {city} and came across {name}.

Patients today search for doctors on Google before booking. If your clinic doesn't have a fast, professional website with your services, timings, and location — you're missing patients who go to the next result.

I build clinic websites in 7 days — appointment booking, services, doctor profile, Google Maps. Starting at Rs. 8,000.

Free 10-min call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — more patients from Google",
            "body": """Hi,

Following up on my last email.

Most clinics that rank on Google in {city} have one thing in common — a clean website with clear service info and an easy way to book.

I can build that for {name} in a week.

Free call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "How clinics in {city} are getting patients online",
            "body": """Hi,

Last follow-up.

I helped a clinic in Rajasthan build their website recently. They started getting appointment requests through Google within 2 weeks of going live.

One slot open this week for {name}. Rs. 8,000, 7 days.

Book: {cal_link}

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Last email — {name}",
            "body": """Hi,

Last one — I won't email again after this.

If {name} ever needs a website, I'd love to help. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

    # ── Coaching Institutes ───────────────────
    "coaching institute": [
        {
            "subject": "Students are searching online — {name}",
            "body": """Hi,

I noticed {name} while looking at coaching institutes in {city}.

Parents and students search online before choosing a coaching centre. A professional website with your courses, results, faculty, and fees makes the first impression that gets them to call you.

I build coaching institute websites in 7 days. Starting at Rs. 8,000.

Free 10-min call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — online admissions",
            "body": """Hi,

Following up quickly.

Coaching centres in {city} with a website and Google listing get significantly more enquiry calls than those without.

I can set this up for {name} in one week for Rs. 8,000.

Free call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Coaching institute websites — what's working in {city}",
            "body": """Hi,

Last follow-up.

A coaching centre I worked with in Rajasthan saw a 40% increase in enquiry calls after we rebuilt their website and optimised it for Google.

One slot this week for {name}.

Book: {cal_link}

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Last email — {name}",
            "body": """Hi,

Last email from me.

If {name} ever needs a modern website, I'm here. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

    # ── Interior Designers ────────────────────
    "interior designers": [
        {
            "subject": "Your portfolio online — {name}",
            "body": """Hi,

I came across {name} while looking at interior designers in {city}.

Interior design is a visual business — clients want to see your work before calling. A slow or outdated website (or no website) means losing high-value clients to designers with better online presence.

I build portfolio websites for interior designers in 7 days — project gallery, before/after photos, contact form. Starting at Rs. 8,000.

Free 10-min call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — showcasing your work online",
            "body": """Hi,

Following up on my last email.

Your design work deserves to be seen. A professional portfolio website means clients find you on Google and see your best projects before even making the first call.

Rs. 8,000, 7 days. Free call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Interior designer portfolios — {city}",
            "body": """Hi,

Last follow-up.

An interior designer I helped in Rajasthan started getting 2-3 project enquiries per week from Google after we launched their portfolio website.

One slot this week for {name}.

Book: {cal_link}

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Last email — {name}",
            "body": """Hi,

Last one from me.

Whenever {name} is ready for a portfolio website, I'd love to help. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

    # ── Real Estate ───────────────────────────
    "real estate": [
        {
            "subject": "Property buyers search online first — {name}",
            "body": """Hi,

I came across {name} while looking at real estate agents in {city}.

Today's property buyers search online and shortlist agents based on their website before calling. Without a professional site showing your listings, areas you cover, and client testimonials — you're invisible to a huge chunk of buyers.

I build real estate websites in 7 days. Starting at Rs. 8,000.

Free 10-min call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — property leads from Google",
            "body": """Hi,

Following up.

Real estate agents in {city} with a website get property enquiries directly from Google search — without spending on ads.

I can build that for {name} in one week for Rs. 8,000.

Free call: {cal_link}

Best,
{your_name}"""
        },
        {
            "subject": "Real estate websites — what's working in {city}",
            "body": """Hi,

Last follow-up.

An agent I worked with in Rajasthan started getting direct property enquiries through Google within a month of launching their site.

One slot this week for {name}. Rs. 8,000, 7 days.

Book: {cal_link}

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Last email — {name}",
            "body": """Hi,

Last email — won't bother you again after this.

If {name} ever needs a website, happy to help. Rs. 8,000, 7 days.

{cal_link}

Best,
{your_name}"""
        },
    ],

}

# Fallback — used if category not found in TEMPLATES
TEMPLATES["default"] = TEMPLATES["chartered accountants"]


def get_template(follow_up_count: int, business_name: str, city: str, category: str = "") -> dict:
    """
    Returns the right email template based on category and follow_up_count.
    follow_up_count: 0=day1, 1=day3, 2=day7, 3=day14
    category: matches TARGET_BUSINESS in .env (case insensitive)
    """
    # Find matching template set
    cat = category.lower().strip()
    template_set = None

    # Exact match first
    if cat in TEMPLATES:
        template_set = TEMPLATES[cat]
    else:
        # Partial match — "chartered accountants in jaipur" → "chartered accountants"
        for key in TEMPLATES:
            if key in cat or cat in key:
                template_set = TEMPLATES[key]
                break

    if not template_set:
        template_set = TEMPLATES["default"]

    # Clamp index to available templates
    idx = min(follow_up_count, len(template_set) - 1)
    t = template_set[idx]

    # Fill in placeholders
    filled_subject = t["subject"].format(
        name=business_name, city=city,
        your_name=YOUR_NAME, cal_link=YOUR_CAL_LINK, website=YOUR_WEBSITE
    )
    filled_body = t["body"].format(
        name=business_name, city=city,
        your_name=YOUR_NAME, cal_link=YOUR_CAL_LINK, website=YOUR_WEBSITE
    )

    return {"subject": filled_subject, "body": filled_body}


def load_custom_templates() -> dict:
    """Load user-edited templates from custom_templates.json if it exists."""
    import json
    path = os.path.join(os.path.dirname(__file__), 'custom_templates.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def get_template(follow_up_count: int, business_name: str, city: str, category: str = "") -> dict:
    """
    Returns the right email for this lead.
    Checks custom templates first, then built-in.
    follow_up_count: 0=day1, 1=day3, 2=day7, 3=day14
    """
    cat = category.lower().strip()

    # 1. Check custom templates first
    custom = load_custom_templates()
    custom_set = None
    if cat in custom:
        custom_set = custom[cat]
    else:
        for key in custom:
            if key in cat or cat in key:
                custom_set = custom[key]
                break

    # 2. Fall back to built-in
    builtin_set = None
    if cat in TEMPLATES:
        builtin_set = TEMPLATES[cat]
    else:
        for key in TEMPLATES:
            if key == "default":
                continue
            if key in cat or cat in key:
                builtin_set = TEMPLATES[key]
                break

    template_set = custom_set or builtin_set or TEMPLATES["default"]

    idx = min(follow_up_count, len(template_set) - 1)
    t   = template_set[idx]

    # Handle both old format (subject/body strings) and new format (day/subject/body dicts)
    subject = t.get("subject", "")
    body    = t.get("body", "")

    filled_subject = subject.format(
        name=business_name, city=city,
        your_name=YOUR_NAME, cal_link=YOUR_CAL_LINK, website=YOUR_WEBSITE
    )
    filled_body = body.format(
        name=business_name, city=city,
        your_name=YOUR_NAME, cal_link=YOUR_CAL_LINK, website=YOUR_WEBSITE
    )
    return {"subject": filled_subject, "body": filled_body}


def get_template(follow_up_count: int, business_name: str, city: str, category: str = "") -> dict:
    """
    Returns email template. Uses custom_templates.json if it exists (edited from frontend).
    Falls back to built-in TEMPLATES.
    """
    import os, json

    # Try custom templates saved from frontend first
    custom_path = os.path.join(os.path.dirname(__file__), 'custom_templates.json')
    if os.path.exists(custom_path):
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                custom = json.load(f)
            if custom:
                TEMPLATES.update(custom)
        except:
            pass

    cat = (category or "").lower().strip()
    template_set = None

    if cat in TEMPLATES:
        template_set = TEMPLATES[cat]
    else:
        for key in TEMPLATES:
            if key == "default": continue
            if key in cat or cat in key:
                template_set = TEMPLATES[key]
                break

    if not template_set:
        template_set = TEMPLATES.get("default", TEMPLATES.get("chartered accountants", []))

    idx = min(follow_up_count, len(template_set) - 1)
    t   = template_set[idx]

    your_name = os.getenv("YOUR_NAME",    "Yogesh")
    cal_link  = os.getenv("YOUR_CAL_LINK","https://cal.com/yourname")
    website   = os.getenv("YOUR_WEBSITE", "https://yourwebsite.com")

    subject = t["subject"].format(name=business_name, city=city,
        your_name=your_name, cal_link=cal_link, website=website)
    body    = t["body"].format(name=business_name, city=city,
        your_name=your_name, cal_link=cal_link, website=website)

    return {"subject": subject, "body": body}
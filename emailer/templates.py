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

I was looking up {name} online and noticed you don't have a modern website yet.

I specialize in building websites for restaurants in {city}. Before I send over more details, I just wanted to ask — are you currently interested in upgrading your online presence?

Please reply with a quick 'Yes' or 'No' so I know whether to send more info or cross you off my list.

Best,
{your_name}"""
        },
        {   # Day 3
            "subject": "Re: {name} — online visibility",
            "body": """Hi,

Just following up on my previous email.

I can help {name} get more customers from Google with a new website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {   # Day 7
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll make this short. I help restaurants in {city} build websites that actually drive reservations.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {   # Day 14
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

Best,
{your_name}"""
        },
    ],

    # ── Chartered Accountants ─────────────────
    "chartered accountants": [
        {
            "subject": "Quick question about {name}'s website",
            "body": """Hi,

I came across {name} while researching CA firms in {city} and noticed your website could use an upgrade.

I build professional websites specifically for CA firms. Before I send over more details, are you currently interested in upgrading your online presence to get more clients?

Please reply with a quick 'Yes' or 'No'.

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — client acquisition online",
            "body": """Hi,

Following up on my last email.

I can help {name} attract more clients from Google with a modern website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll keep this short. I help CA firms in {city} build websites that rank on Google and bring in leads.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

Best,
{your_name}"""
        },
    ],

    # ── Clinics / Doctors ─────────────────────
    "clinics": [
        {
            "subject": "Quick question about {name}'s website",
            "body": """Hi,

I was looking for clinics in {city} and noticed {name} doesn't have a modern website for patients to book appointments.

I specialize in building clinic websites. Before I send over more details, I just wanted to ask — are you currently interested in upgrading your online presence?

Please reply with a quick 'Yes' or 'No'.

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — more patients from Google",
            "body": """Hi,

Just following up on my previous email.

I can help {name} get more patient bookings from Google with a new website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll make this short. I help clinics in {city} build websites that actually drive patient appointments.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

Best,
{your_name}"""
        },
    ],

    # ── Coaching Institutes ───────────────────
    "coaching institute": [
        {
            "subject": "Students are searching online — {name}",
            "body": """Hi,

I noticed {name} while looking at coaching institutes in {city} and saw your website could use an upgrade.

I build websites for coaching centres to help drive admissions. Before I send over more details, are you currently interested in upgrading your online presence?

Please reply with a quick 'Yes' or 'No'.

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — online admissions",
            "body": """Hi,

Just following up on my previous email.

I can help {name} get more admission enquiries from Google with a new website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll make this short. I help coaching centres in {city} build websites that actually drive enrollments.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

Best,
{your_name}"""
        },
    ],

    # ── Interior Designers ────────────────────
    "interior designers": [
        {
            "subject": "Your portfolio online — {name}",
            "body": """Hi,

I came across {name} while looking at interior designers in {city} and noticed your website could use an upgrade.

I build beautiful portfolio websites for interior designers. Before I send over more details, are you currently interested in upgrading your online presence to get more clients?

Please reply with a quick 'Yes' or 'No'.

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — showcasing your work online",
            "body": """Hi,

Just following up on my previous email.

I can help {name} attract more high-value clients from Google with a modern website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll make this short. I help interior designers in {city} build websites that showcase their work and drive leads.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

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

I specialize in building professional websites for real estate agents to showcase properties. Before I send over more details, are you currently interested in upgrading your online presence?

Please reply with a quick 'Yes' or 'No'.

Best,
{your_name}"""
        },
        {
            "subject": "Re: {name} — property leads from Google",
            "body": """Hi,

Just following up on my previous email.

I can help {name} get more property enquiries directly from Google with a new website. Are you interested in discussing this?

A simple 'Yes' or 'No' would be super helpful!

Best,
{your_name}"""
        },
        {
            "subject": "Checking in one last time — {name}",
            "body": """Hi,

I'll make this short. I help real estate agents in {city} build websites that actually generate leads.

If you're interested, let me know. If not, just reply 'No' and I won't reach out again.

Best,
{your_name}
{website}"""
        },
        {
            "subject": "Closing the loop — {name}",
            "body": """Hi,

I haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.

If that changes in the future, feel free to reach out.

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
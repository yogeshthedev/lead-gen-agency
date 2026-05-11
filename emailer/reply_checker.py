"""
emailer/reply_checker.py
Checks Gmail for replies, uses Groq AI (free, no limits) to classify intent.
Auto-updates lead status to interested/not_interested/replied.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re, json, base64, urllib.request, urllib.error, html
from datetime import datetime
from utils.logger import get_logger
from storage.mongo_db import get_all_leads, update_email_status

logger = get_logger(__name__)


def load_env_file(env_path):
    # Prefer python-dotenv if available; otherwise parse simple KEY=VALUE lines.
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(env_path)
        return
    except Exception:
        pass

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# Ensure API keys are available when this file is run directly.
load_env_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))


def get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES    = ['https://www.googleapis.com/auth/gmail.readonly']
    TOKEN     = os.path.join(os.path.dirname(__file__), '..', 'gmail_token.json')
    CREDS     = os.path.join(os.path.dirname(__file__), '..', 'gmail_credentials.json')

    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS):
                raise FileNotFoundError("gmail_credentials.json not found!")
            flow  = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def get_email_body(payload):
    def decode_part_data(data):
        if not data:
            return ""
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def html_to_text(raw_html):
        # Basic HTML cleanup without extra dependencies.
        text = re.sub(r"<br\s*/?>", "\n", raw_html, flags=re.IGNORECASE)
        text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    plain_parts = []
    html_parts = []

    def walk(part):
        mime = (part or {}).get("mimeType", "")
        body = (part or {}).get("body", {})
        data = body.get("data", "")

        if mime == "text/plain":
            decoded = decode_part_data(data)
            if decoded:
                plain_parts.append(decoded)
        elif mime == "text/html":
            decoded = decode_part_data(data)
            if decoded:
                html_parts.append(decoded)

        for child in (part or {}).get("parts", []) or []:
            walk(child)

    walk(payload)

    body = "\n".join(plain_parts).strip()
    if not body and html_parts:
        body = html_to_text("\n".join(html_parts))

    # Remove quoted thread tails to keep newest intent for classification.
    body = re.split(r"\n\s*(On .*wrote:|From:|Sent:|Subject:)\b", body, maxsplit=1, flags=re.IGNORECASE)[0]
    return body[:1200].strip()


def classify_reply_rule_based(reply_text):
    text = (reply_text or "").lower()
    if not text.strip():
        return "replied"

    negative_terms = [
        "not interested", "stop", "unsubscribe", "remove me", "don't contact",
        "do not contact", "no thanks", "no thank you", "not needed", "already have",
        "not now", "never", "don't email"
    ]
    positive_terms = [
        "interested", "let's talk", "lets talk", "call me", "book", "schedule",
        "share pricing", "price", "cost", "quote", "send details", "more info",
        "tell me more", "demo", "meeting"
    ]

    if any(term in text for term in negative_terms):
        return "not_interested"
    if any(term in text for term in positive_terms):
        return "interested"
    return "replied"


def classify_reply(reply_text, business_name):
    """
    Classify reply using Groq only.
    Returns: interested / not_interested / replied
    """
    prompt = (
        "You are analyzing a reply to a cold email about website design services.\n\n"
        f"Business: {business_name}\n"
        f"Their reply: {reply_text}\n\n"
        "Classify their intent as exactly one of:\n"
        "- interested: they want to know more, asking price/details, positive\n"
        "- not_interested: they said no, unsubscribe, not needed, stop emailing\n"
        "- replied: neutral, unclear, out of office\n\n"
        "Reply with ONLY one word: interested, not_interested, or replied"
    )

    # --- Groq (free model) ---
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        fallback = classify_reply_rule_based(reply_text)
        logger.warning("  GROQ_API_KEY is not set; using rule-based classification: " + fallback)
        return fallback

    model_candidates = []
    env_model = (os.getenv("GROQ_MODEL", "") or "").strip()
    if env_model:
        model_candidates.append(env_model)
    for m in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        if m not in model_candidates:
            model_candidates.append(m)

    for model in model_candidates:
        try:
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10,
                "temperature": 0
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + groq_key
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                text = result["choices"][0]["message"]["content"].strip().lower()
                for label in ["not_interested", "interested", "replied"]:
                    if label in text:
                        logger.info("  Groq model " + model + " classified as: " + label)
                        return label
                return classify_reply_rule_based(reply_text)
        except urllib.error.HTTPError as e:
            logger.warning("  Groq model " + model + " HTTP " + str(e.code) + ", trying next model")
        except Exception as e:
            logger.warning("  Groq model " + model + " error: " + str(e) + ", trying next model")

    fallback = classify_reply_rule_based(reply_text)
    logger.warning("  All Groq models failed; using rule-based classification: " + fallback)
    return fallback


def get_replies(service, days_back=30):
    query   = "in:inbox newer_than:" + str(days_back) + "d"
    results = service.users().messages().list(
        userId="me", q=query, maxResults=100
    ).execute()

    messages = results.get("messages", [])
    replies  = []

    for msg in messages:
        full = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        if "In-Reply-To" not in headers:
            continue
        from_h = headers.get("From", "")
        match  = re.search(r'<([^>]+)>', from_h)
        email  = match.group(1).lower() if match else from_h.lower().strip()
        if not email:
            continue
        body = get_email_body(full["payload"])
        replies.append({"email": email, "body": body})
        logger.info("Reply found from: " + email)

    # Deduplicate — keep longest body per email
    seen = {}
    for r in replies:
        e = r["email"]
        if e not in seen or len(r["body"]) > len(seen[e]["body"]):
            seen[e] = r
    return list(seen.values())


def update_replied_leads(replies):
    if not replies:
        logger.info("No new replies found.")
        return {"interested": 0, "not_interested": 0, "replied": 0}

    leads  = get_all_leads()
    counts = {"interested": 0, "not_interested": 0, "replied": 0}
    rmap   = {r["email"]: r for r in replies}

    for lead in leads:
        lead_email = str(lead.get("Email", "") or "").strip().lower()
        status     = str(lead.get("Email Status", "") or "").strip()
        if not lead_email or lead_email not in rmap:
            continue
        if status in ("interested", "not_interested", "closed"):
            continue

        name    = str(lead.get("Business Name", "") or "")
        lead_id = int(lead.get("id"))
        reply   = rmap[lead_email]

        logger.info("Classifying reply from " + name + " (" + lead_email + ")...")
        classification = classify_reply(reply["body"], name)

        update_email_status(lead_id, classification)
        counts[classification] += 1
        logger.info("  " + name + " -> " + classification)
        if classification == "interested":
            logger.info("  *** HOT LEAD — call " + name + " ***")

    return counts


def check_replies():
    logger.info("Checking Gmail for replies...")
    try:
        service = get_gmail_service()
        replies = get_replies(service, days_back=30)
        logger.info("Found " + str(len(replies)) + " unique replies.")
        counts  = update_replied_leads(replies)
        logger.info("Results: " + str(counts))
        return counts
    except FileNotFoundError as e:
        logger.error(str(e))
        return {}
    except Exception as e:
        logger.error("Gmail check failed: " + str(e))
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    check_replies()
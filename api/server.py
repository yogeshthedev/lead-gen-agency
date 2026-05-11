"""
api/server.py  —  Flask backend for LeadGen Dashboard
"""
import sys, os, traceback, threading, json, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from utils.helpers import today_str
from config import EXPORT_TO_SHEETS
from storage.mongo_db import (
    init_db,
    get_all_leads,
    update_email_status,
)
from sheets.sheet_manager import export_db_to_sheet

app = Flask(__name__)
CORS(app)

FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'frontend')
TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), '..', 'emailer', 'custom_templates.json')

# ── Job state ────────────────────────────────
_state = {"running": False, "done": False, "error": None, "logs": [], "step": ""}

def _log(msg):
    _state["logs"].append(msg)
    print(msg)

def _reset():
    _state.update({"running": True, "done": False, "error": None, "logs": [], "step": ""})


def _parse_int(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    s = re.sub(r"[^0-9]", "", s)
    return int(s) if s else None


def _parse_float(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


def _parse_bool(val):
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ("yes", "true", "1", "y"):
        return True
    if s in ("no", "false", "0", "n"):
        return False
    return None


def _extract_rating(lead):
    rating = _parse_float(lead.get("Rating"))
    if rating is not None:
        return rating
    notes = str(lead.get("Notes", "") or "")
    m = re.search(r"Rating:\s*([0-9.]+)", notes)
    return float(m.group(1)) if m else None


def _extract_reviews(lead):
    reviews = _parse_int(lead.get("Review Count"))
    if reviews is not None:
        return reviews
    notes = str(lead.get("Notes", "") or "")
    m = re.search(r"Reviews?:\s*([0-9,]+)", notes, re.I)
    return _parse_int(m.group(1)) if m else None


def _compute_lead_score(lead):
    score = 0
    has_website = _parse_bool(lead.get("Has Website"))
    if has_website is None:
        has_website = True if str(lead.get("Website", "") or "").strip() else False

    website_quality = str(lead.get("Website Quality", "") or "").strip().lower()
    if not website_quality:
        website_quality = "ok" if has_website else "missing"

    if not has_website or website_quality == "missing":
        score += 35
    elif website_quality == "weak":
        score += 20
    else:
        score += 5

    reviews = _extract_reviews(lead)
    if reviews is None:
        score += 5
    elif reviews == 0:
        score += 8
    elif 1 <= reviews <= 50:
        score += 15
    elif 51 <= reviews <= 200:
        score += 10
    elif reviews > 200:
        score += 3

    rating = _extract_rating(lead)
    if rating is None:
        score += 3
    elif 3.5 <= rating <= 4.6:
        score += 10
    elif rating < 3.5:
        score += 6
    else:
        score += 3

    if str(lead.get("Phone", "") or "").strip():
        score += 10
    if str(lead.get("Email", "") or "").strip():
        score += 5

    return min(score, 100)

# ── Serve frontend ───────────────────────────
@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

# ── Status ───────────────────────────────────
@app.route("/api/status")
def status():
    return jsonify(_state)

@app.route("/health")
def health():
    return jsonify({"ok": True})

# ── Stats ────────────────────────────────────
@app.route("/api/leads/stats")
def get_stats():
    try:
        leads = get_all_leads()

        JUNK = ["results","rating","hours","filters","showing results","search instead","overview","reviews","photos","menu"]

        def is_real(l):
            name = str(l.get("Business Name","") or "").strip()
            if not name or len(name) < 5: return False
            if any(ord(c) > 8000 for c in name): return False
            if name.lower() in JUNK: return False
            if any(p in name.lower() for p in ["showing results","search instead"]): return False
            return True

        clean = [l for l in leads if is_real(l)]

        stats = {
            "total": len(clean),
            "has_email": sum(1 for l in clean if str(l.get("Email","")).strip()),
            "not_sent": 0, "sent": 0, "follow_up": 0,
            "replied": 0, "interested": 0, "not_interested": 0, "closed": 0, "failed": 0,
            "by_source": {}, "by_category": {}, "by_day": {}
        }

        for l in clean:
            es  = str(l.get("Email Status","not_sent") or "not_sent").strip()
            src = str(l.get("Source","") or "").strip()
            cat = str(l.get("Category","") or "").strip()
            day = str(l.get("Date Scraped","") or "").strip()

            if es in stats: stats[es] += 1
            else: stats["not_sent"] += 1

            if src: stats["by_source"][src] = stats["by_source"].get(src, 0) + 1
            if cat: stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            if day: stats["by_day"][day] = stats["by_day"].get(day, 0) + 1

        return jsonify(stats)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── All leads ────────────────────────────────
@app.route("/api/leads")
def get_leads():
    try:
        leads = get_all_leads()
        JUNK = ["results","rating","hours","filters","showing results","search instead"]
        def is_real(l):
            name = str(l.get("Business Name","") or "").strip()
            if not name or len(name) < 5: return False
            if any(ord(c) > 8000 for c in name): return False
            if name.lower() in JUNK: return False
            return True

        # Filters
        min_score = _parse_int(request.args.get("min_score"))
        max_score = _parse_int(request.args.get("max_score"))

        min_reviews = _parse_int(request.args.get("min_reviews"))
        max_reviews = _parse_int(request.args.get("max_reviews"))

        has_website = _parse_bool(request.args.get("has_website"))

        results = []
        for l in leads:
            if not is_real(l):
                continue

            score = _compute_lead_score(l)
            rating = _extract_rating(l)
            reviews = _extract_reviews(l)
            website = str(l.get("Website", "") or "").strip()

            if not str(l.get("Has Website", "") or "").strip():
                l["Has Website"] = "yes" if website else "no"
            if not str(l.get("Website Quality", "") or "").strip():
                l["Website Quality"] = "ok" if l.get("Has Website") == "yes" else "missing"

            # Normalize fields for frontend
            l["Lead Score"] = score
            if rating is not None and not l.get("Rating"):
                l["Rating"] = rating
            if reviews is not None and not l.get("Review Count"):
                l["Review Count"] = reviews

            # Apply filters
            if min_score is not None and score < min_score:
                continue
            if max_score is not None and score > max_score:
                continue

            if min_reviews is not None or max_reviews is not None:
                review_val = reviews if reviews is not None else 0
                if min_reviews is not None and review_val < min_reviews:
                    continue
                if max_reviews is not None and review_val > max_reviews:
                    continue

            if has_website is not None:
                hw = _parse_bool(l.get("Has Website"))
                if hw is None:
                    hw = True if str(l.get("Website", "") or "").strip() else False
                if hw != has_website:
                    continue

            results.append(l)

        return jsonify({"leads": results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── Update lead status ───────────────────────
@app.route("/api/leads/update-status", methods=["POST"])
def update_status():
    try:
        data      = request.json or {}
        lead_id   = int(data.get("lead_id", 0))
        row_index = int(data.get("row_index", 0))
        status    = data.get("status", "")
        if not status or (not lead_id and not row_index):
            return jsonify({"error": "lead_id (or row_index) and status required"}), 400

        if lead_id:
            update_email_status(lead_id, status)
        else:
            # Backward compatibility: row_index is no longer supported in SQLite.
            return jsonify({"error": "row_index is deprecated; please use lead_id"}), 400

        if EXPORT_TO_SHEETS:
            export_db_to_sheet()
        return jsonify({"ok": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── Update lead notes ────────────────────────
@app.route("/api/leads/update-notes", methods=["POST"])
def update_notes():
    try:
        data = request.json or {}
        lead_id = int(data.get("lead_id", 0))
        notes = data.get("notes", "")
        if not lead_id:
            return jsonify({"error": "lead_id required"}), 400

        from storage.mongo_db import update_lead_fields
        update_lead_fields(lead_id, {"Notes": notes})

        if EXPORT_TO_SHEETS:
            export_db_to_sheet()
        return jsonify({"ok": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── Update lead response ─────────────────────
@app.route("/api/leads/update-response", methods=["POST"])
def update_response():
    try:
        data = request.json or {}
        lead_id = int(data.get("lead_id", 0))
        response = data.get("response", "")
        if not lead_id:
            return jsonify({"error": "lead_id required"}), 400

        from storage.mongo_db import update_lead_fields
        update_lead_fields(lead_id, {"Response": response})

        if EXPORT_TO_SHEETS:
            export_db_to_sheet()
        return jsonify({"ok": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── Templates ────────────────────────────────
@app.route("/api/templates", methods=["GET"])
def get_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route("/api/templates/save", methods=["POST"])
def save_templates():
    try:
        data = request.json or {}
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Scrape ───────────────────────────────────
@app.route("/api/scrape", methods=["POST"])
def scrape():
    if _state["running"]:
        return jsonify({"error": "A job is already running"}), 400
    data     = request.json or {}
    city     = data.get("city", "Jaipur")
    business = data.get("business", "chartered accountants")
    source   = data.get("source", "maps")
    limit    = int(data.get("limit", 30))
    _reset()

    def run():
        try:
            _state["step"] = "Scraping..."
            _log(f"[Scraper] {business} in {city} [{source}]")

            init_db()

            if source in ("justdial", "both"):
                _log(f"[JustDial] {business} in {city}...")
                _state["step"] = "JustDial scraping..."
                from scraper.justdial_scraper import scrape_and_save as jd_scrape
                n = jd_scrape(city=city, business=business, max_leads=limit)
                _log(f"[JustDial] Saved {n} leads.")

            if source in ("maps", "both"):
                _log(f"[Maps] {business} in {city}...")
                _state["step"] = "Google Maps scraping..."
                from scraper.maps_scraper import scrape_maps_and_save
                n = scrape_maps_and_save(city=city, business=business, max_leads=limit)
                _log(f"[Maps] Saved {n} leads.")

            _state["step"] = "Finding emails..."
            _log("[Finder] Looking for emails...")
            from scraper.email_finder import enrich_leads_with_emails
            found = enrich_leads_with_emails()
            _log(f"[Finder] Found {found} new emails.")

            if EXPORT_TO_SHEETS:
                export_db_to_sheet()

            _state["step"] = "Done"
            _state["done"] = True
        except Exception as e:
            traceback.print_exc()
            _state["error"] = str(e)
            _log(f"[ERROR] {e}")
            _state["done"] = True
        finally:
            _state["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True})

# ── Send emails ──────────────────────────────
@app.route("/api/send-emails", methods=["POST"])
def send_emails():
    if _state["running"]:
        return jsonify({"error": "A job is already running"}), 400
    _reset()

    def run():
        try:
            _state["step"] = "Sending cold emails..."
            _log("[Email] Sending cold emails to new leads...")
            from emailer.send_emails import send_to_new_leads
            sent = send_to_new_leads(limit=50)
            _log(f"[Email] Done. Sent: {sent}")
            if EXPORT_TO_SHEETS:
                export_db_to_sheet()
            _state["step"] = "Done"
            _state["done"] = True
        except Exception as e:
            traceback.print_exc()
            _state["error"] = str(e)
            _log(f"[ERROR] {e}")
            _state["done"] = True
        finally:
            _state["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True})

# ── Send follow-ups ──────────────────────────
@app.route("/api/send-followups", methods=["POST"])
def send_followups():
    if _state["running"]:
        return jsonify({"error": "A job is already running"}), 400
    _reset()

    def run():
        try:
            _state["step"] = "Sending follow-ups..."
            _log("[Followup] Checking leads for Day 3/7/14 follow-ups...")
            from emailer.followup import send_followups
            sent = send_followups()
            _log(f"[Followup] Done. Sent: {sent}")
            if EXPORT_TO_SHEETS:
                export_db_to_sheet()
            _state["step"] = "Done"
            _state["done"] = True
        except Exception as e:
            traceback.print_exc()
            _state["error"] = str(e)
            _log(f"[ERROR] {e}")
            _state["done"] = True
        finally:
            _state["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True})

# ── Run ──────────────────────────────────────
if __name__ == "__main__":
    print("\nDashboard -> http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=5000, debug=False)

# ── Check Gmail replies ───────────────────────
@app.route("/api/check-replies", methods=["POST"])
def check_replies():
    if _state["running"]:
        return jsonify({"error": "A job is already running"}), 400
    _reset()

    def run():
        try:
            _state["step"] = "Checking Gmail for replies..."
            _log("[Gmail] Checking inbox for replies...")
            from emailer.reply_checker import check_replies as do_check
            updated = do_check()
            _log(f"[Gmail] Done. Updated {updated} leads to replied status.")
            if EXPORT_TO_SHEETS:
                export_db_to_sheet()
            _state["step"] = "Done"
            _state["done"] = True
        except Exception as e:
            import traceback
            traceback.print_exc()
            _state["error"] = str(e)
            _log(f"[ERROR] {e}")
            _state["done"] = True
        finally:
            _state["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True})

# ── WhatsApp bot control ─────────────────────
import subprocess, signal

_wa_process = None

@app.route("/api/whatsapp/start", methods=["POST"])
def wa_start():
    global _wa_process
    try:
        if _wa_process and _wa_process.poll() is None:
            return jsonify({"ok": True, "message": "Bot already running"})
        wa_dir = os.path.join(os.path.dirname(__file__), '..', 'whatsapp')
        _wa_process = subprocess.Popen(
            ["node", "bot.js"],
            cwd=os.path.abspath(wa_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        return jsonify({"ok": True, "message": "Bot starting... check WhatsApp tab for QR"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/whatsapp/stop", methods=["POST"])
def wa_stop():
    global _wa_process
    try:
        if _wa_process and _wa_process.poll() is None:
            _wa_process.terminate()
            _wa_process = None
            return jsonify({"ok": True, "message": "Bot stopped"})
        return jsonify({"ok": True, "message": "Bot was not running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/whatsapp/status")
def wa_status():
    global _wa_process
    running = _wa_process is not None and _wa_process.poll() is None
    # Also check if bot's own server is up
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:3000/", timeout=2)
        connected = True
    except:
        connected = False
    return jsonify({"running": running, "connected": connected})

@app.route("/api/whatsapp/run-now", methods=["POST"])
def wa_run_now():
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:3000/run-now", timeout=5)
        import json as _json
        return jsonify(_json.loads(r.read()))
    except Exception as e:
        return jsonify({"error": "Bot not running. Start it first."}), 400

# ── WhatsApp QR code ─────────────────────────
@app.route("/api/whatsapp/qr")
def wa_qr():
    """Return QR data for dashboard display."""
    qr_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'wa_qr.txt')
    if os.path.exists(qr_file):
        with open(qr_file, 'r') as f:
            return jsonify({"qr": f.read().strip(), "pending": True})
    return jsonify({"qr": None, "pending": False})

# ── WhatsApp bot logs ────────────────────────
@app.route("/api/whatsapp/logs")
def wa_logs():
    """Stream latest logs from running bot."""
    try:
        import urllib.request as _ur, json as _j
        r = _ur.urlopen("http://localhost:3000/", timeout=2)
        d = _j.loads(r.read())
        return jsonify({"logs": d.get("recentLogs", []), "sentToday": d.get("sentToday", 0), "connected": True})
    except:
        return jsonify({"logs": [], "sentToday": 0, "connected": False})
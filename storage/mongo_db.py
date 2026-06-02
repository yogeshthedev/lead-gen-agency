"""
storage/mongo_db.py
MongoDB storage for leads (replacing SQLite).
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

from utils.logger import get_logger

logger = get_logger(__name__)

# MongoDB Connection
MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb+srv://user:password@cluster.mongodb.net/leadgen")
client = MongoClient(MONGO_DB_URL)
db = client.get_database('leadgen')

# Collections
leads_collection = db['leads']
email_history_collection = db['email_history']

# Map fields
DB_COLUMNS = [
    "business_name",
    "owner_contact",
    "email",
    "phone",
    "website",
    "maps_url",
    "city",
    "category",
    "source",
    "date_scraped",
    "email_status",
    "last_email_date",
    "follow_up_count",
    "notes",
    "wa_status",
    "wa_date",
    "wa_count",
    "rating",
    "review_count",
    "has_website",
    "website_quality",
    "lead_score",
    "response",
    "normalized_name",
    "social_links",
]

SHEET_TO_DB = {
    "Business Name": "business_name",
    "Owner / Contact": "owner_contact",
    "Email": "email",
    "Phone": "phone",
    "Website": "website",
    "Maps URL": "maps_url",
    "City": "city",
    "Category": "category",
    "Source": "source",
    "Date Scraped": "date_scraped",
    "Email Status": "email_status",
    "Last Email Date": "last_email_date",
    "Follow Up Count": "follow_up_count",
    "Notes": "notes",
    "WhatsApp Status": "wa_status",
    "WhatsApp Date": "wa_date",
    "WhatsApp Count": "wa_count",
    "Rating": "rating",
    "Review Count": "review_count",
    "Has Website": "has_website",
    "Website Quality": "website_quality",
    "Lead Score": "lead_score",
    "Response": "response",
    "Social Links": "social_links",
}

DB_TO_SHEET = {v: k for k, v in SHEET_TO_DB.items()}


def init_db():
    """Initialize MongoDB indexes."""
    try:
        leads_collection.create_index("email")
        leads_collection.create_index("phone")
        leads_collection.create_index("normalized_name")
        logger.info("✅ MongoDB initialized with indexes")
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")


def _normalize_name(name: str) -> str:
    return (name or "").strip().lower()[:30]


def _lead_value(lead: Dict, key: str) -> str:
    return str(lead.get(key, "") or "").strip()


def _lead_to_db_row(lead: Dict) -> Dict:
    row = {k: "" for k in DB_COLUMNS}
    for sheet_key, db_key in SHEET_TO_DB.items():
        row[db_key] = _lead_value(lead, sheet_key)
    row["normalized_name"] = _normalize_name(row.get("business_name", ""))
    return row


def lead_exists(email: str, phone: str, name: str, website: str, city: str) -> bool:
    """Check if lead already exists. Uses strict Phone/Email/Website or Name+City match."""
    import re
    email = (email or "").strip().lower()
    
    # Strictly strip phone to digits
    phone = re.sub(r'\D', '', (phone or ""))
    if phone.startswith("91") and len(phone) > 10:
        phone = phone[2:]
    elif phone.startswith("0") and len(phone) > 10:
        phone = phone[1:]
        
    website = (website or "").strip().lower()
    name_norm = _normalize_name(name)
    city_norm = (city or "").strip().lower()

    or_conditions = []
    
    if phone:
        # Match against phone in db by regex since it might have spaces in DB
        or_conditions.append({"phone": {"$regex": f"{phone}$"}})
    if email:
        or_conditions.append({"email": {"$regex": f"^{email}$", "$options": "i"}})
    if website and "google" not in website:
        or_conditions.append({"website": {"$regex": f"{website}$", "$options": "i"}})
        
    if not or_conditions:
        # Fallback to Name + City
        if name_norm and city_norm:
            or_conditions.append({
                "normalized_name": name_norm,
                "city": {"$regex": f"^{city_norm}$", "$options": "i"}
            })
        elif name_norm:
            or_conditions.append({"normalized_name": name_norm})
            
    if not or_conditions:
        return False
        
    query = {"$or": or_conditions}
    return leads_collection.find_one(query) is not None


def add_lead(lead: Dict) -> bool:
    """Add a new lead to MongoDB."""
    init_db()
    row = _lead_to_db_row(lead)

    if lead_exists(row.get("email"), row.get("phone"), row.get("business_name"), row.get("website"), row.get("city")):
        logger.info(f"Skipped duplicate: {row.get('business_name')}")
        return False

    try:
        result = leads_collection.insert_one(row)
        logger.info(f"Added: {row.get('business_name')} | {row.get('email') or row.get('phone')}")
        return True
    except Exception as e:
        logger.error(f"Error adding lead: {e}")
        return False


def _row_to_lead(row: Dict) -> Dict:
    """Convert MongoDB document to lead dict."""
    lead = {}
    for db_key, sheet_key in DB_TO_SHEET.items():
        if db_key in row:
            lead[sheet_key] = row[db_key]
    if "_id" in row:
        lead["id"] = str(row["_id"])
    return lead


def get_all_leads() -> List[Dict]:
    """Get all leads from MongoDB."""
    init_db()
    try:
        leads = list(leads_collection.find().sort("date_scraped", -1))
        return [_row_to_lead(l) for l in leads]
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        return []


def get_lead_by_id(lead_id: str) -> Optional[Dict]:
    """Get a single lead by ID."""
    try:
        lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
        return _row_to_lead(lead) if lead else None
    except Exception as e:
        logger.error(f"Error fetching lead: {e}")
        return None


def update_email_status(lead_id: str, status: str) -> bool:
    """Update email status for a lead."""
    try:
        result = leads_collection.update_one(
            {"_id": ObjectId(lead_id) if isinstance(lead_id, str) else lead_id},
            {
                "$set": {
                    "email_status": status,
                    "last_email_date": datetime.now().strftime("%Y-%m-%d")
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return False


def update_lead_fields(lead_id: str, updates: Dict) -> bool:
    """Update specific fields in a lead."""
    try:
        # Convert sheet names to DB names
        db_updates = {}
        for key, value in updates.items():
            db_key = SHEET_TO_DB.get(key, key)
            db_updates[db_key] = value

        result = leads_collection.update_one(
            {"_id": ObjectId(lead_id) if isinstance(lead_id, str) else lead_id},
            {"$set": db_updates}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating fields: {e}")
        return False


def get_leads_by_status(status: str) -> List[Dict]:
    """Get all leads with a specific email status."""
    try:
        leads = list(leads_collection.find({"email_status": status}).sort("date_scraped", -1))
        return [_row_to_lead(l) for l in leads]
    except Exception as e:
        logger.error(f"Error fetching leads by status: {e}")
        return []


def count_by_status() -> Dict[str, int]:
    """Count leads by email status."""
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$email_status",
                    "count": {"$sum": 1}
                }
            }
        ]
        result = list(leads_collection.aggregate(pipeline))
        return {item["_id"] or "not_sent": item["count"] for item in result}
    except Exception as e:
        logger.error(f"Error counting by status: {e}")
        return {}


def delete_lead(lead_id: str) -> bool:
    """Delete a lead by ID."""
    try:
        result = leads_collection.delete_one({"_id": ObjectId(lead_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        return False


def get_leads_without_email() -> List[Dict]:
    """Get all leads that don't have email addresses."""
    try:
        leads = list(leads_collection.find(
            {"$or": [{"email": ""}, {"email": None}, {"email": {"$exists": False}}]}
        ).sort("date_scraped", -1))
        return [_row_to_lead(l) for l in leads]
    except Exception as e:
        logger.error(f"Error fetching leads without email: {e}")
        return []


def get_leads_to_email() -> List[Dict]:
    """Get leads that haven't been emailed yet and have email addresses."""
    try:
        leads = list(leads_collection.find({
            "email_status": "not_sent",
            "email": {"$ne": "", "$exists": True}
        }).sort("_id", 1))
        return [_row_to_lead(l) for l in leads]
    except Exception as e:
        logger.error(f"Error fetching leads to email: {e}")
        return []


def get_leads_missing_email() -> List[Dict]:
    """Get all leads without email addresses."""
    try:
        leads = list(leads_collection.find({
            "$or": [{"email": ""}, {"email": None}, {"email": {"$exists": False}}]
        }).sort("_id", 1))
        return [_row_to_lead(l) for l in leads]
    except Exception as e:
        logger.error(f"Error fetching leads missing email: {e}")
        return []


def update_email_status(lead_id, status: str, followup_count: Optional[int] = None):
    """Update email status for a lead."""
    try:
        update_dict = {
            "email_status": status,
            "last_email_date": datetime.now().strftime("%Y-%m-%d")
        }
        if followup_count is not None:
            update_dict["follow_up_count"] = int(followup_count)

        # Handle both ObjectId strings and raw ObjectIds
        if isinstance(lead_id, str):
            query = {"_id": ObjectId(lead_id)}
        else:
            query = {"_id": lead_id}

        result = leads_collection.update_one(query, {"$set": update_dict})
        logger.info(f"Lead {lead_id} email status: {status}")
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating email status: {e}")
        return False


def get_leads_for_followup(days_ago: int) -> List[Dict]:
    """Get leads for follow-up from a specific number of days ago."""
    try:
        target_date = (datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        leads = list(leads_collection.find({
            "email_status": {"$in": ["sent", "follow_up"]},
            "last_email_date": target_date,
            "email": {"$ne": "", "$exists": True}
        }).sort("_id", 1))

        results = []
        for lead in leads:
            followup_count = int(lead.get("follow_up_count") or 0)
            if followup_count < 3:
                results.append(_row_to_lead(lead))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching leads for followup: {e}")
        return []


def get_leads_for_whatsapp() -> List[Dict]:
    """Get leads that are ready for WhatsApp outreach."""
    try:
        from datetime import timedelta as _timedelta
        
        leads = list(leads_collection.find({}).sort("_id", 1))
        result = []

        for lead in leads:
            phone = str(lead.get("phone") or "").strip()
            name = str(lead.get("business_name") or "").strip()
            wa_status = str(lead.get("wa_status") or "").strip()
            wa_date = str(lead.get("wa_date") or "").strip()
            wa_count = int(lead.get("wa_count") or 0)

            if not phone or not name:
                continue
            if wa_status == "wa_done":
                continue

            if not wa_status:
                result.append((_row_to_lead(lead), 0))
            elif wa_status == "wa_sent":
                try:
                    days_since = (datetime.now() - datetime.strptime(wa_date, "%Y-%m-%d")).days
                    if days_since >= 3 and wa_count < 3:
                        result.append((_row_to_lead(lead), wa_count + 1))
                except:
                    pass

        return result
    except Exception as e:
        logger.error(f"Error fetching leads for WhatsApp: {e}")
        return []




def add_email_record(lead_id: str, subject: str, body: str, email_type: str, status: str = "sent"):
    """Record a sent email in history."""
    try:
        record = {
            "lead_id": lead_id,
            "subject": subject,
            "body": body,
            "type": email_type,
            "status": status,
            "sent_at": datetime.now().isoformat()
        }
        email_history_collection.insert_one(record)
        return True
    except Exception as e:
        logger.error(f"Error adding email record: {e}")
        return False

def get_email_history(lead_id: str) -> List[Dict]:
    """Get all past emails for a lead."""
    try:
        cursor = email_history_collection.find({"lead_id": lead_id}).sort("sent_at", -1)
        history = list(cursor)
        for h in history:
            h["_id"] = str(h["_id"])
        return history
    except Exception as e:
        logger.error(f"Error fetching email history: {e}")
        return []

def get_lead_email_thread(lead_id: str) -> List[Dict]:
    """Get chronological email history."""
    try:
        cursor = email_history_collection.find({"lead_id": lead_id}).sort("sent_at", 1)
        history = list(cursor)
        for h in history:
            h["_id"] = str(h["_id"])
        return history
    except Exception as e:
        logger.error(f"Error fetching email thread: {e}")
        return []

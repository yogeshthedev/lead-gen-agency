/**
 * sheets.js
 * (Renamed from Google Sheets adapter to MongoDB adapter)
 * Reads leads from MongoDB and updates their WhatsApp status.
 */

const { MongoClient, ObjectId } = require("mongodb");
require("dotenv").config({ path: "../.env" });

const MONGO_DB_URL = process.env.MONGO_DB_URL;
let dbInstance = null;

async function getDB() {
  if (dbInstance) return dbInstance;
  const client = new MongoClient(MONGO_DB_URL);
  await client.connect();
  dbInstance = client.db('leadgen');
  return dbInstance;
}

/**
 * Get leads ready for WhatsApp outreach.
 * Returns leads where:
 * - Phone number exists
 * - WhatsApp Status is empty (not sent yet) OR due for follow-up
 */
async function getLeadsForWhatsApp() {
  const db = await getDB();
  const rows = await db.collection('leads').find({}).toArray();
  
  const leads = [];
  const today = new Date().toISOString().split("T")[0];

  rows.forEach((row) => {
    const phone    = (row.phone || "").trim();
    const name     = (row.business_name || "").trim();
    const city     = (row.city || "").trim();
    const category = (row.category || "").trim();
    const waStatus = (row.wa_status || "").trim();
    const waDate   = (row.wa_date || "").trim();
    const waCount  = parseInt(row.wa_count || "0", 10);

    if (!phone || !name) return;

    // Skip if already completed all follow-ups
    if (waStatus === "wa_done") return;

    // First message — never contacted
    if (!waStatus || waStatus === "") {
      leads.push({ rowIndex: row._id.toString(), name, phone, city, category, waCount: 0 });
      return;
    }

    // Follow-up logic — contact again after N days
    if (waStatus === "wa_sent" && waDate) {
      const sentDate  = new Date(waDate);
      const daysSince = Math.floor((new Date() - sentDate) / (1000 * 60 * 60 * 24));
      const schedule  = [0, 4, 8]; // day 0, day 4, day 8

      if (waCount < 2 && daysSince >= schedule[waCount + 1]) {
        leads.push({ rowIndex: row._id.toString(), name, phone, city, category, waCount: waCount + 1 });
      }
    }
  });

  return leads;
}

/**
 * Update WhatsApp status for a lead after sending.
 */
async function updateWhatsAppStatus(rowIndex, status, count) {
  const db = await getDB();
  const today  = new Date().toISOString().split("T")[0];

  await db.collection('leads').updateOne(
    { _id: new ObjectId(rowIndex) },
    { $set: { wa_status: status, wa_date: today, wa_count: count } }
  );

  console.log(`[MongoDB] Lead ${rowIndex} → ${status} (count: ${count})`);
}

/**
 * No-op for MongoDB (kept for compatibility with bot.js)
 */
async function ensureWhatsAppHeaders() {
  // Not needed for MongoDB
  console.log("[MongoDB] Database connected successfully.");
}

module.exports = { getLeadsForWhatsApp, updateWhatsAppStatus, ensureWhatsAppHeaders };

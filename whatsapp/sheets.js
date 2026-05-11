/**
 * sheets.js
 * Read leads from Google Sheets and update their WhatsApp status.
 */

const { google } = require("googleapis");
require("dotenv").config({ path: "../.env" });

const SHEET_ID   = process.env.GOOGLE_SHEET_ID;
const CREDS_FILE = "../credentials.json";

// Column indices (0-based)
const COL = {
  NAME:        0,   // A - Business Name
  CONTACT:     1,   // B - Owner/Contact
  EMAIL:       2,   // C - Email
  PHONE:       3,   // D - Phone
  WEBSITE:     4,   // E - Website
  MAPS_URL:    5,   // F - Maps URL
  CITY:        6,   // G - City
  CATEGORY:    7,   // H - Category
  SOURCE:      8,   // I - Source
  DATE:        9,   // J - Date Scraped
  STATUS:      10,  // K - Email Status
  LAST_DATE:   11,  // L - Last Email Date
  FOLLOWUP:    12,  // M - Follow Up Count
  NOTES:       13,  // N - Notes
  WA_STATUS:   14,  // O - WhatsApp Status  ← new column
  WA_DATE:     15,  // P - WhatsApp Date    ← new column
  WA_COUNT:    16,  // Q - WhatsApp Count   ← new column
};

async function getAuthClient() {
  const auth = new google.auth.GoogleAuth({
    keyFile: CREDS_FILE,
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
  return auth.getClient();
}

async function getSheetData() {
  const auth   = await getAuthClient();
  const sheets = google.sheets({ version: "v4", auth });
  const res    = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: "Sheet1!A2:Q",   // skip header row
  });
  return res.data.values || [];
}

/**
 * Get leads ready for WhatsApp outreach.
 * Returns leads where:
 * - Phone number exists
 * - WhatsApp Status is empty (not sent yet) OR due for follow-up
 */
async function getLeadsForWhatsApp() {
  const rows  = await getSheetData();
  const leads = [];
  const today = new Date().toISOString().split("T")[0];

  rows.forEach((row, i) => {
    const phone    = (row[COL.PHONE]     || "").trim();
    const name     = (row[COL.NAME]      || "").trim();
    const city     = (row[COL.CITY]      || "").trim();
    const category = (row[COL.CATEGORY]  || "").trim();
    const waStatus = (row[COL.WA_STATUS] || "").trim();
    const waDate   = (row[COL.WA_DATE]   || "").trim();
    const waCount  = parseInt(row[COL.WA_COUNT] || "0");

    if (!phone || !name) return;

    // Skip if already completed all follow-ups
    if (waStatus === "wa_done") return;

    // First message — never contacted
    if (!waStatus || waStatus === "") {
      leads.push({ rowIndex: i + 2, name, phone, city, category, waCount: 0 });
      return;
    }

    // Follow-up logic — contact again after N days
    if (waStatus === "wa_sent" && waDate) {
      const sentDate  = new Date(waDate);
      const daysSince = Math.floor((new Date() - sentDate) / (1000 * 60 * 60 * 24));
      const schedule  = [0, 4, 8]; // day 0, day 4, day 8

      if (waCount < 2 && daysSince >= schedule[waCount + 1]) {
        leads.push({ rowIndex: i + 2, name, phone, city, category, waCount: waCount + 1 });
      }
    }
  });

  return leads;
}

/**
 * Update WhatsApp status for a lead after sending.
 */
async function updateWhatsAppStatus(rowIndex, status, count) {
  const auth   = await getAuthClient();
  const sheets = google.sheets({ version: "v4", auth });
  const today  = new Date().toISOString().split("T")[0];

  // Update columns O, P, Q
  await sheets.spreadsheets.values.update({
    spreadsheetId: SHEET_ID,
    range: `Sheet1!O${rowIndex}:Q${rowIndex}`,
    valueInputOption: "RAW",
    requestBody: {
      values: [[status, today, count]],
    },
  });

  console.log(`[Sheets] Row ${rowIndex} → ${status} (count: ${count})`);
}

/**
 * Ensure WhatsApp columns exist in header row.
 */
async function ensureWhatsAppHeaders() {
  const auth   = await getAuthClient();
  const sheets = google.sheets({ version: "v4", auth });

  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: "Sheet1!O1:Q1",
  });

  const existing = (res.data.values || [[]])[0] || [];
  if (!existing.includes("WhatsApp Status")) {
    await sheets.spreadsheets.values.update({
      spreadsheetId: SHEET_ID,
      range: "Sheet1!O1:Q1",
      valueInputOption: "RAW",
      requestBody: {
        values: [["WhatsApp Status", "WhatsApp Date", "WhatsApp Count"]],
      },
    });
    console.log("[Sheets] WhatsApp columns added to header.");
  }
}

module.exports = { getLeadsForWhatsApp, updateWhatsAppStatus, ensureWhatsAppHeaders };

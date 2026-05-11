/**
 * bot.js — WhatsApp outreach bot
 * 
 * How it works:
 * 1. Scan QR code once with your phone
 * 2. Bot reads leads from Google Sheets
 * 3. Sends 30 personalised messages per day
 * 4. Waits 15-20 minutes between each message
 * 5. Updates Sheets after each send
 * 6. Runs 24/7 on Railway (free hosting)
 * 
 * Run: node bot.js
 */

require("dotenv").config({ path: "../.env" });
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode                = require("qrcode-terminal");
const express               = require("express");
const { getMessage }        = require("./templates");
const { getLeadsForWhatsApp, updateWhatsAppStatus, ensureWhatsAppHeaders } = require("./sheets");

// ── Config ──────────────────────────────────────────────
const YOUR_NAME       = process.env.YOUR_NAME    || "Yogesh";
const BOT_PORT        = parseInt(process.env.WA_BOT_PORT || "3000", 10);
const DAILY_LIMIT     = 30;                        // max messages per day
const DELAY_MIN_MS    = 15 * 60 * 1000;           // 15 minutes minimum
const DELAY_MAX_MS    = 22 * 60 * 1000;           // 22 minutes maximum
const START_HOUR      = 9;                         // don't send before 9am
const STOP_HOUR       = 20;                        // don't send after 8pm
const RUN_HOUR        = 9;                         // start sending at 9am daily

// ── State ────────────────────────────────────────────────
let isReady      = false;
let sentToday    = 0;
let lastRunDate  = "";
let isSending    = false;
let statusLog    = [];

function log(msg) {
  const line = `[${new Date().toLocaleTimeString("en-IN")}] ${msg}`;
  console.log(line);
  statusLog.push(line);
  if (statusLog.length > 100) statusLog = statusLog.slice(-100);
}

// ── WhatsApp Client ──────────────────────────────────────
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./session" }),
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-accelerated-2d-canvas",
      "--no-first-run",
      "--no-zygote",
      "--single-process",
      "--disable-gpu",
      "--disable-ipv6",
    ],
  },
});

// QR code — scan this with your phone once
const fs = require("fs");
const path = require("path");

client.on("qr", (qr) => {
  log("QR code generated — scan with WhatsApp on your phone:");
  qrcode.generate(qr, { small: true });
  // Save QR data so Flask dashboard can display it
  try {
    const qrFile = path.join(__dirname, "..", "data", "wa_qr.txt");
    fs.writeFileSync(qrFile, qr, "utf8");
    log("QR saved for dashboard display.");
  } catch(e) {}
  log("After scanning, the bot will start automatically.");
});

client.on("ready", async () => {
  isReady = true;
  log("WhatsApp connected! Bot is ready.");
  // Clear QR file
  try { const fs2 = require("fs"); fs2.unlinkSync(path.join(__dirname, "..", "data", "wa_qr.txt")); } catch(e) {}
  await ensureWhatsAppHeaders();
  scheduleDaily();
});

client.on("disconnected", (reason) => {
  isReady = false;
  log(`WhatsApp disconnected: ${reason}. Reconnecting...`);
  client.initialize();
});

client.on("auth_failure", () => {
  log("Auth failed — delete ./session folder and restart to re-scan QR.");
});

// ── Helpers ──────────────────────────────────────────────
function randomDelay(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function isWorkingHours() {
  const h = new Date().getHours();
  return h >= START_HOUR && h < STOP_HOUR;
}

function formatPhone(phone) {
  // Remove all non-digits
  let clean = phone.replace(/\D/g, "");
  // Add India country code if not present
  if (clean.length === 10) clean = "91" + clean;
  if (clean.startsWith("0"))  clean = "91" + clean.slice(1);
  return clean + "@c.us";  // WhatsApp ID format
}

// ── Core send function ───────────────────────────────────
async function sendMessage(lead) {
  const { rowIndex, name, phone, city, category, waCount } = lead;

  try {
    const chatId  = formatPhone(phone);
    const message = getMessage(category, waCount, name, city, YOUR_NAME);

    log(`Sending to ${name} (${phone}) [${category}] follow-up #${waCount}`);

    // Check if number exists on WhatsApp
    const isRegistered = await client.isRegisteredUser(chatId);
    if (!isRegistered) {
      log(`  ${name} — not on WhatsApp, skipping.`);
      await updateWhatsAppStatus(rowIndex, "wa_not_found", waCount);
      return false;
    }

    await client.sendMessage(chatId, message);
    log(`  Sent to ${name} ✓`);

    const newCount  = waCount + 1;
    const newStatus = newCount >= 3 ? "wa_done" : "wa_sent";
    await updateWhatsAppStatus(rowIndex, newStatus, newCount);
    sentToday++;
    return true;

  } catch (err) {
    log(`  Error sending to ${name}: ${err.message}`);
    return false;
  }
}

// ── Daily outreach runner ────────────────────────────────
async function runDailyOutreach() {
  const today = new Date().toISOString().split("T")[0];

  // Reset counter on new day
  if (lastRunDate !== today) {
    sentToday   = 0;
    lastRunDate = today;
    log(`New day — counter reset. Date: ${today}`);
  }

  if (!isReady) { log("WhatsApp not ready yet."); return; }
  if (isSending) { log("Already sending — skipping."); return; }
  if (!isWorkingHours()) { log("Outside working hours — skipping."); return; }
  if (sentToday >= DAILY_LIMIT) { log(`Daily limit reached (${DAILY_LIMIT}). Will resume tomorrow.`); return; }

  isSending = true;
  log(`Starting daily outreach. Sent today: ${sentToday}/${DAILY_LIMIT}`);

  try {
    const leads = await getLeadsForWhatsApp();
    log(`Leads ready for WhatsApp: ${leads.length}`);

    if (!leads.length) {
      log("No leads to message today.");
      isSending = false;
      return;
    }

    for (const lead of leads) {
      if (sentToday >= DAILY_LIMIT) {
        log(`Daily limit (${DAILY_LIMIT}) reached. Stopping for today.`);
        break;
      }

      if (!isWorkingHours()) {
        log("Outside working hours. Will continue tomorrow.");
        break;
      }

      const success = await sendMessage(lead);

      if (success) {
        // Wait 15-22 minutes between messages — looks human, avoids ban
        const waitMs = randomDelay(DELAY_MIN_MS, DELAY_MAX_MS);
        const waitMin = Math.round(waitMs / 60000);
        log(`Waiting ${waitMin} minutes before next message...`);
        await new Promise(r => setTimeout(r, waitMs));
      } else {
        // Short wait even on failure
        await new Promise(r => setTimeout(r, 5000));
      }
    }

  } catch (err) {
    log(`Outreach error: ${err.message}`);
  }

  isSending = false;
  log(`Outreach session done. Total sent today: ${sentToday}`);
}

// ── Scheduler — run daily at 9am ─────────────────────────
function scheduleDaily() {
  log("Scheduler started. Will send messages at 9am daily.");

  // Check every minute if it's time to run
  setInterval(() => {
    const now = new Date();
    const h   = now.getHours();
    const m   = now.getMinutes();

    // Run at 9:00am daily
    if (h === RUN_HOUR && m === 0) {
      log("9:00am — starting daily outreach...");
      runDailyOutreach();
    }
  }, 60 * 1000);

  // Also run immediately if it's already working hours and nothing sent yet
  if (isWorkingHours() && sentToday === 0) {
    log("Working hours detected — running outreach now...");
    setTimeout(runDailyOutreach, 5000);
  }
}

// ── HTTP status server ───────────────────────────────────
// Keeps Railway server alive + shows bot status
const app = express();

// Allow requests from dashboard
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type");
  next();
});

app.get("/", (req, res) => {
  res.json({
    status:      isReady ? "connected" : "disconnected",
    sentToday,
    dailyLimit:  DAILY_LIMIT,
    isSending,
    lastRunDate,
    recentLogs:  statusLog.slice(-20),
  });
});

app.get("/run-now", async (req, res) => {
  if (!isReady) return res.json({ error: "WhatsApp not connected" });
  log("Manual run triggered via /run-now");
  runDailyOutreach();
  res.json({ message: "Outreach started manually." });
});

const statusServer = app.listen(BOT_PORT, () => {
  log(`Status server running on port ${BOT_PORT}`);
});

statusServer.on("error", (err) => {
  if (err && err.code === "EADDRINUSE") {
    log(`Port ${BOT_PORT} is already in use. Another bot process is likely running.`);
    log("Stop the old process first, then start bot again.");
    process.exit(1);
  }
  throw err;
});

// ── Start ────────────────────────────────────────────────
log("Starting WhatsApp bot...");

let _initRetryTimer = null;

function scheduleReinit(reason) {
  if (_initRetryTimer) return;
  log(`Init failed: ${reason}`);
  log("Retrying WhatsApp initialization in 15 seconds...");
  _initRetryTimer = setTimeout(() => {
    _initRetryTimer = null;
    startClient();
  }, 15000);
}

function startClient() {
  client.initialize().catch((err) => {
    scheduleReinit(err && err.message ? err.message : String(err));
  });
}

process.on("unhandledRejection", (err) => {
  scheduleReinit(err && err.message ? err.message : String(err));
});

startClient();
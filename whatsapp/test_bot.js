/**
 * test_bot.js
 * Tests WITHOUT connecting to WhatsApp.
 * Checks: Sheets connection, message templates, phone formatting.
 * Run: node test_bot.js
 */

require("dotenv").config({ path: "../.env" });
const { getMessage }        = require("./templates");
const { getLeadsForWhatsApp, ensureWhatsAppHeaders } = require("./sheets");

function formatPhone(phone) {
  let clean = phone.replace(/\D/g, "");
  if (clean.length === 10) clean = "91" + clean;
  if (clean.startsWith("0"))  clean = "91" + clean.slice(1);
  return clean + "@c.us";
}

async function runTest() {
  console.log("=" .repeat(55));
  console.log("WhatsApp Bot — Pre-flight Test");
  console.log("=".repeat(55));

  // Test 1: Templates
  console.log("\n[1] Template preview — chartered accountants:\n");
  const msg = getMessage("chartered accountants", 0, "Goyal & Co", "Jaipur", process.env.YOUR_NAME || "Yogesh");
  console.log(msg);

  console.log("\n[2] Template preview — restaurants:\n");
  const msg2 = getMessage("restaurants", 0, "Cafe 99", "Jaipur", process.env.YOUR_NAME || "Yogesh");
  console.log(msg2);

  // Test 2: Phone formatting
  console.log("\n[3] Phone formatting:");
  ["9876543210", "09876543210", "919876543210"].forEach(p => {
    console.log(`  ${p} → ${formatPhone(p)}`);
  });

  // Test 3: Sheets connection
  console.log("\n[4] Google Sheets connection...");
  try {
    await ensureWhatsAppHeaders();
    console.log("  Headers OK");
    const leads = await getLeadsForWhatsApp();
    console.log(`  Found ${leads.length} leads ready for WhatsApp`);
    if (leads.length > 0) {
      console.log(`\n  First 3 leads:`);
      leads.slice(0, 3).forEach(l => {
        console.log(`    - ${l.name} | ${l.phone} | ${l.category}`);
      });
    }
  } catch (e) {
    console.log(`  Sheets error: ${e.message}`);
  }

  console.log("\n" + "=".repeat(55));
  console.log("Test done. If Sheets shows leads above,");
  console.log("run: node bot.js  and scan the QR code.");
  console.log("=".repeat(55));
}

runTest();

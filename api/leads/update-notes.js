const { MongoClient, ObjectId } = require('mongodb');
require('dotenv').config();

let cachedClient = null;

async function connectDB() {
  if (cachedClient) {
    return cachedClient;
  }
  
  const client = new MongoClient(process.env.MONGO_DB_URL);
  await client.connect();
  cachedClient = client;
  return client;
}

async function syncToGoogleSheets(db) {
  try {
    console.log('🔄 Starting sheet sync...');
    
    if (!process.env.GOOGLE_SHEET_ID) {
      throw new Error('GOOGLE_SHEET_ID not set');
    }
    if (!process.env.GOOGLE_CREDENTIALS_JSON) {
      throw new Error('GOOGLE_CREDENTIALS_JSON not set');
    }

    const { google } = require('googleapis');
    let credentials;
    
    try {
      credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS_JSON);
      console.log('✅ Credentials parsed');
    } catch (parseErr) {
      throw new Error(`Invalid GOOGLE_CREDENTIALS_JSON: ${parseErr.message}`);
    }
    
    const auth = new google.auth.GoogleAuth({
      credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
    });

    const sheets = google.sheets({ version: 'v4', auth });
    console.log('✅ Auth initialized');
    
    const leads = await db.collection('leads').find({}).toArray();
    console.log(`✅ Fetched ${leads.length} leads from MongoDB`);

    const values = [
      ['Business Name', 'Owner / Contact', 'Email', 'Phone', 'Website', 'Maps URL', 'City', 'Category', 'Source', 'Date Scraped', 'Email Status', 'Last Email Date', 'Follow Up Count', 'Notes', 'Rating', 'Review Count', 'Lead Score', 'Response'],
      ...leads.map(l => [
        l.business_name || '',
        l.owner_contact || '',
        l.email || '',
        l.phone || '',
        l.website || '',
        l.maps_url || '',
        l.city || '',
        l.category || '',
        l.source || '',
        l.date_scraped || '',
        l.email_status || '',
        l.last_email_date || '',
        l.follow_up_count || 0,
        l.notes || '',
        l.rating || '',
        l.review_count || '',
        l.lead_score || 0,
        l.response || 'new'
      ])
    ];

    console.log(`📝 Updating sheet with ${values.length} rows (1 header + ${leads.length} leads)`);

    const updateRes = await sheets.spreadsheets.values.update({
      spreadsheetId: process.env.GOOGLE_SHEET_ID,
      range: 'Sheet1!A1',
      valueInputOption: 'RAW',
      requestBody: { values }
    });

    console.log(`✅ Synced to Google Sheets: ${updateRes.data.updatedRows} rows updated`);
  } catch (err) {
    console.error('❌ Sheet sync failed:', err.message);
    throw err;
  }
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { lead_id, notes } = req.body;

    if (!lead_id) {
      return res.status(400).json({ error: 'lead_id required' });
    }

    const client = await connectDB();
    const db = client.db('leadgen');

    const result = await db.collection('leads').updateOne(
      { _id: new ObjectId(lead_id) },
      { $set: { notes: notes || '' } }
    );

    if (result.matchedCount === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    console.log(`✅ Updated notes for lead ${lead_id}`);
    
    if (process.env.GOOGLE_SHEET_ID && process.env.GOOGLE_CREDENTIALS_JSON) {
      try {
        await syncToGoogleSheets(db);
        console.log('✅ Sheet sync completed');
        return res.status(200).json({ ok: true, synced: true });
      } catch (syncErr) {
        console.error('Sheet sync error:', syncErr.message);
        return res.status(200).json({ ok: true, synced: false, syncError: syncErr.message });
      }
    } else {
      console.warn('Sheet sync skipped: missing GOOGLE_SHEET_ID or GOOGLE_CREDENTIALS_JSON');
      return res.status(200).json({ ok: true, synced: false, reason: 'Missing sheet credentials' });
    }
  } catch (err) {
    console.error('Error updating notes:', err);
    res.status(500).json({ error: err.message });
  }
};

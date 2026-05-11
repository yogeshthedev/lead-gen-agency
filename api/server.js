const express = require('express');
const cors = require('cors');
const { MongoClient, ObjectId } = require('mongodb');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const MONGO_DB_URL = process.env.MONGO_DB_URL;
let db;
let dbConnectPromise = null;

const connectDB = async () => {
  try {
    const client = new MongoClient(MONGO_DB_URL);
    await client.connect();
    db = client.db('leadgen');
    console.log('✅ Connected to MongoDB');
    
    // Create indexes
    await db.collection('leads').createIndex({ email: 1 });
    await db.collection('leads').createIndex({ phone: 1 });
    await db.collection('leads').createIndex({ normalized_name: 1 });
    
    return client;
  } catch (err) {
    console.error('❌ MongoDB connection failed:', err);
    throw err;
  }
};

const ensureDB = async () => {
  if (db) return;
  if (!dbConnectPromise) {
    dbConnectPromise = connectDB();
  }
  await dbConnectPromise;
};

app.use(async (req, res, next) => {
  try {
    await ensureDB();
    next();
  } catch (err) {
    res.status(500).json({ error: 'Database connection failed' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ ok: true, db: db ? 'connected' : 'disconnected' });
});

// Get all leads with filters
app.get('/api/leads', async (req, res) => {
  try {
    const {
      min_score,
      max_score,
      min_reviews,
      max_reviews,
      has_website,
      status
    } = req.query;

    let filter = { business_name: { $exists: true, $ne: '' } };

    // Apply filters
    if (min_score) filter.lead_score = { ...filter.lead_score, $gte: parseInt(min_score) };
    if (max_score) filter.lead_score = { ...filter.lead_score, $lte: parseInt(max_score) };
    
    if (min_reviews) filter.review_count = { ...filter.review_count, $gte: parseInt(min_reviews) };
    if (max_reviews) filter.review_count = { ...filter.review_count, $lte: parseInt(max_reviews) };
    
    if (has_website !== undefined) {
      filter.has_website = has_website === 'true' ? 'yes' : 'no';
    }

    if (status) {
      filter.email_status = status;
    }

    const leads = await db.collection('leads')
      .find(filter)
      .sort({ date_scraped: -1 })
      .toArray();

    res.json({ leads: leads || [] });
  } catch (err) {
    console.error('Error fetching leads:', err);
    res.status(500).json({ error: err.message });
  }
});

// Get lead stats
app.get('/api/leads/stats', async (req, res) => {
  try {
    const leads = await db.collection('leads').find({}).toArray();

    const stats = {
      total: leads.length,
      has_email: leads.filter(l => l.email && l.email.trim()).length,
      not_sent: 0,
      sent: 0,
      follow_up: 0,
      replied: 0,
      interested: 0,
      not_interested: 0,
      closed: 0,
      failed: 0,
      by_source: {},
      by_category: {},
      by_day: {}
    };

    leads.forEach(lead => {
      const status = lead.email_status || 'not_sent';
      if (status in stats) stats[status]++;

      const source = lead.source || '';
      if (source) stats.by_source[source] = (stats.by_source[source] || 0) + 1;

      const category = lead.category || '';
      if (category) stats.by_category[category] = (stats.by_category[category] || 0) + 1;

      const day = lead.date_scraped || '';
      if (day) stats.by_day[day] = (stats.by_day[day] || 0) + 1;
    });

    res.json(stats);
  } catch (err) {
    console.error('Error fetching stats:', err);
    res.status(500).json({ error: err.message });
  }
});

async function syncSheetsIfEnabled() {
  if (!process.env.GOOGLE_SHEET_ID) return;
  await syncToGoogleSheets();
}

// Update lead status
app.post('/api/leads/update-status', async (req, res) => {
  try {
    const { lead_id, status } = req.body;

    if (!lead_id || !status) {
      return res.status(400).json({ error: 'lead_id and status required' });
    }

    const result = await db.collection('leads').updateOne(
      { _id: new ObjectId(lead_id) },
      {
        $set: {
          email_status: status,
          last_email_date: new Date().toISOString().split('T')[0]
        }
      }
    );

    if (result.modifiedCount === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    await syncSheetsIfEnabled();
    res.json({ ok: true });
  } catch (err) {
    console.error('Error updating status:', err);
    res.status(500).json({ error: err.message });
  }
});

// Update lead notes
app.post('/api/leads/update-notes', async (req, res) => {
  try {
    const { lead_id, notes } = req.body;

    if (!lead_id) {
      return res.status(400).json({ error: 'lead_id required' });
    }

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
        await syncToGoogleSheets();
        console.log('✅ Sheet sync completed');
        res.json({ ok: true, synced: true });
      } catch (syncErr) {
        console.error('Sheet sync error:', syncErr.message);
        res.json({ ok: true, synced: false, syncError: syncErr.message });
      }
    } else {
      console.warn('Sheet sync skipped: missing GOOGLE_SHEET_ID or GOOGLE_CREDENTIALS_JSON');
      res.json({ ok: true, synced: false, reason: 'Missing sheet credentials' });
    }
  } catch (err) {
    console.error('Error updating notes:', err);
    res.status(500).json({ error: err.message });
  }
});

// Update lead response value
app.post('/api/leads/update-response', async (req, res) => {
  try {
    const { lead_id, response } = req.body;

    if (!lead_id) {
      return res.status(400).json({ error: 'lead_id required' });
    }

    const result = await db.collection('leads').updateOne(
      { _id: new ObjectId(lead_id) },
      { $set: { response: response || 'new' } }
    );

    if (result.matchedCount === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    await syncSheetsIfEnabled();
    res.json({ ok: true });
  } catch (err) {
    console.error('Error updating response:', err);
    res.status(500).json({ error: err.message });
  }
});

// Update any lead field
app.post('/api/leads/update', async (req, res) => {
  try {
    const { lead_id, updates } = req.body;

    if (!lead_id || !updates) {
      return res.status(400).json({ error: 'lead_id and updates required' });
    }

    const result = await db.collection('leads').updateOne(
      { _id: new ObjectId(lead_id) },
      { $set: updates }
    );

    if (result.matchedCount === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    await syncSheetsIfEnabled();
    res.json({ ok: true });
  } catch (err) {
    console.error('Error updating lead:', err);
    res.status(500).json({ error: err.message });
  }
});

// Google Sheets Sync function
async function syncToGoogleSheets() {
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

if (require.main === module) {
  connectDB().then(() => {
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  });
}

module.exports = app;

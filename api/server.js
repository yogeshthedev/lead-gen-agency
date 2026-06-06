const express = require('express');
const cors = require('cors');
const { MongoClient, ObjectId } = require('mongodb');
const path = require('path');
const { spawn, exec } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve frontend statically
app.use(express.static(path.join(__dirname, '../frontend/dist')));

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
  // await syncToGoogleSheets();
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

    console.log(`Updated notes for lead ${lead_id}`);
    await syncSheetsIfEnabled();
    res.json({ ok: true });
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





// Generate WhatsApp Deep Link
app.post('/api/leads/send-whatsapp', async (req, res) => {
  try {
    const { lead_id, custom_message } = req.body;
    if (!lead_id) return res.status(400).json({ error: 'lead_id required' });

    const lead = await db.collection('leads').findOne({ _id: new ObjectId(lead_id) });
    if (!lead || !lead.phone) return res.status(404).json({ error: 'Lead not found or missing phone' });

    // Format phone
    let phone = lead.phone.replace(/\D/g, "");
    if (phone.length === 10) phone = "91" + phone;
    if (phone.startsWith("0")) phone = "91" + phone.slice(1);

    const msg = custom_message || `Hi ${lead.business_name}, I was hoping to chat with you about...`;
    const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;

    // Optional: mark as contacted in DB
    await db.collection('leads').updateOne(
      { _id: new ObjectId(lead_id) },
      { $set: { wa_status: 'wa_sent', wa_date: new Date().toISOString().split('T')[0] } }
    );

    res.json({ ok: true, url });
  } catch (err) {
    console.error('Error with WhatsApp:', err);
    res.status(500).json({ error: err.message });
  }
});

// ── Outreach API ────────────────────────────────────────

app.get('/api/leads/:id/template', async (req, res) => {
  try {
    const lead = await db.collection('leads').findOne({ _id: new ObjectId(req.params.id) });
    if (!lead) return res.status(404).json({ error: 'Lead not found' });

    const followUpCount = parseInt(lead.follow_up_count || "0", 10);
    const waCount = parseInt(lead.wa_count || "0", 10);

    // Get WhatsApp Template (JS)
    const { getMessage } = require('../whatsapp/templates');
    const waMessage = getMessage(
      lead.category || '',
      waCount,
      lead.business_name || '',
      lead.city || '',
      process.env.YOUR_NAME || 'Yogesh'
    );

    res.json({
      whatsapp: waMessage
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});




// Settings API
app.get('/api/settings', async (req, res) => {
  try {
    let settings = await db.collection('settings').findOne({ _id: 'global' });
    if (!settings) {
      settings = { 
        _id: 'global', 
        your_name: process.env.YOUR_NAME || 'Your Name', 
        your_cal_link: process.env.YOUR_CAL_LINK || 'https://cal.com/yourname',
        wa_default_msg: 'Hi {name},\n\nI was looking up your business and noticed...'
      };
      await db.collection('settings').insertOne(settings);
    }
    res.json(settings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/settings', async (req, res) => {
  try {
    const { your_name, your_cal_link, wa_default_msg } = req.body;
    await db.collection('settings').updateOne(
      { _id: 'global' },
      { $set: { your_name, your_cal_link, wa_default_msg } },
      { upsert: true }
    );
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});



// Browser UI Scraper API
let scrapingProcess = null;
let scrapeLogs = [];

app.post('/api/scrape/start', (req, res) => {
  if (scrapingProcess) return res.status(400).json({error: 'Scraping is already in progress. Please wait for it to finish.'});
  
  const { city, business, source, max_leads, website_filter } = req.body;
  if (!city || !business || !source || !max_leads) {
    return res.status(400).json({error: 'Missing parameters'});
  }
  
  const wsFilter = website_filter || 'all';
  scrapeLogs = [{type: 'i', msg: `Starting scrape job for ${business} in ${city} via ${source} (Website: ${wsFilter})...`}];
  
  try {
    const pyPath = path.join(__dirname, '..', '.venv_linux', 'bin', 'python');
    const pythonExecutable = require('fs').existsSync(pyPath) ? pyPath : 'python';
    
    const args = ['scraper/run_scrapers.py', city, business, source, max_leads.toString(), wsFilter];
    
    scrapingProcess = spawn(pythonExecutable, args, {
      cwd: path.join(__dirname, '..'),
      env: process.env
    });
    
    scrapingProcess.stdout.on('data', (data) => {
      const lines = data.toString().split('\n').filter(Boolean);
      lines.forEach(l => {
        scrapeLogs.push({type: 'i', msg: l});
        console.log(`Scraper: ${l}`);
      });
    });
    
    scrapingProcess.stderr.on('data', (data) => {
      const lines = data.toString().split('\n').filter(Boolean);
      lines.forEach(l => {
        scrapeLogs.push({type: 'e', msg: l});
        console.error(`Scraper Err: ${l}`);
      });
    });
    
    scrapingProcess.on('close', (code) => {
      scrapingProcess = null;
      if (code === 0) {
        scrapeLogs.push({type: 'i', msg: '✅ SCRAPING COMPLETED SUCCESSFULLY'});
      } else {
        scrapeLogs.push({type: 'e', msg: `❌ SCRAPING FAILED WITH CODE ${code}`});
      }
    });
    
    res.json({ok: true});
  } catch (err) {
    scrapingProcess = null;
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/scrape/status', (req, res) => {
  res.json({ running: !!scrapingProcess, logs: scrapeLogs });
});

// Fallback to index.html for React Router
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});

if (require.main === module) {
  connectDB().then(() => {
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  });
}

module.exports = app;

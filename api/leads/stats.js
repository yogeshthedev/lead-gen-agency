const { MongoClient } = require('mongodb');
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

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const client = await connectDB();
    const db = client.db('leadgen');

    // Get all leads
    const leads = await db.collection('leads').find({}).toArray();
    
    const total = leads.length;
    const has_email = leads.filter(l => l.email).length;
    const sent = leads.filter(l => l.email_status === 'sent').length;
    const follow_up = leads.filter(l => l.email_status === 'follow_up').length;
    const replied = leads.filter(l => l.email_status === 'replied').length;
    const interested = leads.filter(l => l.response === 'interested').length;
    const closed = leads.filter(l => l.email_status === 'closed').length;
    const not_sent = leads.filter(l => !l.email_status || l.email_status === 'not_sent').length;

    // Group by source
    const by_source = {};
    leads.forEach(l => {
      const src = l.source || 'unknown';
      by_source[src] = (by_source[src] || 0) + 1;
    });

    // Group by category
    const by_category = {};
    leads.forEach(l => {
      const cat = l.category || 'unknown';
      by_category[cat] = (by_category[cat] || 0) + 1;
    });

    // Group by day (date_scraped)
    const by_day = {};
    leads.forEach(l => {
      const date = l.date_scraped ? l.date_scraped.split(' ')[0] : 'unknown';
      by_day[date] = (by_day[date] || 0) + 1;
    });

    res.status(200).json({
      total,
      has_email,
      sent,
      follow_up,
      replied,
      interested,
      closed,
      not_sent,
      by_source,
      by_category,
      by_day,
      email_status: {
        not_sent,
        sent,
        follow_up,
        replied
      }
    });
  } catch (err) {
    console.error('Error fetching stats:', err);
    res.status(500).json({ error: err.message });
  }
};

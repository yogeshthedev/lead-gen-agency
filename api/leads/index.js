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
    const {
      min_score,
      max_score,
      min_reviews,
      max_reviews,
      has_website,
      status
    } = req.query;

    const client = await connectDB();
    const db = client.db('leadgen');

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

    res.status(200).json({ leads: leads || [] });
  } catch (err) {
    console.error('Error fetching leads:', err);
    res.status(500).json({ error: err.message });
  }
};

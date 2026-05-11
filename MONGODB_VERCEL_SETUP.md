# MongoDB + Vercel + GitHub Pages Setup Guide

## **Complete Architecture**

```
┌─────────────────────────┐
│  GitHub Pages           │
│  (Frontend Dashboard)   │
└───────────┬─────────────┘
            │ API calls
            ▼
┌─────────────────────────┐
│  Vercel Backend         │
│  (Node.js Express)      │
└───────────┬─────────────┘
            │ reads/writes
            ▼
┌─────────────────────────┐
│  MongoDB Atlas (Cloud)  │
│  (Database)             │
└─────────────────────────┘

GitHub Actions (Python Scraper)
            │
            └──> MongoDB + Google Sheets (sync)
```

---

## **Step 1: Setup MongoDB Atlas (Free Tier)**

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a **free account** and log in
3. Create a **new project** (e.g., "LeadGen")
4. Click **Create a Deployment**
   - Provider: AWS
   - Region: closest to you
   - Tier: **M0 (Free)**
   - Cluster name: `leadgen-cluster`
5. Wait ~5 minutes for cluster to deploy

### Get Connection String:
1. Click **Connect** button
2. Choose **"Drivers"** (not "MongoDB Shell")
3. Copy the connection string:
   ```
   mongodb+srv://username:password@leadgen-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `username` and `password` with your database user credentials
5. Save this as `MONGODB_URI` - you'll need it later

---

## **Step 2: Setup Vercel Backend**

### Create Vercel Account:
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select your `lead-gen-agency` GitHub repo
5. Click **Import**

### Configure Environment Variables:
1. Before deploying, click **"Environment Variables"**
2. Add these secrets:

| Variable | Value |
|----------|-------|
| `MONGODB_URI` | Your MongoDB connection string |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID |
| `GOOGLE_CREDENTIALS_JSON` | Full contents of credentials.json |
| `BREVO_API_KEY` | Your Brevo API key |
| `FROM_EMAIL` | Your email address |
| `FROM_NAME` | Your name |

3. Click **Deploy**

### Get Your Backend URL:
- Vercel will show you a deployment URL like: `https://your-project-name.vercel.app`
- Your API endpoint is: `https://your-project-name.vercel.app/api`
- Save this URL - you'll need it for the dashboard

---

## **Step 3: Update Dashboard to Use Vercel Backend**

Edit `frontend/index.html` and find this line (~line 900):

```javascript
var API = 'http://localhost:5000/api';
```

Replace with your Vercel API URL:

```javascript
var API = 'https://your-project-name.vercel.app/api';
```

---

## **Step 4: Enable GitHub Pages (Dashboard)**

1. Go to GitHub repo **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main** → **/root**
   - Click **Save**
3. Wait ~2 minutes
4. Your dashboard will be live at: `https://your-username.github.io/lead-gen-agency/`

---

## **Step 5: Setup GitHub Actions (Scraper)**

### Add Secrets to GitHub:
1. Go to repo **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add:

| Secret | Value |
|--------|-------|
| `MONGODB_URI` | MongoDB connection string |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID |
| `GOOGLE_CREDENTIALS_JSON` | Full contents of credentials.json file |
| `BREVO_API_KEY` | Brevo API key |
| `FROM_EMAIL` | Your email |
| `FROM_NAME` | Your name |
| `YOUR_NAME` | Your full name |
| `YOUR_CAL_LINK` | Your Calendly link |
| `YOUR_WEBSITE` | Your website URL |
| `TARGET_CITY` | City to scrape (e.g., "Jaipur") |
| `TARGET_BUSINESS` | Business type (e.g., "chartered accountants") |

### Test the Workflow:
1. Go to **Actions** tab
2. Click **"Daily Lead Gen Scraper"**
3. Click **"Run workflow"** → **"Run workflow"** button
4. Watch the logs as it runs
5. Check MongoDB to verify data was saved

---

## **Step 6: Sync to Google Sheets (Automatic)**

The Vercel backend automatically syncs MongoDB to Google Sheets when you:
- Add new leads (via scraper)
- Update lead status
- Edit notes

No additional setup needed! Data syncs whenever it changes.

---

## **How It Works Together**

1. **GitHub Actions** (daily at 9 AM UTC):
   - Runs Python scraper
   - Saves leads to MongoDB
   - Automatically syncs to Google Sheets

2. **Vercel Backend** (always online):
   - Serves API for dashboard edits
   - Updates MongoDB when you change lead data
   - Syncs changes to Google Sheets

3. **GitHub Pages Dashboard** (always accessible):
   - Shows leads from MongoDB
   - Let's you edit status, notes, etc.
   - Works on any device (phone, tablet, desktop)

---

## **Troubleshooting**

### Dashboard shows "Cannot reach API"
- Check that your Vercel API URL is correct in `frontend/index.html`
- Verify Vercel is deployed (check vercel.com dashboard)
- Check CORS is enabled in Node.js server (it is by default)

### Scraper runs but data doesn't appear in dashboard
- Check MongoDB connection string is correct
- Go to Vercel dashboard and check function logs
- Verify `MONGODB_URI` secret is set correctly

### Google Sheets not syncing
- Verify `GOOGLE_SHEET_ID` is correct (copy from sheet URL)
- Check service account email has edit access to sheet
- Verify `GOOGLE_CREDENTIALS_JSON` is valid

### No logs appearing in Vercel
- Go to Vercel dashboard → Your project → "Functions" tab
- Click the function and check logs

---

## **Local Testing**

Want to test locally before deploying?

```bash
# Install Node dependencies
npm install

# Start local backend
node api/server.js

# In frontend/index.html, keep API = 'http://localhost:5000/api'

# Open dashboard in browser
python -m http.server 8000
# Visit http://localhost:8000/frontend/
```

---

## **File Changes Made**

1. ✅ `package.json` - Node.js dependencies
2. ✅ `vercel.json` - Vercel configuration
3. ✅ `api/server.js` - Express backend (NEW)
4. ✅ `storage/mongo_db.py` - MongoDB driver for Python (NEW)
5. ✅ `requirements.txt` - Added pymongo
6. ✅ `.github/workflows/daily.yml` - Updated with MongoDB secrets
7. ✅ All Python scrapers - Updated to use MongoDB

**What you need to do:**
- Update `frontend/index.html` line 900 with your Vercel URL
- Create MongoDB Atlas cluster
- Deploy to Vercel
- Add GitHub secrets
- Enable GitHub Pages

---

## **Costs**

✅ **All FREE tier:**
- MongoDB Atlas: Free tier (512 MB)
- Vercel: Free tier (hobby)
- GitHub: Free (actions + pages)
- Google Sheets: Free

**Total cost: $0** 🎉

---

**Questions?** Check logs at:
- Vercel: vercel.com (your project → Functions)
- GitHub Actions: Actions tab
- MongoDB: atlas.mongodb.com (your project)


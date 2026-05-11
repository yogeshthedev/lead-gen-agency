# Lead Gen Agency — Automation System

Zero investment lead generation system for Indian market.
**Scrapes leads → MongoDB → Dashboard (GitHub Pages) → Google Sheets → Cold emails → Follow-ups**

🚀 **Now with MongoDB + Vercel backend for real-time dashboard editing!**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Pages Dashboard                 │
│          (Edit leads, track status in real-time)        │
└────────────────────┬────────────────────────────────────┘
                     │ API calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Vercel Backend (Node.js)                  │
│            (Always online, serverless)                  │
└────────────────────┬────────────────────────────────────┘
                     │ reads/writes
                     ▼
┌─────────────────────────────────────────────────────────┐
│          MongoDB Atlas (Cloud Database)                 │
│            (Free 512MB tier, no setup)                  │
└─────────────────────────────────────────────────────────┘

                  GitHub Actions
                  (Daily scraper)
                      ↓
            └──> MongoDB + Google Sheets
```

---

## 📁 Folder Structure

```
lead-gen-agency/
├── api/
│   └── server.js             # Express backend (Node.js) NEW
├── scraper/                  # Playwright scraping scripts
├── emailer/                  # Brevo email + follow-up logic
├── sheets/                   # Google Sheets sync
├── storage/
│   ├── db.py                 # SQLite (keep for reference)
│   └── mongo_db.py           # MongoDB driver NEW
├── frontend/
│   └── index.html            # Dashboard (GitHub Pages)
├── utils/                    # Shared helpers
├── .github/workflows/        # GitHub Actions (daily scraper)
├── package.json              # Node.js dependencies NEW
├── vercel.json               # Vercel config NEW
├── config.py                 # All configuration
├── main.py                   # Python scraper runner
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
└── QUICK_START.md            # 5-minute setup guide
```

---

## ⚡ Quick Start (5 Minutes)

### 1. MongoDB Atlas (Free)
```
→ mongodb.com/cloud/atlas
→ Create account & free cluster (M0)
→ Copy connection string (MONGODB_URI)
```

### 2. Deploy to Vercel
```
→ vercel.com (sign in with GitHub)
→ Import your GitHub repo
→ Add secrets (see QUICK_START.md)
→ Get your Vercel URL
```

### 3. Update Dashboard
In `frontend/index.html` (~line 900):
```javascript
var API = 'https://your-project.vercel.app/api';
```

### 4. Push & Done!
```bash
git add .
git commit -m "Setup MongoDB + Vercel"
git push
```

✅ Dashboard live at: `https://username.github.io/lead-gen-agency/`

---

## 📋 Setup Checklist

See **`QUICK_START.md`** for detailed 5-minute setup.

For complete setup guide with screenshots, see **`MONGODB_VERCEL_SETUP.md`**.

**Quick version:**
- [ ] Create MongoDB Atlas cluster
- [ ] Deploy to Vercel with secrets
- [ ] Update dashboard API URL
- [ ] Add GitHub Actions secrets
- [ ] Enable GitHub Pages
- [ ] Test dashboard & scraper

---

## 💰 Costs

**$0 — Completely FREE**

- MongoDB Atlas: Free tier (512 MB)
- Vercel: Free tier (hobby)
- GitHub: Free (Pages + Actions)
- Google Sheets: Free
- Brevo: Free tier (300 emails/day)

---

## 🔄 How It Works

### Daily at 9 AM UTC:
1. GitHub Actions runs Python scraper
2. Scraper finds leads on JustDial + Google Maps
3. Finds email addresses
4. Saves to MongoDB
5. Syncs to Google Sheets (automatic)
6. Sends cold emails via Brevo
7. Sends follow-ups on schedule

### When You Edit:
1. Update lead status in dashboard
2. Dashboard calls Vercel API
3. Vercel updates MongoDB
4. Changes sync to Google Sheets
5. Real-time on any device

---

## 📊 Features

✅ **Scraping**
- JustDial (business listings)
- Google Maps (reviews, ratings)
- Duplicate detection
- Lead scoring

✅ **Email**
- Cold email sending (Brevo)
- Follow-up sequences (Day 3, 7, 14)
- Reply detection (Gmail)
- Custom templates

✅ **Dashboard**
- View all leads in real-time
- Edit lead status & notes
- Filter by score, website, source
- Sales pipeline tracking
- Export to Google Sheets

✅ **Automation**
- Daily scraping (GitHub Actions)
- Automatic email sends
- Follow-up scheduling
- Google Sheets sync

---

## 🚀 Deployment

### GitHub Pages (Dashboard)
1. Settings → Pages
2. Source: main branch, /root directory
3. Live at: `https://username.github.io/lead-gen-agency/`

### Vercel (Backend API)
1. vercel.com → Import repo
2. Add environment variables
3. Deploy
4. API at: `https://your-project.vercel.app/api`

### GitHub Actions (Scraper)
1. Add secrets to repo
2. Scraper runs daily at 9 AM UTC
3. Manual trigger: Actions → Run workflow

---

## 🛠️ Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt
playwright install chromium

# Install Node.js dependencies
npm install

# Start backend
node api/server.js

# In another terminal, test scraper
python main.py

# Open dashboard at localhost
python -m http.server 8000
# Visit http://localhost:8000/frontend/
```

---

## 📞 Environment Variables

Copy `.env.example` → `.env` and fill in:

```
MONGODB_URI=...           # MongoDB connection
GOOGLE_SHEET_ID=...       # Your sheet ID
GOOGLE_CREDENTIALS_JSON=  # Service account JSON
BREVO_API_KEY=...         # Email API key
FROM_EMAIL=...            # Your email
FROM_NAME=...             # Your name
YOUR_CAL_LINK=...         # Calendly link
TARGET_CITY=Jaipur        # City to scrape
TARGET_BUSINESS=...       # Business type
```

---

## 📖 Documentation

- **QUICK_START.md** — 5-minute setup
- **MONGODB_VERCEL_SETUP.md** — Detailed setup with screenshots
- **GITHUB_PAGES_SETUP.md** — Old GitHub Pages only setup (for reference)

---

## ✨ What's New

### vs Old Version (SQLite):
- ✅ MongoDB cloud database (no local storage)
- ✅ Real-time edits from dashboard
- ✅ Always-online backend (Vercel)
- ✅ Edit dashboard from anywhere (phone, tablet, desktop)
- ✅ Automatic Google Sheets sync on every change
- ✅ Better for scaling (unlimited leads)

---

## 🐛 Troubleshooting

**Dashboard shows "Cannot reach API"**
- Check Vercel API URL in `frontend/index.html`
- Verify Vercel is deployed

**Scraper doesn't sync to MongoDB**
- Check MONGODB_URI is correct
- Verify secrets in GitHub Actions

**Google Sheets not updating**
- Check sheet has edit access
- Verify GOOGLE_CREDENTIALS_JSON is valid

See **MONGODB_VERCEL_SETUP.md** for more troubleshooting.

---

## 📝 License

MIT — Free to use and modify

---

**Ready to start?** Follow **QUICK_START.md** 🚀

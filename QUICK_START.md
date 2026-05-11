# 🚀 Quick Start: MongoDB + Vercel Setup

## **What Changed?**

- ✅ Replaced **SQLite** with **MongoDB** (cloud database)
- ✅ Created **Node.js backend** for Vercel
- ✅ Updated **Python scraper** to use MongoDB
- ✅ Automatic **Google Sheets sync**
- ✅ Dashboard edits now work everywhere (GitHub Pages)

---

## **5-Minute Setup**

### 1️⃣ MongoDB Atlas Account (2 min)
```
→ Go to mongodb.com/cloud/atlas
→ Create free account
→ Create free cluster (M0)
→ Get connection string (Copy the MONGO_DB_URL)
```

### 2️⃣ Deploy to Vercel (2 min)
```
→ Go to vercel.com
→ Import your GitHub repo
→ Add environment variables (MONGO_DB_URL, GOOGLE_SHEET_ID, etc.)
→ Click Deploy
→ Copy your Vercel URL (e.g., https://your-project.vercel.app)
```

### 3️⃣ Update Dashboard (1 min)
```
Edit frontend/index.html, find line ~900:
  var API = 'http://localhost:5000/api';
Change to:
  var API = 'https://your-project.vercel.app/api';
Git push!
```

### 4️⃣ GitHub Pages + Actions (No action needed!)
```
✅ Already set up
✅ Scraper runs daily at 9 AM UTC
✅ Dashboard live at: https://USERNAME.github.io/lead-gen-agency/
```

---

## **Files Modified**

| File | What | Why |
|------|------|-----|
| `package.json` | Node.js config | NEW - Express server |
| `vercel.json` | Vercel config | NEW - Deployment settings |
| `api/server.js` | Express backend | NEW - Node.js API |
| `storage/mongo_db.py` | MongoDB driver | NEW - Replaces SQLite |
| `requirements.txt` | Added pymongo | For MongoDB from Python |
| `.github/workflows/daily.yml` | Added MongoDB vars | For Actions scraper |
| `config.py` | Added MongoDB URI | Configuration |
| All scraper files | Changed imports | Now use mongo_db instead of db |

---

## **Environment Variables Needed**

### **MongoDB Atlas:**
```
MONGO_DB_URL=mongodb+srv://user:pass@cluster.mongodb.net/leadgen
```

### **Google (Sheets + Gmail):**
```
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

### **Brevo (Email):**
```
BREVO_API_KEY=xkeysib_xxx
FROM_EMAIL=your@email.com
FROM_NAME=Your Name
```

### **Your Info:**
```
YOUR_NAME=Your Name
YOUR_CAL_LINK=https://cal.com/you
YOUR_WEBSITE=https://yoursite.com
TARGET_CITY=Jaipur
TARGET_BUSINESS=chartered accountants
```

---

## **How Data Flows**

```
GitHub Actions (9 AM UTC)
    ↓
Scrapes JustDial + Maps
    ↓
Saves to MongoDB
    ↓
Syncs to Google Sheets (automatic!)

--------------------

You edit in Dashboard
    ↓
Dashboard calls Vercel API
    ↓
Updates MongoDB
    ↓
Syncs to Google Sheets (automatic!)
```

---

## **Testing Locally**

Before deploying, test everything locally:

```bash
# Install
npm install
pip install pymongo

# Start backend
node api/server.js

# In another terminal, run scraper (test)
python main.py

# Open dashboard
python -m http.server 8000
# Visit http://localhost:8000/frontend/
```

---

## **Deployment Checklist**

- [ ] MongoDB Atlas account created & cluster running
- [ ] Vercel project created & environment variables added
- [ ] `frontend/index.html` updated with Vercel API URL
- [ ] `git push` done
- [ ] GitHub Actions secrets added (Settings → Secrets)
- [ ] GitHub Pages enabled (Settings → Pages)
- [ ] Tested dashboard loads at `https://username.github.io/lead-gen-agency/`
- [ ] Manually triggered GitHub Actions workflow
- [ ] Data appears in MongoDB Atlas dashboard
- [ ] Data appears in Google Sheets

---

## **Troubleshooting**

### "Cannot reach API"
→ Check Vercel URL is correct in `frontend/index.html`
→ Verify Vercel deployment was successful

### Scraper runs but no data in dashboard
→ Check MongoDB connection string is correct
→ Verify secrets are set in GitHub Actions

### Google Sheets not updating
→ Verify sheet has edit access from service account
→ Check GOOGLE_CREDENTIALS_JSON is valid JSON

### Vercel shows error
→ Check logs at: vercel.com → your project → Functions
→ Verify all environment variables are set

---

## **Support Files**

See detailed setup: `MONGODB_VERCEL_SETUP.md`
See old Flask setup: `GITHUB_PAGES_SETUP.md` (for reference)

---

**Ready?** Follow the "5-Minute Setup" above! 🚀

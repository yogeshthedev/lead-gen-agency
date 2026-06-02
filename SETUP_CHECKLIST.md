# 🎯 Complete Setup Checklist

Use this checklist to ensure everything is set up correctly.

## Phase 1: Local Setup & Testing

- [ ] Python environment set up
  ```bash
  python -m venv venv
  # Windows: venv\Scripts\activate
  # Mac/Linux: source venv/bin/activate
  pip install -r requirements.txt
  playwright install chromium
  ```

- [ ] Node.js dependencies installed
  ```bash
  npm install
  ```

- [ ] MongoDB connection tested locally
  ```bash
  python -c "from storage.mongo_db import init_db; init_db(); print('✓ MongoDB connected')"
  ```

- [ ] Scraper works locally
  ```bash
  python main.py
  ```

- [ ] Backend works locally
  ```bash
  node api/server.js
  # Should show: "✓ Connected to MongoDB" and "🚀 Server running on port 5000"
  ```

- [ ] Dashboard loads locally
  ```bash
  python -m http.server 8000
  # Open browser: http://localhost:8000/frontend/
  ```

---

## Phase 2: Cloud Setup

### MongoDB Atlas Setup
- [ ] Create free MongoDB account (mongodb.com/cloud/atlas)
- [ ] Create free cluster (M0 tier)
- [ ] Create database user
- [ ] Whitelist your IP (or 0.0.0.0 for GitHub Actions)
- [ ] Copy connection string
  ```
  MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/leadgen
  ```
- [ ] Save this - you'll need it for Vercel and GitHub Actions

### Google Cloud Setup
- [ ] Go to console.cloud.google.com
- [ ] Create new project "LeadGen"
- [ ] Enable APIs:
  - [ ] Google Sheets API
  - [ ] Google Drive API
- [ ] Create Service Account
- [ ] Generate JSON key
- [ ] Download and save the JSON (full contents)
  ```
  GOOGLE_CREDENTIALS_JSON={full json here}
  ```
- [ ] Create Google Sheet
- [ ] Copy Sheet ID from URL
  ```
  GOOGLE_SHEET_ID=your_sheet_id_here
  ```
- [ ] Share sheet with service account email

### Brevo Setup
- [ ] Sign up at brevo.com (free)
- [ ] Go to Settings → API Keys
- [ ] Generate new API key
  ```
  BREVO_API_KEY=xkeysib_xxxxxxxxxxxxx
  ```

---

## Phase 3: Vercel Deployment

- [ ] Create Vercel account (vercel.com, sign in with GitHub)
- [ ] Import your GitHub repo
- [ ] Add environment variables in Vercel:
  - [ ] `MONGODB_URI` (from MongoDB Atlas)
  - [ ] `GOOGLE_SHEET_ID` (from Google Sheets)
  - [ ] `GOOGLE_CREDENTIALS_JSON` (full JSON from Google)
  - [ ] `BREVO_API_KEY` (from Brevo)
  - [ ] `FROM_EMAIL` (your email)
  - [ ] `FROM_NAME` (your name)
- [ ] Click "Deploy"
- [ ] Wait for deployment to complete (~2 min)
- [ ] Note your Vercel URL: `https://your-project-name.vercel.app`

### Verify Vercel Works
- [ ] Open browser: `https://your-project-name.vercel.app/health`
- [ ] Should show: `{"ok":true,"db":"connected"}`

---

## Phase 4: Update Dashboard

- [ ] Open `frontend/index.html`
- [ ] Find line ~900: `var API = 'http://localhost:5000/api';`
- [ ] Replace with your Vercel URL:
  ```javascript
  var API = 'https://your-project-name.vercel.app/api';
  ```
- [ ] Save and commit
  ```bash
  git add frontend/index.html
  git commit -m "Update API endpoint to Vercel"
  git push
  ```

---

## Phase 5: GitHub Setup

### Enable GitHub Pages
- [ ] Go to GitHub repo → Settings → Pages
- [ ] Source: Deploy from a branch
- [ ] Branch: main → /root
- [ ] Click Save
- [ ] Wait ~2 minutes
- [ ] Dashboard will be live at: `https://YOUR_USERNAME.github.io/lead-gen-agency/`

### Add GitHub Actions Secrets
- [ ] Go to Settings → Secrets and variables → Actions
- [ ] Add these secrets (one by one):
  - [ ] `MONGODB_URI` (from MongoDB Atlas)
  - [ ] `GOOGLE_SHEET_ID` (from Google Sheets)
  - [ ] `GOOGLE_CREDENTIALS_JSON` (full JSON)
  - [ ] `BREVO_API_KEY` (from Brevo)
  - [ ] `FROM_EMAIL` (your email)
  - [ ] `FROM_NAME` (your name)
  - [ ] `YOUR_NAME` (your full name)
  - [ ] `YOUR_CAL_LINK` (calendly link)
  - [ ] `YOUR_WEBSITE` (your website)
  - [ ] `TARGET_CITY` (city to scrape, e.g., "Jaipur")
  - [ ] `TARGET_BUSINESS` (business type, e.g., "chartered accountants")

---

## Phase 6: Test Everything

### Test Dashboard
- [ ] Open: `https://YOUR_USERNAME.github.io/lead-gen-agency/`
- [ ] Dashboard loads
- [ ] "Dashboard" tab shows stats (should be 0 for now)
- [ ] No error about "Cannot reach API"

### Test GitHub Actions Scraper
- [ ] Go to GitHub → Actions tab
- [ ] Click "Daily Lead Gen Scraper" workflow
- [ ] Click "Run workflow" → "Run workflow"
- [ ] Watch logs as it runs
- [ ] Wait 2-3 minutes for completion
- [ ] Check MongoDB dashboard to verify leads were added
- [ ] Refresh dashboard in browser - leads should appear
- [ ] Check Google Sheet - data should be synced

### Test Dashboard Editing
- [ ] In dashboard, find a lead
- [ ] Click the pencil icon to edit
- [ ] Change status to "sent"
- [ ] Click Save
- [ ] Refresh dashboard - status should still be "sent"
- [ ] Check Google Sheet - status should be updated there too

---

## Phase 7: Verify Automation

### Daily Scraper Schedule
- [ ] GitHub Actions will run automatically every day at 9 AM UTC
- [ ] To verify: Go to Actions tab, check for latest runs
- [ ] Should see "Daily Lead Gen Scraper" running

### Manual Trigger
- [ ] To run scraper manually:
  - [ ] Actions tab → "Daily Lead Gen Scraper"
  - [ ] Click "Run workflow"
  - [ ] Select "Run workflow"
  - [ ] Logs will show live

---

## 🆘 Troubleshooting Checklist

### If Dashboard Shows "Cannot reach API"
- [ ] Verify Vercel deployment successful (check vercel.com dashboard)
- [ ] Check `frontend/index.html` has correct Vercel URL
- [ ] Check your internet connection
- [ ] Try hard refresh (Ctrl+Shift+R)
- [ ] Check Vercel function logs (Vercel dashboard → Functions)

### If Scraper Runs but No Data
- [ ] Check MONGODB_URI is correct in GitHub Actions secrets
- [ ] Verify MongoDB cluster is running (check MongoDB Atlas dashboard)
- [ ] Check GitHub Actions logs for errors
- [ ] Verify GOOGLE_CREDENTIALS_JSON is valid JSON

### If Google Sheets Not Syncing
- [ ] Verify sheet ID is correct (from URL)
- [ ] Verify service account email has edit access to sheet
- [ ] Check GOOGLE_CREDENTIALS_JSON is complete
- [ ] Wait 2-3 minutes - sync may take time

### If Vercel Shows 500 Error
- [ ] Check Vercel function logs
- [ ] Verify all environment variables are set
- [ ] Check MONGODB_URI format is correct
- [ ] Redeploy: Settings → Deployments → Redeploy

---

## 📞 Quick Reference

| What | Where | Value |
|------|-------|-------|
| Dashboard | GitHub Pages | https://USERNAME.github.io/lead-gen-agency/ |
| Backend API | Vercel | https://your-project.vercel.app/api |
| Database | MongoDB | mongodb+srv://... (from Atlas) |
| Sheets | Google | Your Google Sheet URL |
| Logs | GitHub Actions | Actions tab in GitHub |
| Logs | Vercel | vercel.com dashboard |
| Logs | MongoDB | MongoDB Atlas dashboard |

---

## ✅ Success Checklist

When everything is working:

- [ ] ✅ Dashboard loads with no errors
- [ ] ✅ Can view all scraped leads
- [ ] ✅ Can edit lead status and see changes persist
- [ ] ✅ Google Sheets updates when you make changes
- [ ] ✅ Scraper runs every day at 9 AM UTC
- [ ] ✅ New leads appear in dashboard within minutes
- [ ] ✅ Emails send successfully
- [ ] ✅ Follow-ups trigger on schedule

**Congratulations! Your system is live! 🎉**

---

## 💡 Tips

1. **Monitoring**: Check `MongoDB Atlas Dashboard` → your cluster → Metrics to see activity
2. **Scaling**: MongoDB free tier supports up to 512 MB. If you exceed, upgrade to paid tier
3. **Backup**: Export data regularly to Google Sheets (automatic)
4. **Customization**: Edit templates in `emailer/templates.py`
5. **Testing**: Use GitHub Actions "Run workflow" manually to test scraper

---

## 📚 Documentation Files

- `README.md` - Overview of entire system
- `QUICK_START.md` - 5-minute setup
- `MONGODB_VERCEL_SETUP.md` - Detailed setup with screenshots
- `GITHUB_PAGES_SETUP.md` - Old setup (for reference)

---

**Questions?** Check the specific setup guide mentioned above.

**Ready to deploy?** Start with Phase 1 and work through each phase in order! 🚀

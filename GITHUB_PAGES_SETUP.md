# 🚀 Setup: GitHub Pages + GitHub Actions

## **Part 1: Push to GitHub**

1. Initialize git repo (if not already):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a repo on GitHub (don't initialize with README)

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/lead-gen-agency.git
git branch -M main
git push -u origin main
```

---

## **Part 2: Enable GitHub Pages (Dashboard)**

Your frontend dashboard will be live at: `https://YOUR_USERNAME.github.io/lead-gen-agency/`

### Steps:

1. Go to **Settings** → **Pages** (left sidebar)
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main** → **/root**
   - Click **Save**

3. Wait ~1 minute. You'll see: "Your site is live at https://YOUR_USERNAME.github.io/lead-gen-agency/"

✅ **Dashboard is now hosted!**

---

## **Part 3: Setup GitHub Actions (Scraper)**

Your scraper will run automatically every day at 9 AM UTC.

### Add Secrets (for GitHub Actions):

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add these:

| Secret Name | Value |
|-----------|-------|
| `BREVO_API_KEY` | Your Brevo API key |
| `FROM_EMAIL` | Your email address |
| `FROM_NAME` | Your name |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID |
| `GOOGLE_CREDENTIALS` | *Full contents of credentials.json file* |
| `YOUR_NAME` | Your full name |
| `YOUR_CAL_LINK` | Your Calendly/Cal link |
| `YOUR_WEBSITE` | Your website URL |
| `TARGET_CITY` | City to scrape (e.g., "Jaipur") |
| `TARGET_BUSINESS` | Business type (e.g., "chartered accountants") |

⚠️ **Important**: For `GOOGLE_CREDENTIALS`, paste the entire contents of your `credentials.json` file.

### Check Workflow Status:

1. Go to **Actions** tab
2. Select **Daily Lead Gen Scraper**
3. You'll see past and future runs

✅ **Scraper is now automated!**

---

## **What Happens Now:**

- **Every day at 9 AM UTC**: 
  1. GitHub Actions scrapes JustDial + Google Maps
  2. Finds email addresses
  3. Sends cold emails via Brevo
  4. Exports data to your Google Sheet

- **Your Dashboard**: 
  - Accessible at `https://YOUR_USERNAME.github.io/lead-gen-agency/`
  - Shows stats (scraped leads, sent emails, etc.)
  - Can be viewed on any device (phone, tablet, desktop)

---

## **Customize Scraper Schedule**

Edit `.github/workflows/daily.yml` to change the run time:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change this
```

**Cron format**: `minute hour * * day-of-week`

Examples:
- `0 9 * * *` → 9 AM every day
- `0 9 * * 1` → 9 AM every Monday
- `0 6,18 * * *` → 6 AM and 6 PM every day

---

## **Troubleshooting**

### Scraper failed?
- Check **Actions** tab → **Daily Lead Gen Scraper** → Recent run
- Look at logs to see what went wrong

### Dashboard not loading?
- Make sure branch is set to `/root` in Pages settings
- Try hard refresh (`Ctrl+Shift+R`)

### Credentials not working?
- Verify secrets are added correctly
- Check that `credentials.json` content is pasted without extra spaces

---

## **Files Created:**

- `.gitignore` — Prevents secrets from being committed
- `.github/workflows/daily.yml` — Scraper automation
- `requirements.txt` — Python dependencies

**You're all set! 🎉**

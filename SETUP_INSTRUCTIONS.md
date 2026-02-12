# COMPLETE SETUP INSTRUCTIONS
## Garmin Health Tracker - From Zero to Live in 1 Hour

Follow every step EXACTLY as written. Do not skip any steps.

---

## PART 1: INSTALL REQUIRED SOFTWARE (15 minutes)

### Step 1.1: Install Git

**What is Git?** A tool that uploads your code to the internet.

**Windows:**
1. Go to: https://git-scm.com/download/win
2. Click "Click here to download"
3. Run the installer
4. Click "Next" on everything (use default settings)
5. Click "Install"
6. Click "Finish"

**Mac:**
1. Open Terminal (press Cmd+Space, type "Terminal", press Enter)
2. Type this command and press Enter:
   ```bash
   git --version
   ```
3. If it says "command not found", install from: https://git-scm.com/download/mac
4. Otherwise, you already have it! Continue to next step.

**Verify it worked:**
- Open Command Prompt (Windows) or Terminal (Mac)
- Type: `git --version`
- You should see something like "git version 2.43.0"

---

### Step 1.2: Create GitHub Account

**What is GitHub?** A website where you store your code.

1. Go to: https://github.com
2. Click "Sign up" (top right corner)
3. Enter your email address
4. Click "Continue"
5. Create a password
6. Create a username (any name is fine, like "yourname-health")
7. Verify you're human (do the puzzle)
8. Check your email for verification code
9. Enter the 6-digit code
10. Click "Continue"
11. Skip the personalization questions (click "Skip personalization")
12. You're done! You should see your GitHub homepage

---

### Step 1.3: Create Render Account

**What is Render?** The free cloud server that will run your app 24/7.

1. Go to: https://render.com
2. Click "Get Started" or "Sign Up" (top right)
3. Click "GitHub" button (to sign up with GitHub)
4. It will ask permission - click "Authorize Render"
5. You're now logged into Render!
6. You should see your Render Dashboard

---

## PART 2: PREPARE YOUR CODE FILES (10 minutes)

### Step 2.1: Download Your Project Files

**Option A - Easy Way (Recommended):**

I'll tell you the exact files you need. You already have them in your outputs - I'll package them for you now.

**Option B - Manual Way:**

Create a folder on your Desktop called `garmin-health-tracker` and save these files inside (I'll provide them all).

---

### Step 2.2: Organize Your Files

Your folder should look EXACTLY like this:

```
garmin-health-tracker/
├── app.py
├── fetch_garmin_data.py
├── requirements.txt
├── render.yaml
├── .gitignore
├── README.md
├── templates/
│   └── dashboard.html
└── static/
    └── style.css
```

**How to check:**
- Open the `garmin-health-tracker` folder
- You should see 6 files directly in the folder
- You should see 2 folders: `templates` and `static`
- Inside `templates` folder: 1 file called `dashboard.html`
- Inside `static` folder: 1 file called `style.css`

---

## PART 3: UPLOAD CODE TO GITHUB (15 minutes)

### Step 3.1: Open Terminal/Command Prompt

**Windows:**
1. Click Start menu
2. Type "cmd"
3. Click "Command Prompt"

**Mac:**
1. Press Cmd+Space
2. Type "terminal"
3. Press Enter

---

### Step 3.2: Navigate to Your Project Folder

Type these commands ONE AT A TIME (press Enter after each):

**Windows:**
```bash
cd Desktop
cd garmin-health-tracker
```

**Mac:**
```bash
cd ~/Desktop/garmin-health-tracker
```

**Verify you're in the right place:**
- Type: `dir` (Windows) or `ls` (Mac)
- You should see your files listed: app.py, fetch_garmin_data.py, etc.

---

### Step 3.3: Initialize Git Repository

Copy and paste these commands ONE AT A TIME, pressing Enter after each:

```bash
git init
```

You should see: "Initialized empty Git repository"

---

### Step 3.4: Add All Files

```bash
git add .
```

(That's "git add" then a DOT)

No output is normal.

---

### Step 3.5: Commit Files

```bash
git commit -m "Initial commit"
```

You should see something like "9 files changed, 500 insertions"

---

### Step 3.6: Create GitHub Repository

1. Go to: https://github.com/new
2. In "Repository name" box, type: `garmin-health-tracker`
3. Leave it as "Public"
4. **DO NOT** check any boxes (no README, no gitignore, nothing)
5. Click "Create repository" (green button at bottom)

You'll see a page with instructions. **IGNORE THEM.** Follow my instructions below instead.

---

### Step 3.7: Link Your Local Code to GitHub

On the GitHub page you just opened, find the section that says "…or push an existing repository from the command line"

Copy the TWO commands shown there. They'll look like:

```bash
git remote add origin https://github.com/YOUR-USERNAME/garmin-health-tracker.git
git branch -M main
git push -u origin main
```

**Replace YOUR-USERNAME with your actual GitHub username!**

Paste these commands into your Terminal/Command Prompt ONE AT A TIME.

**If asked for username/password:**
- Username: Your GitHub username
- Password: You need a "personal access token" (see Step 3.8)

---

### Step 3.8: Create GitHub Personal Access Token (If Needed)

If GitHub asks for a password and rejects it, you need a token:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. In "Note" field, type: "Render deployment"
4. Check the box next to "repo" (this checks all repo boxes)
5. Scroll down, click "Generate token" (green button)
6. **COPY THE TOKEN IMMEDIATELY** (it looks like: ghp_xxxxxxxxxxxx)
7. Paste it when asked for password
8. Save it somewhere safe (you'll need it again)

---

### Step 3.9: Verify Upload Worked

1. Go to: https://github.com/YOUR-USERNAME/garmin-health-tracker
   (Replace YOUR-USERNAME with your username)
2. You should see all your files listed
3. Click on a few files to verify they uploaded correctly

✅ **CHECKPOINT:** Your code is now on GitHub!

---

## PART 4: DEPLOY TO RENDER (20 minutes)

### Step 4.1: Connect GitHub to Render

1. Go to: https://dashboard.render.com
2. Click "New +" button (top right)
3. Select "Blueprint"
4. Click "Connect GitHub" button
5. A popup appears - click "Authorize Render"
6. You might see a list of repositories - click "Configure GitHub App"
7. Scroll down, find "Repository access"
8. Select "Only select repositories"
9. Click the dropdown, find `garmin-health-tracker`
10. Click "Save"
11. You're back on Render - click "Connect" next to your repository

---

### Step 4.2: Set Up Environment Variables

1. You should see "Name: garmin-health-tracker"
2. Scroll down to "Environment Variables" section
3. Click "Add Environment Variable" button

**Add these variables ONE AT A TIME:**

**Variable 1:**
- Key: `GARMIN_EMAIL`
- Value: Your Garmin Connect email (like: yourname@gmail.com)
- Click "Add"

**Variable 2:**
- Key: `GARMIN_PASSWORD`
- Value: Your Garmin Connect password
- Click "Add"

**IMPORTANT:** Make sure you typed your email and password correctly! Double-check for typos.

---

### Step 4.3: Deploy Your App

1. Scroll to bottom of page
2. Click "Apply" button (blue button)
3. Render will now deploy your app (this takes 3-5 minutes)
4. You'll see a build log with lots of text scrolling

**What you should see:**
- "Installing dependencies..."
- "Build successful"
- "Deploy successful"
- Your app URL will appear at top (like: https://garmin-health-tracker-abc123.onrender.com)

**If you see errors:** Don't panic! Skip to "Common Errors" section at bottom of this doc.

---

### Step 4.4: Run First Data Sync

Your web app is live, but you have no data yet! Let's fix that.

1. In Render dashboard, find your services
2. You should see TWO services:
   - `garmin-health-tracker` (Web Service) - Your website
   - `daily-garmin-sync` (Cron Job) - Your data syncer

3. Click on `daily-garmin-sync`
4. Click "Manual Trigger" button (or "Trigger cron job")
5. Click "Trigger" to confirm
6. Watch the logs - you should see:
   ```
   Starting Garmin Data Sync
   Connecting to Garmin Connect...
   ✅ Logged in successfully!
   Fetching data from 2025-11-12 to 2026-02-10
   Fetching daily health metrics...
   ```
7. This will take 5-15 minutes to fetch 90 days of data
8. Wait for "✨ Sync Complete!"

---

### Step 4.5: View Your Dashboard!

1. Go back to the `garmin-health-tracker` Web Service
2. At the top, you'll see your URL (like: https://garmin-health-tracker-abc123.onrender.com)
3. Click on it or copy-paste into your browser
4. **First load might take 30 seconds** (free tier wakes up from sleep)
5. You should see your dashboard with:
   - Today's stats (steps, heart rate, sleep, body battery)
   - Charts showing 30-day trends
   - List of recent activities

🎉 **CONGRATULATIONS!** Your app is live!

---

## PART 5: VERIFY AUTOMATION (5 minutes)

### Step 5.1: Check Cron Schedule

1. In Render dashboard, click on `daily-garmin-sync`
2. You should see: "Schedule: 0 7 * * *"
3. This means: "Run at 7:00 AM every day"

**Want to change the time?**
- Edit `render.yaml` file on your computer
- Change `"0 7 * * *"` to your preferred time:
  - `"0 8 * * *"` = 8 AM
  - `"0 19 * * *"` = 7 PM
  - `"30 6 * * *"` = 6:30 AM
- Push changes to GitHub (repeat Part 3 steps 3.4-3.7)
- Render will automatically update

---

### Step 5.2: Test Manual Sync

Try triggering the data sync manually to make sure it works:

1. Click "Manual Trigger" on the cron job
2. Watch logs for any errors
3. When complete, refresh your dashboard
4. You should see updated data

---

## PART 6: ONGOING USAGE

### How It Works Now:

1. **Automatic:** Every day at 7 AM, Render automatically:
   - Logs into your Garmin account
   - Downloads yesterday's data
   - Saves it to your database
   - Goes back to sleep

2. **Manual:** Anytime you want:
   - Visit your dashboard URL
   - See all your health data
   - Check from phone, tablet, or computer

### Your Dashboard URL

Save this somewhere you can find it:
- **URL:** https://garmin-health-tracker-YOUR-ID.onrender.com
- Bookmark it on your phone and computer
- You can share it with family if you want (it has no password protection by default)

---

## COMMON ERRORS & SOLUTIONS

### Error: "Login failed"

**Cause:** Wrong email or password in environment variables

**Fix:**
1. Go to Render dashboard
2. Click on `daily-garmin-sync`
3. Click "Environment" tab
4. Click "Edit" next to GARMIN_EMAIL and GARMIN_PASSWORD
5. Fix any typos
6. Click "Save Changes"
7. Trigger the cron job again

---

### Error: "Module not found: garminconnect"

**Cause:** Dependencies didn't install

**Fix:**
1. Check that `requirements.txt` file exists in your GitHub repo
2. In Render, click "Manual Deploy" → "Deploy latest commit"

---

### Error: "Database is locked"

**Cause:** Web service and cron job trying to access database simultaneously

**Fix:**
- This is normal and rare
- Just trigger the cron job again
- It should work the second time

---

### Error: Website shows "Service Unavailable"

**Cause:** App is sleeping (free tier)

**Fix:**
- Wait 30 seconds and refresh
- After first load, it will be instant

---

### Error: No data showing on dashboard

**Possible causes:**

1. **Sync hasn't run yet**
   - Manually trigger the cron job
   - Wait for it to complete

2. **Garmin account has no data**
   - Make sure you've been using your Garmin device
   - Check Garmin Connect website to verify data exists

3. **Date range issue**
   - The dashboard shows last 30 days
   - If you're a new Garmin user, you might not have 30 days yet

---

## BACKFILLING OLDER DATA

After the initial 90-day sync, if you want ALL your historical data:

1. In Render dashboard, go to `daily-garmin-sync`
2. Click "Environment" tab
3. Find `DAYS_TO_FETCH`
4. Change value from `1` to `365` (or `730` for 2 years, etc.)
5. Click "Save Changes"
6. Click "Manual Trigger"
7. Wait for sync to complete (might take 30+ minutes for years of data)
8. After it's done, change `DAYS_TO_FETCH` back to `1`
9. Click "Save Changes"

---

## ADDING PASSWORD PROTECTION

Your dashboard is currently public (anyone with the URL can see it).

To add password protection:

1. We'd need to modify `app.py`
2. Add Flask-Login or Flask-HTTPAuth
3. This is more advanced - let me know if you want instructions!

---

## DOWNLOADING YOUR DATA

Want to download your database for backup or Excel analysis?

**Steps:**
1. In Render dashboard, click on `garmin-health-tracker` (web service)
2. Click "Shell" tab
3. Type: `ls` and press Enter (you should see `health.db`)
4. Unfortunately, Render doesn't offer easy file download on free tier
5. **Workaround:** Add a download endpoint to your app (I can show you how)

---

## UPDATING YOUR APP

If you want to change anything:

1. Edit the files on your computer
2. Run these commands:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. Render automatically detects changes and redeploys
4. Wait 2-3 minutes for deploy to complete

---

## COSTS

**Current cost: $0/month**

**Free tier includes:**
- 750 hours/month of web service (enough for 24/7)
- Unlimited cron jobs
- 1 GB database storage
- Unlimited bandwidth (within reason)

**If you exceed free tier:**
- Render will email you
- You can upgrade to paid ($7/month for no-sleep web service)
- Or reduce usage

---

## GETTING HELP

If something doesn't work:

1. **Check the logs:**
   - In Render dashboard
   - Click on the service
   - Click "Logs" tab
   - Copy the error message

2. **Ask me:**
   - Share the exact error message
   - Tell me which step you're on
   - I'll help you fix it!

---

## NEXT STEPS

Once everything is working, you can:

1. **Customize the dashboard**
   - Edit `templates/dashboard.html`
   - Edit `static/style.css`
   - Add more charts or stats

2. **Add more metrics**
   - Edit `fetch_garmin_data.py`
   - Add new data fields
   - Update database schema in `app.py`

3. **Add notifications**
   - Email yourself daily summaries
   - Get alerts for health milestones

4. **Export to other tools**
   - Add CSV export button
   - Integrate with Google Sheets
   - Send data to Apple Health

Let me know what you want to add!

---

## QUICK REFERENCE

**Your URLs:**
- GitHub Repo: https://github.com/YOUR-USERNAME/garmin-health-tracker
- Render Dashboard: https://dashboard.render.com
- Your Dashboard: https://garmin-health-tracker-YOUR-ID.onrender.com

**Important Commands:**
```bash
# Update your app after making changes:
git add .
git commit -m "your message"
git push

# Check if Git is working:
git status
```

**Cron Schedule Format:**
- `0 7 * * *` = 7:00 AM daily
- `0 12 * * *` = 12:00 PM daily
- `0 20 * * *` = 8:00 PM daily
- `0 */6 * * *` = Every 6 hours

---

## SUMMARY OF WHAT YOU BUILT

You now have:

✅ A cloud-hosted web application
✅ Automatic daily data sync from Garmin
✅ Interactive dashboard with charts
✅ 90 days of historical health data
✅ Detailed heart rate data for all activities
✅ Sport-specific metrics for swimming, cycling, rowing
✅ Free hosting that runs 24/7
✅ Accessible from any device

**Total time:** ~1 hour
**Total cost:** $0
**Technical skills required:** None (you just followed steps!)

---

You did it! 🎉

Any questions about any step? Let me know the step number and I'll clarify!

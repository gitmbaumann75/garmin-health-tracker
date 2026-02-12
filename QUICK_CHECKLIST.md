# Quick Reference Checklist

Use this to track your progress!

## Before You Start
- [ ] Python is installed (check: open Terminal/CMD, type `python --version`)
- [ ] You have your Garmin Connect email and password handy
- [ ] You have 1-2 hours available

---

## Part 1: Install Software (15 min)

- [ ] Install Git
  - Windows: Download from https://git-scm.com/download/win
  - Mac: Type `git --version` in Terminal
- [ ] Create GitHub account at https://github.com
- [ ] Create Render account at https://render.com (use GitHub to sign up)

---

## Part 2: Prepare Files (5 min)

- [ ] Download the `garmin-health-tracker` folder
- [ ] Place it on your Desktop
- [ ] Open the folder - you should see 8-10 files

---

## Part 3: Upload to GitHub (15 min)

- [ ] Open Terminal/Command Prompt
- [ ] Navigate to your folder: `cd Desktop/garmin-health-tracker`
- [ ] Run: `git init`
- [ ] Run: `git add .`
- [ ] Run: `git commit -m "Initial commit"`
- [ ] Create repository on GitHub.com
- [ ] Link and push (commands from GitHub)
- [ ] Verify files appear on GitHub.com

---

## Part 4: Deploy to Render (20 min)

- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Blueprint"
- [ ] Connect GitHub account
- [ ] Select `garmin-health-tracker` repository
- [ ] Add environment variables:
  - GARMIN_EMAIL = your_email@gmail.com
  - GARMIN_PASSWORD = your_password
- [ ] Click "Apply"
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Copy your app URL

---

## Part 5: First Data Sync (10 min)

- [ ] In Render dashboard, find `daily-garmin-sync`
- [ ] Click "Manual Trigger"
- [ ] Watch logs for "✅ Logged in successfully!"
- [ ] Wait for "✨ Sync Complete!" (5-15 minutes)
- [ ] Visit your app URL
- [ ] See your data on dashboard!

---

## Part 6: Verify Everything Works

- [ ] Dashboard loads (may take 30 sec first time)
- [ ] You see today's stats in cards
- [ ] Charts show your data
- [ ] Click "Export CSV" - file downloads
- [ ] Open CSV in Excel - see your data

---

## You're Done! 🎉

Now:
- [ ] Bookmark your dashboard URL
- [ ] Check it tomorrow to verify automatic sync worked
- [ ] Celebrate - you built a cloud app!

---

## Important URLs to Save

**Your GitHub Repository:**
https://github.com/YOUR-USERNAME/garmin-health-tracker

**Your Render Dashboard:**
https://dashboard.render.com

**Your Health Dashboard:**
https://garmin-health-tracker-XXXXX.onrender.com
(Get this from Render after deployment)

---

## Daily Automatic Sync

Every day at 7:00 AM (server time):
1. Render wakes up your sync job
2. Logs into Garmin
3. Downloads yesterday's data
4. Saves to database
5. Goes back to sleep

You don't need to do anything!

---

## If Something Goes Wrong

**Error during git push:**
- You probably need a personal access token
- See Step 3.8 in SETUP_INSTRUCTIONS.md

**Error during deployment:**
- Check that environment variables are correct
- Make sure you typed email/password correctly

**No data showing:**
- Did the sync job complete successfully?
- Check the logs in Render
- Make sure your Garmin has data

**Site shows "Service Unavailable":**
- Wait 30 seconds (free tier wakes from sleep)
- Refresh the page

---

## Common Commands

**Update your app after making changes:**
```bash
git add .
git commit -m "Updated something"
git push
```

**Check if you're in the right folder:**
```bash
ls        # Mac/Linux
dir       # Windows
```

**See if Git is working:**
```bash
git status
```

---

## Next Steps (After It's Working)

1. Use it for 2-4 weeks
2. See what insights you gain
3. Decide if you want to add InBody
4. Tell me when you're ready for Phase 2!

---

Questions? Stuck? Let me know which checkbox you're on!

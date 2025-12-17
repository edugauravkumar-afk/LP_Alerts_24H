# 🎯 Daily Scheduling Setup - LP Alerts 24H

Configure LP Alerts to run automatically every day at 8:00 AM UTC, just like Daily_Alert folder.

---

## 📋 Prerequisites

1. ✅ System is already set up and tested
2. ✅ `.env` file configured with credentials
3. ✅ Virtual environment created

---

## 🖥️ For macOS & Linux

### Option 1: Automatic Setup (Easy)

```bash
cd /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H
bash schedule_cron.sh
```

**What it does:**
- ✅ Adds cron job for daily 8:00 AM UTC
- ✅ Logs to alert_checker.log
- ✅ Runs automatically every day

### Option 2: Manual Setup

```bash
# Edit crontab
crontab -e

# Add this line:
0 8 * * * cd /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H && /usr/bin/python3 main.py >> alert_checker.log 2>&1
```

### Verify Cron Job

```bash
# List all your cron jobs
crontab -l

# Watch for execution
tail -f alert_checker.log
```

### Remove Cron Job

```bash
crontab -e
# Delete the LP_Alerts_24H line
```

---

## 🪟 For Windows

### Option 1: Automatic Setup (Easy)

1. **Run as Administrator:**
   - Right-click `schedule_windows.bat`
   - Select "Run as Administrator"

2. **That's it!** Task is created and scheduled

**What it does:**
- ✅ Creates Windows scheduled task
- ✅ Sets daily trigger at 8:00 AM
- ✅ Runs automatically every day

### Option 2: Manual Setup via Task Scheduler

1. **Open Task Scheduler** (search in Start menu)
2. **Right-click** "Task Scheduler Library"
3. **Click** "Create Basic Task"
4. **Configure:**
   - **Name:** `LP_Alerts_24H`
   - **Description:** Daily LP Alert Checker
   - **Trigger:** Daily at 08:00 AM
   - **Action:** Start program
     - **Program:** `C:\path\to\venv\Scripts\python.exe`
     - **Arguments:** `main.py`
     - **Start in:** `C:\path\to\LP_Alerts_24H`

### Verify Windows Task

```cmd
# List the task
schtasks /query /tn "LP_Alerts_24H" /v

# View task history
schtasks /query /tn "LP_Alerts_24H" /fo list /v
```

### Remove Windows Task

```cmd
# Run as Administrator
schtasks /delete /tn "LP_Alerts_24H" /f
```

---

## 📧 Email Configuration

Update your `.env` file to match Daily_Alert settings:

```env
# Email Recipients (comma-separated, no spaces)
RECIPIENTS=user1@taboola.com,user2@taboola.com,user3@taboola.com

# Optional CC recipients
CC_RECIPIENTS=team@taboola.com

# SMTP Settings
SMTP_SERVER=ildcsmtp.office.taboola.com
SMTP_PORT=25
FROM_EMAIL=Daily-LP-Alerts@taboola.com
```

**Note:** Use same values as your Daily_Alert folder .env

---

## 🔍 Monitoring & Logging

### View Recent Logs

```bash
# Last 20 lines
tail -20 alert_checker.log

# Follow logs in real-time
tail -f alert_checker.log

# Search for errors
grep "❌" alert_checker.log

# Count total runs
wc -l alert_checker.log
```

### Log File Location

```
/Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/alert_checker.log
```

### Sample Log Output

```
[2025-12-18 08:00:00] ================================================================================
[2025-12-18 08:00:00] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-18 08:00:00] ================================================================================
[2025-12-18 08:00:00] 📍 Fetching campaigns targeting English countries...
[2025-12-18 08:00:05] ✅ Found 100000 English-targeting campaigns
[2025-12-18 08:00:06] 📅 Fetching LP alerts for last 24 hours...
[2025-12-18 08:00:06]   📦 Chunk 1: 2025-12-17 14:00:00 to 2025-12-17 18:00:00
[2025-12-18 08:00:30]      ✅ Got 5 LP_CHANGE alerts
[2025-12-18 08:02:00] 🔍 Matching alerts to publishers...
[2025-12-18 08:02:15] ✅ Matched 3 alerts to target regions
[2025-12-18 08:02:20] ✅ Deduplication: 2 new / 3 total
[2025-12-18 08:02:25] 📧 Sending email to: user1@taboola.com, user2@taboola.com
[2025-12-18 08:02:25] 📧 CC: team@taboola.com
[2025-12-18 08:02:30] ✅ Email sent to 2 recipients + 1 CC
[2025-12-18 08:02:30] ✅ Alert check complete: 2 alerts sent to 2 recipients
```

---

## 🆘 Troubleshooting

### Cron Job Not Running (macOS/Linux)

```bash
# Check if cron daemon is running
sudo launchctl list | grep cron

# Check system logs
log stream --predicate 'process == "cron"'

# Verify permissions
ls -la /usr/lib/cron/tabs/

# Check if user is in cron allow list
sudo cat /etc/cron.allow 2>/dev/null || echo "No cron.allow file"
```

### Task Not Running (Windows)

1. Open Task Scheduler
2. Click "Task Scheduler Library"
3. Find "LP_Alerts_24H"
4. Right-click → "Run" to test manually
5. Check "Last Run Result" (should be 0 for success)

### Email Not Sending

1. Check .env file:
   ```bash
   grep "RECIPIENTS\|CC_\|SMTP" .env
   ```

2. Verify RECIPIENTS is not empty:
   ```bash
   # Should not be empty
   echo $RECIPIENTS
   ```

3. Test SMTP connection:
   ```bash
   telnet ildcsmtp.office.taboola.com 25
   ```

### Permission Denied Error

**macOS/Linux:**
```bash
# Make scripts executable
chmod +x schedule_cron.sh
chmod +x main.py
```

**Windows:**
- Right-click script
- "Run as Administrator"

---

## ✅ Verification Checklist

- [ ] Cron job added (macOS/Linux) or Task created (Windows)
- [ ] `.env` file has RECIPIENTS configured
- [ ] `.env` file has CC_RECIPIENTS (if needed)
- [ ] SMTP_SERVER is correct
- [ ] Ran `python main.py` manually once (to verify it works)
- [ ] Check alert_checker.log exists
- [ ] Viewed logs to confirm no errors

---

## 📊 Schedule Summary

| OS | Scheduler | Command | Time |
|---|-----------|---------|------|
| macOS/Linux | Cron | `bash schedule_cron.sh` | 08:00 UTC daily |
| Windows | Task Scheduler | `schedule_windows.bat` | 08:00 AM daily |

---

## 🔄 Next Steps

1. **If macOS/Linux:**
   ```bash
   bash schedule_cron.sh
   ```

2. **If Windows:**
   - Right-click `schedule_windows.bat`
   - "Run as Administrator"

3. **Verify:**
   ```bash
   tail -f alert_checker.log
   ```

4. **Test manually:**
   ```bash
   python main.py
   ```

---

**System is now fully automated!** 🚀

The alert checker will run every day at 8:00 AM UTC and email you results.

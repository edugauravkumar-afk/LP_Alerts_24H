# 📑 INDEX - LP_Alerts_24H Folder Contents

Complete standalone system for 24-hour LP alert checking.

## 🗂 File Structure

```
LP_Alerts_24H/
├── 📄 main.py                    (370 lines) - Main alert checker
├── 🔧 config.py                  (60 lines)  - Configuration constants
├── 📧 send_email.py              (270 lines) - Email module
├── 🧪 test_system.py             (200 lines) - System tester
├── 🏃 setup.sh                   (40 lines)  - Automated setup
├── 📦 requirements.txt            (3 packages) - Dependencies
├── 📝 .env.example               (13 lines)  - Credentials template
├── 🔐 .env                       (To create) - Your credentials
├── 📋 seen_lp_alerts.json        (Empty)    - Deduplication tracker
├── 📚 README.md                  (Complete docs)
├── ⚡ QUICK_START.md             (1-minute guide)
├── 📊 SETUP_SUMMARY.md           (This folder overview)
└── 📑 INDEX.md                   (This file)
```

## 📖 Documentation Files

### Start Here
- **QUICK_START.md** - 5-minute setup and run guide
- **SETUP_SUMMARY.md** - Overview of what's included

### Detailed Guides
- **README.md** - Complete documentation with troubleshooting
- **INDEX.md** - This file

## 🔨 Script Files

### Main Scripts
| File | Purpose | Lines |
|------|---------|-------|
| main.py | Alert checker with 6-step logic | 370 |
| send_email.py | Email formatting & sending | 270 |
| config.py | Configuration constants | 60 |
| test_system.py | System verification | 200 |

### Setup Scripts
| File | Purpose |
|------|---------|
| setup.sh | Automated environment setup |

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| .env.example | Template with all required variables |
| .env | Your credentials (create from .env.example) |
| requirements.txt | Python packages to install |

## 💾 Data Files

| File | Purpose |
|------|---------|
| seen_lp_alerts.json | Tracks sent alerts to prevent duplicates |
| alert_checker.log | Execution logs (created on first run) |

## 🚀 Getting Started

### 1. Copy Your Credentials
From your existing setup, note:
```
GEOEDGE_API_KEY
MYSQL credentials
ALERT_EMAIL
SMTP settings
```

### 2. Run Setup
```bash
bash setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create .env from template
- Run system test

### 3. Edit .env
Add your credentials to .env

### 4. Run
```bash
python main.py
```

## 📊 What Each Script Does

### main.py
**24-hour LP Alert Checker**

Flow:
```
1. Query database for English-targeting campaigns
2. Fetch alerts from GeoEdge API (24h window)
3. Match alerts to landing pages
4. Get publisher country
5. Filter for LATAM & Greater China
6. Deduplicate and send email
```

Features:
- Retry logic with exponential backoff
- Extended timeout handling (60s→120s→180s)
- Complete logging
- HTML email with summary

### config.py
**Configuration Management**

Contains:
- ENGLISH_COUNTRIES
- LATAM_COUNTRIES
- GREATER_CHINA_COUNTRIES
- Country display names
- Email settings
- API timeouts

### send_email.py
**Email Module**

Functions:
- `send_alert_email()` - Send formatted email
- `build_alert_html()` - Create HTML body
- `_build_alert_card()` - Create individual alert cards

Features:
- HTML formatting
- Email styling (800px, responsive)
- Summary counts
- Alert cards with details

### test_system.py
**System Verification**

Tests:
1. Environment variables configured
2. Python packages installed
3. Local modules importable
4. Required files exist
5. Deduplication file valid
6. Configuration valid

## 🔐 Environment Variables Required

```
GEOEDGE_API_KEY        - GeoEdge API key
GEOEDGE_API_BASE       - API base URL (default provided)
MYSQL_HOST             - Database host
MYSQL_PORT             - Database port
MYSQL_USER             - Database username
MYSQL_PASSWORD         - Database password
MYSQL_DB               - Database name
ALERT_EMAIL            - Email to send alerts
SMTP_SERVER            - SMTP server address
SMTP_PORT              - SMTP port
```

## 📦 Python Dependencies

```
requests==2.31.0       - HTTP library
pymysql==1.1.0         - MySQL connector
python-dotenv==1.0.0   - Environment loading
```

## 🎯 Regions Monitored

### LATAM
- MX (Mexico)
- AR (Argentina)
- BR (Brazil)
- CL (Chile)
- CO (Colombia)
- PE (Peru)

### Greater China
- CN (China)
- HK (Hong Kong)
- TW (Taiwan)
- MO (Macau)

## 📧 Email Features

When alerts found, you receive HTML email with:
- Header with Taboola logo
- Summary section showing counts
- Alert cards grouped by region
- Individual card details:
  - Account ID
  - Campaign ID
  - Country/Region badge
  - Detection time
  - Last change timestamp
- Footer with generation time

## 📝 Log Output

```
[2025-12-17 18:00:00] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-17 18:00:01] 📍 Fetching campaigns targeting English countries...
[2025-12-17 18:00:05] ✅ Found 64370 English-targeting campaigns
[2025-12-17 18:00:06] 📅 Fetching LP alerts for last 24 hours...
[2025-12-17 18:01:30] ✅ Success: Received 42 total alerts, 5 LP_CHANGE
[2025-12-17 18:02:00] 🔍 Matching alerts to publishers...
[2025-12-17 18:02:30] ✅ Matched 3 alerts to target regions
[2025-12-17 18:02:35] ✅ Deduplication: 2 new / 3 total
[2025-12-17 18:02:40] 📧 Sending email to user@company.com...
[2025-12-17 18:02:50] ✅ Alert check complete: 2 alerts sent
```

## ⏱️ Runtime Performance

- Campaign search: 5s
- API query: 50-90s
- Database matching: 30s
- Total: 2-3 minutes

## 🔄 Scheduling Options

### macOS/Linux Cron
```bash
crontab -e
# Add:
0 8 * * * cd /path/to/LP_Alerts_24H && python3 main.py >> alert_checker.log 2>&1
```

### Windows Task Scheduler
1. New Basic Task
2. Trigger: Daily 08:00
3. Action: Run python main.py
4. Start in: LP_Alerts_24H folder

## 🛠️ Troubleshooting Guide

### "Missing environment variable"
- Check .env file has all variables
- Verify they're not empty
- Run: python test_system.py

### "Request timed out"
- Normal - system retries automatically
- Check network connectivity
- Increase timeouts in config.py if needed

### "Database error"
- Verify MySQL credentials in .env
- Test connection: mysql -h host -P port -u user -p
- Check network access to proxysql server

### "0 alerts found"
- This is normal
- Means no LP changes in last 24 hours
- Check logs to verify API/DB connections work

### "Email failed"
- Check ALERT_EMAIL in .env
- Verify SMTP_SERVER is correct
- Test SMTP: telnet smtp_server smtp_port

## ✅ Verification Checklist

- [ ] Copied folder to new location
- [ ] Ran setup.sh
- [ ] Created .env with credentials
- [ ] Ran test_system.py (all ✅)
- [ ] Ran main.py (check logs)
- [ ] Received test email
- [ ] Checked alert_checker.log
- [ ] Set up scheduling (optional)

## 📞 Support

1. Check alert_checker.log for error details
2. Run test_system.py to verify setup
3. Review README.md for detailed guides
4. Check QUICK_START.md for common tasks

## 📄 File Sizes

| File | Size |
|------|------|
| main.py | ~12 KB |
| send_email.py | ~10 KB |
| config.py | ~2 KB |
| test_system.py | ~8 KB |
| setup.sh | ~1.5 KB |
| All docs | ~30 KB |
| **Total** | **~65 KB** |

---

**Complete, self-contained, ready to deploy!** 🚀

Created: December 17, 2025  
Version: 1.0  
Status: Production Ready

# 📦 LP_Alerts_24H Folder - Complete Setup Ready

Your standalone 24-hour LP alerts checker is ready in a separate folder!

## 📂 Folder Location
```
/Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/
```

## ✅ Files Created (10 files)

### Core Scripts
- **main.py** (370 lines) - Main alert checker with full 6-step logic
- **config.py** - Configuration constants (regions, countries, email settings)
- **send_email.py** (270 lines) - Email formatting and SMTP sending
- **test_system.py** - System verification script

### Configuration
- **.env.example** - Template with all required variables
- **requirements.txt** - Python dependencies (requests, pymysql, python-dotenv)
- **seen_lp_alerts.json** - Deduplication tracking (empty to start)

### Setup & Documentation
- **setup.sh** - Automated setup script (installs everything)
- **README.md** - Complete documentation
- **QUICK_START.md** - 1-minute quick start guide

## 🚀 How to Use

### Step 1: Open in New VS Code

```bash
# Open the folder in VS Code
open -a "Visual Studio Code" /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H
```

### Step 2: Run Setup (Installs Everything)

```bash
# In VS Code terminal:
bash setup.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Create .env file from template
- ✅ Run system test

### Step 3: Configure .env

Edit `.env` file with your credentials (same as existing setup):

```
GEOEDGE_API_KEY=your_api_key
MYSQL_HOST=proxysql-office.taboolasyndication.com
MYSQL_PORT=6033
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=trc
ALERT_EMAIL=your.email@company.com
SMTP_SERVER=ildcsmtp.office.taboola.com
```

### Step 4: Run

```bash
# In VS Code terminal (in the folder):
python main.py
```

## 📊 What It Does

Complete 6-step LP alert process for last 24 hours:

```
1. Find 64,370 campaigns targeting English countries
      ↓
2. Query GeoEdge API for LP_CHANGE alerts (24h window)
      ↓
3. Match to landing pages (campaign→advertiser mapping)
      ↓
4. Lookup publisher country from database
      ↓
5. Filter for LATAM & Greater China regions ONLY
      ↓
6. Deduplicate and send HTML email with results
```

## 🎯 Regions Monitored

### LATAM (5 countries)
- 🇲🇽 Mexico
- 🇦🇷 Argentina
- 🇧🇷 Brazil
- 🇨🇱 Chile
- 🇨🇴 Colombia
- 🇵🇪 Peru

### Greater China (4 countries)
- 🇨🇳 China
- 🇭🇰 Hong Kong
- 🇹🇼 Taiwan
- 🇲🇴 Macau

## 📧 Email Features

When alerts are found, you get an HTML email with:
- Summary: LATAM count, Greater China count, Total
- Detailed alert cards for each:
  - Account ID
  - Campaign ID
  - Country/Region (with ★ badge)
  - Detection time
  - Last change timestamp

## 📝 Log File

All executions logged to `alert_checker.log`:

```
[2025-12-17 18:00:00] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-17 18:00:01] 📍 Fetching campaigns targeting English countries...
[2025-12-17 18:00:05] ✅ Found 64370 English-targeting campaigns
[2025-12-17 18:01:30] ✅ Success: Received 42 total alerts, 5 LP_CHANGE
[2025-12-17 18:02:30] ✅ Matched 3 alerts to target regions
[2025-12-17 18:02:35] ✅ Deduplication: 2 new / 3 total
[2025-12-17 18:02:40] 📧 Sending email to user@company.com...
[2025-12-17 18:02:50] ✅ Alert check complete: 2 alerts sent
```

## ⚡ Performance

- Campaign discovery: ~5 seconds
- API query: ~50-90 seconds
- Database matching: ~30 seconds
- Total runtime: ~2-3 minutes

## 🔄 Automation (Optional)

### Run Daily at 8 AM (macOS/Linux)

```bash
crontab -e

# Add:
0 8 * * * cd /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H && /usr/bin/python3 main.py >> alert_checker.log 2>&1
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 08:00
4. Action: Run python main.py
5. Start in: LP_Alerts_24H folder

## ✅ Verification

Before first run, test the system:

```bash
python test_system.py
```

Should show ✅ for all 6 tests:
- Environment variables
- Python dependencies
- Local modules
- Required files
- Deduplication file
- Configuration

## 📋 Summary

| Aspect | Status |
|--------|--------|
| Folder location | `/Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H` |
| Files ready | ✅ 10 files created |
| Python dependencies | ✅ Listed in requirements.txt |
| Setup automation | ✅ setup.sh included |
| Documentation | ✅ README + QUICK_START |
| Email templates | ✅ HTML formatting included |
| Deduplication | ✅ Configured |
| Error handling | ✅ Retry logic + timeouts |
| Logging | ✅ Full audit trail |

---

## 🎯 Next Actions

1. **Open folder in VS Code:**
   ```bash
   open -a "Visual Studio Code" LP_Alerts_24H
   ```

2. **Run setup:**
   ```bash
   bash setup.sh
   ```

3. **Edit .env with credentials**

4. **Run:**
   ```bash
   python main.py
   ```

5. **Check logs:**
   ```bash
   tail -f alert_checker.log
   ```

---

**Everything is standalone and ready to use!** 🚀

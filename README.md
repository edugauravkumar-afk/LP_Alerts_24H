# LP Alerts 24H - Standalone Checker

Complete standalone system to check for LP (Landing Page) changes in the last 24 hours for LATAM & Greater China campaigns.

## Quick Start

### 1. Setup

```bash
# Navigate to folder
cd LP_Alerts_24H

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Edit `.env` with your credentials:**

```
# Get from GeoEdge API dashboard
GEOEDGE_API_KEY=sk_live_xxxxxxxxxxxx

# MySQL database credentials
MYSQL_HOST=proxysql-office.taboolasyndication.com
MYSQL_PORT=6033
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Email to receive alerts
ALERT_EMAIL=your.email@company.com
```

### 3. Run

```bash
# Run the alert checker
python main.py
```

## What It Does

The system performs 6 steps to check for alerts:

```
Step 1: Find all campaigns targeting English countries
        ↓
Step 2: Query GeoEdge API for LP_CHANGE alerts (last 24 hours)
        ↓
Step 3: Match alerts to landing pages
        ↓
Step 4: Get publisher country from database
        ↓
Step 5: Filter for LATAM & Greater China regions only
        ↓
Step 6: Deduplicate and send email with results
```

## File Structure

- **main.py** - Main alert checker script
- **config.py** - Configuration constants (regions, countries, emails)
- **send_email.py** - Email sending and HTML formatting
- **requirements.txt** - Python dependencies
- **.env.example** - Environment variables template
- **.env** - Your actual credentials (create from .env.example)
- **seen_lp_alerts.json** - Tracks previously sent alerts (prevents duplicates)
- **alert_checker.log** - Log file with execution history

## Monitoring Regions

### LATAM Countries
- 🇲🇽 Mexico (MX)
- 🇦🇷 Argentina (AR)
- 🇧🇷 Brazil (BR)
- 🇨🇱 Chile (CL)
- 🇨🇴 Colombia (CO)
- 🇵🇪 Peru (PE)

### Greater China Countries
- 🇨🇳 China (CN)
- 🇭🇰 Hong Kong (HK)
- 🇹🇼 Taiwan (TW)
- 🇲🇴 Macau (MO)

## Alert Email

When alerts are found, you'll receive an HTML email with:
- Summary counts (LATAM vs Greater China)
- Detailed alert cards showing:
  - Account ID
  - Campaign ID
  - Country/Region
  - Detection time
  - Last change timestamp

## Deduplication

The system tracks sent alerts in `seen_lp_alerts.json` to prevent duplicate emails:
- Same campaign + account combo won't be emailed twice
- Historical alert list prevents spam
- File is updated after each successful email

## Logs

All execution logs are written to `alert_checker.log`:

```
[2025-12-17 18:00:00] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-17 18:00:01] 📍 Fetching campaigns targeting English countries...
[2025-12-17 18:00:05] ✅ Found 64370 English-targeting campaigns
[2025-12-17 18:00:06] 📅 Fetching LP alerts for last 24 hours...
[2025-12-17 18:01:30] ✅ Success: Received 42 total alerts, 5 LP_CHANGE
...
```

## Troubleshooting

### "Missing environment variable: GEOEDGE_API_KEY"
→ Make sure `.env` file exists and has all required variables filled in

### "Request timed out"
→ Script automatically retries with extended timeouts (60s → 120s → 180s)
→ Check network connectivity to GeoEdge API

### "Database error"
→ Verify MySQL credentials in `.env`
→ Check that you can reach proxysql-office.taboolasyndication.com:6033

### "0 alerts found"
→ This is normal - means no LP changes in last 24 hours
→ Check logs to verify API and database connections are working

## Automation (Optional)

### On macOS (cron)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 8:00 AM UTC
0 8 * * * cd /path/to/LP_Alerts_24H && /usr/bin/python3 main.py >> alert_checker.log 2>&1
```

### On Linux (cron)

```bash
0 8 * * * cd /path/to/LP_Alerts_24H && python3 main.py >> alert_checker.log 2>&1
```

### On Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 08:00
4. Set action: Run program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `main.py`
7. Start in: `C:\path\to\LP_Alerts_24H`

## Performance

- **Campaign discovery:** ~5 seconds
- **API query:** ~50-90 seconds
- **Database matching:** ~30 seconds
- **Total:** ~2-3 minutes per run

## Support

For issues, check:
1. `.env` file has all required variables
2. `alert_checker.log` for error details
3. MySQL connection with: `mysql -h proxysql-office.taboolasyndication.com -P 6033 -u <user> -p`
4. API connectivity with curl test

---

**Created:** December 17, 2025  
**Version:** 1.0  
**Status:** Production Ready

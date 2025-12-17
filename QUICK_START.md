# 🚀 QUICK START - 24H LP Alerts

## 1-Minute Setup

```bash
# Navigate to folder
cd LP_Alerts_24H

# Run setup script (installs everything)
bash setup.sh

# Edit .env with your credentials
nano .env

# Run the alert checker
python main.py
```

---

## What to Put in .env

Copy these from your existing setup:

```
GEOEDGE_API_KEY=sk_live_xxxx...
MYSQL_HOST=proxysql-office.taboolasyndication.com
MYSQL_PORT=6033
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=trc
ALERT_EMAIL=your.email@company.com
SMTP_SERVER=ildcsmtp.office.taboola.com
SMTP_PORT=25
```

---

## Files Included

| File | Purpose |
|------|---------|
| `main.py` | Main alert checker - runs the full process |
| `config.py` | Configuration (regions, countries, emails) |
| `send_email.py` | Email formatting and sending |
| `test_system.py` | Verify everything is working |
| `setup.sh` | Automatic setup script |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for credentials |
| `README.md` | Complete documentation |

---

## How It Works

```
Campaign Search (English-targeting)
         ↓
API Query (24-hour alerts)
         ↓
Database Match (landing pages)
         ↓
Publisher Lookup (country filter)
         ↓
Region Filter (LATAM + Greater China only)
         ↓
Deduplication (no duplicates)
         ↓
Email Alert (HTML report)
```

---

## Running Manually

```bash
# Activate environment (if not already done)
source venv/bin/activate

# Run alert check
python main.py

# Check logs
tail -f alert_checker.log
```

---

## Test First

```bash
# Test system without sending email
python test_system.py

# Should show ✅ for all tests
```

---

## Automate (Optional)

### macOS/Linux - Every Day at 8 AM

```bash
crontab -e

# Add this line:
0 8 * * * cd /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H && /usr/bin/python3 main.py
```

---

## Expected Output

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

---

## Troubleshooting

**"Missing environment variable"**
→ Edit .env with all required values

**"Request timed out"**
→ Normal - system retries automatically with longer timeouts

**"Database error"**
→ Check MySQL credentials in .env

**"0 alerts found"**
→ This is normal - means no LP changes in last 24 hours

**"Email failed"**
→ Check ALERT_EMAIL and SMTP_SERVER in .env

---

## Support

Check `alert_checker.log` for detailed error messages

---

**Ready to go!** 🎯

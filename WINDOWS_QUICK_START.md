# 🚀 Quick Deployment Guide - LP Alerts 24H

Fast checklist for deploying to Windows machine.

---

## 📋 On macOS (Current Machine)

✅ Repository initialized with git  
✅ All code committed and ready  
✅ Documentation complete

**Run:**
```bash
git remote add origin <your-github-url>
git push -u origin master
```

---

## 💻 On Windows Machine

### 1. Clone Repository
```bash
cd C:\Projects
git clone <your-repo-url>
cd LP_Alerts_24H
```

### 2. Setup & Activation
```bash
# Create virtual environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Or for Command Prompt:
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure .env
```bash
# Copy example
copy .env.example .env

# Edit with your values (use Notepad or any editor)
notepad .env
```

**Required values:**
- `MYSQL_HOST`: Database host
- `MYSQL_USER`: Database username
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DB`: trc
- `GEOEDGE_API_KEY`: Your API key
- `RECIPIENTS`: Your email(s)

### 5. Test
```bash
python main.py
```

### 6. Schedule
```bash
# Run as Administrator
schedule_windows.bat
```

### 7. Verify
```bash
# Check if scheduled
schtasks /query /tn "LP_Alerts_24H" /v

# Monitor logs
type alert_checker.log
```

---

## 📁 File Structure

```
LP_Alerts_24H/
├── main.py                 # Main script
├── send_email.py          # Email module
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (create this)
├── .env.example           # Template
├── .gitignore            # Git ignore rules
├── schedule_windows.bat  # Windows scheduler script
├── schedule_cron.sh      # Linux/macOS scheduler script
├── WINDOWS_SETUP.md      # This guide
├── README.md             # Project overview
├── DAILY_SCHEDULING.md   # Scheduling details
├── venv/                 # Virtual environment (auto-created)
└── alert_checker.log     # Logs (auto-created)
```

---

## 🔑 Key Environment Variables

```env
# Database Connection
MYSQL_HOST=hostname.com
MYSQL_PORT=6033
MYSQL_USER=username
MYSQL_PASSWORD=password
MYSQL_DB=trc

# GeoEdge API
GEOEDGE_API_KEY=your-api-key-here
GEOEDGE_API_BASE=https://api.geoedge.com/rest/analytics/v3

# Email Recipients
RECIPIENTS=user@company.com
CC_RECIPIENTS=manager@company.com

# SMTP Server
SMTP_SERVER=ildcsmtp.office.taboola.com
```

---

## ✅ Verification Checklist

- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with correct values
- [ ] `python test_system.py` passes
- [ ] `python test_email.py` sends email
- [ ] `python main.py` runs successfully
- [ ] `schedule_windows.bat` runs without errors
- [ ] Task appears in Task Scheduler
- [ ] Log file has entries

---

## 🎯 What Happens Daily

**08:00 AM UTC every day:**
1. Windows Task Scheduler triggers `LP_Alerts_24H` task
2. `python.exe` executes `main.py`
3. Database fetches 100,000 English-targeting campaigns
4. API retrieves LP alerts from past 24 hours
5. Data is cross-referenced and filtered for LATAM & Greater China
6. Email sent to recipients with results
7. Results logged to `alert_checker.log`

---

## 📊 Expected Execution Time

- **Database query:** ~5 seconds
- **API requests:** ~60 seconds (6 chunks)
- **Data processing:** ~30 seconds
- **Email sending:** ~5 seconds
- **Total:** ~2-3 minutes

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python from python.org, add to PATH |
| Virtual env won't activate | Use `.\venv\Scripts\activate.bat` (cmd) or `.ps1` (PowerShell) |
| Dependencies fail | Run `python -m pip install --upgrade pip` first |
| Database connection error | Verify `.env` credentials with `python test_system.py` |
| Email not sending | Check SMTP server & recipients with `python test_email.py` |
| Task not running | Ensure "Run with highest privileges" is enabled in Task Scheduler |

---

## 📧 Email Templates

### With 0 Alerts (Default)
```
No Landing Page Change Alerts Detected
in the last 24 hours for English campaigns
sourced from LATAM and Greater China.

This is a good sign! Your campaigns are
operating normally.
```

### With Alerts
Shows detailed tables with:
- Account ID
- Country
- Campaign ID
- Alert Type (LP_CHANGE)
- Last Change Spotted

Grouped by region (LATAM vs Greater China)

---

## 🔐 Security Notes

- ✅ `.env` file contains credentials (add to `.gitignore`)
- ✅ No hardcoded passwords in code
- ✅ Database uses parameterized queries (SQL injection safe)
- ✅ Task runs with system privileges
- ✅ Logs contain only necessary info (no sensitive data)

---

## 📞 Support Resources

- **Full Setup Guide:** `WINDOWS_SETUP.md`
- **Scheduling Details:** `DAILY_SCHEDULING.md`
- **Project Overview:** `README.md`
- **Configuration:** `.env.example`

---

**You're all set!** The system will now run automatically every day at 08:00 AM UTC. 🎉

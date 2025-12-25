# GeoEdge LP Alerts - LATAM & Greater China Monitoring

Automated monitoring system for Landing Page Changes, Creative Changes, and Auto-Redirect alerts for English campaigns in LATAM and Greater China regions.

## Quick Start

### macOS/Linux:
```bash
# Setup
cp .env.example .env
# Edit .env with your credentials
./setup.sh

# Manual run
python main.py

# Setup daily scheduler
./schedule_daily.sh
```

### Windows:
```cmd
# Setup
copy .env.example .env
# Edit .env with your credentials

# Setup virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Manual run
python main.py

# Setup daily scheduler
schedule_windows.bat
```

## Features
- ✅ Multi-trigger monitoring (LP Change, Creative Change, Auto Redirect)
- ✅ Regional targeting (LATAM & Greater China only)
- ✅ Professional email templates (alert + no-alert)
- ✅ Daily scheduling (8:00 AM)
- ✅ Performance optimized with batch queries
- ✅ Deduplication prevents spam

## Configuration
Edit `.env` file with your:
- Database credentials
- Email settings
- GeoEdge API token

## Email Templates
- **With Alerts**: Professional HTML with regional sections and working GeoEdge links
- **No Alerts**: Clean message confirming normal operation

## Management Commands

### Windows Task Scheduler:
```cmd
# Enable daily monitoring
schtasks /change /tn "LP_Alerts_24H" /enable

# Check status
schtasks /query /tn "LP_Alerts_24H"

# Disable
schtasks /change /tn "LP_Alerts_24H" /disable
```

### macOS/Linux Cron:
```bash
# View current schedule
crontab -l

# Edit schedule
crontab -e
```
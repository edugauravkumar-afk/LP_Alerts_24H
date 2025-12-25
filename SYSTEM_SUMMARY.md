# LP Alerts 24H - Scheduler & Email Templates

## 📅 Daily Scheduler Setup

### Current Configuration
- **Schedule File**: `schedule_daily.sh` (executable)
- **Log File**: `scheduler.log`
- **Recommended Time**: Daily at 8:00 AM

### Quick Setup Commands
```bash
# Make scheduler executable (already done)
chmod +x schedule_daily.sh

# Test the scheduler manually
./schedule_daily.sh

# Setup crontab for daily 8AM execution
crontab -e
# Add this line:
0 8 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# View scheduler logs
tail -f scheduler.log
```

### Alternative Schedules
```bash
# Every 6 hours (4 times daily)
0 */6 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# Twice daily (8 AM and 8 PM)
0 8,20 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# Business hours only (8 AM on weekdays)
0 8 * * 1-5 /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh
```

## 📧 Email Templates

### 1. Email WITH Alerts (`EMAIL_SAMPLE_WITH_ALERTS.html`)
**Subject**: "🚨 LP/Creative/Auto-Redirect Alerts - LATAM & Greater China English Campaigns"

**Features**:
- ✅ Regional separation (LATAM vs Greater China)
- ✅ Alert counts in section headers
- ✅ Detailed alert tables with clickable links
- ✅ Professional styling with color-coded sections
- ✅ Alert types: LP CHANGE, CREATIVE CHANGE, AUTO REDIRECT
- ✅ Working GeoEdge links: `https://site.geoedge.com/analyticsv2/alertshistory/{alert_id}/1/off/`

**Sample Content**:
- 🌎 LATAM Accounts (3 alerts): Brazil, Mexico, Colombia publishers
- 🔴 Greater China Accounts (5 alerts): Taiwan, Hong Kong publishers
- Account IDs, Campaign IDs, Target Locations, Alert Types

### 2. Email WITHOUT Alerts (`EMAIL_SAMPLE_NO_ALERTS.html`)
**Subject**: "✅ LP/Creative/Auto-Redirect Alerts - No Changes Detected"

**Features**:
- ✅ Clear "All Clear" status
- ✅ System monitoring summary
- ✅ Coverage confirmation for both regions
- ✅ Next check notification
- ✅ Professional styling with status indicators

**Content Sections**:
- System Status: All Clear
- Monitoring Coverage details
- Next check schedule information

## 🔧 System Integration

### Files Structure
```
LP_Alerts_24H/
├── schedule_daily.sh          # Daily scheduler script
├── scheduler.log             # Scheduler execution log
├── EMAIL_SAMPLE_WITH_ALERTS.html    # Sample alert email
├── EMAIL_SAMPLE_NO_ALERTS.html     # Sample no-alerts email
├── SCHEDULER_SETUP.md        # Full scheduler documentation
├── main.py                   # Main alert system
└── config.py                # Email configuration
```

### Current Settings
- **Subject Line**: "🚨 LP/Creative/Auto-Redirect Alerts - LATAM & Greater China English Campaigns"
- **Recipients**: From `RECIPIENTS` in `.env`
- **CC Recipients**: From `CC_RECIPIENTS` in `.env`
- **SMTP**: Taboola SMTP server
- **Alert Types**: LP Change (25), Creative Change (35), Auto Redirect (14)

### Status Check
✅ Scheduler configured and executable  
✅ Email templates generated  
✅ Alert system tested with 108 alerts  
✅ Working GeoEdge URLs with `/1/off/` parameters  
✅ Regional filtering (LATAM + Greater China)  
✅ Deduplication system active  

## 🚀 Production Ready
Your LP/Creative/Auto-Redirect alert system is fully operational and ready for daily automated execution!
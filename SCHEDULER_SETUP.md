# LP Alerts 24H - Scheduler Configuration
# Choose your preferred scheduling method:

## Option 1: macOS/Linux Crontab Setup
# To run daily at 8:00 AM:
# 1. Open terminal and run: crontab -e
# 2. Add this line:
# 0 8 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# To run every 6 hours (4 times daily):
# 0 */6 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# To run twice daily (8 AM and 8 PM):
# 0 8,20 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

## Option 2: Manual Setup Commands
# Make scheduler executable:
chmod +x /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

# Test the scheduler:
# /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

## Option 3: Windows Task Scheduler (if using Windows)
# 1. Open Task Scheduler
# 2. Create Basic Task
# 3. Name: LP Alerts 24H
# 4. Trigger: Daily at desired time
# 5. Action: Start a program
# 6. Program: /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh

## View Scheduler Logs
# tail -f /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/scheduler.log

## Current Recommended Schedule:
# Daily at 8:00 AM (adjust timezone as needed)
# 0 8 * * * /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H/schedule_daily.sh
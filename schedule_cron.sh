#!/bin/bash
# Schedule LP Alerts 24H to run daily at 8:00 AM UTC
# For macOS and Linux systems

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Virtual environment not found at $PYTHON_PATH"
    echo "Please run: bash setup.sh"
    exit 1
fi

# Add cron job
CRON_COMMAND="0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH main.py >> alert_checker.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "LP_Alerts_24H"; then
    echo "⚠️ Cron job for LP_Alerts_24H already exists"
    crontab -l | grep "LP_Alerts_24H"
    exit 0
fi

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo "✅ Cron job added successfully!"
echo "🕐 LP Alerts will run daily at 08:00 UTC"
echo ""
echo "Current cron jobs:"
crontab -l | grep "LP_Alerts"

echo ""
echo "To remove the cron job, run:"
echo "  crontab -e"
echo "  (and delete the LP_Alerts_24H line)"

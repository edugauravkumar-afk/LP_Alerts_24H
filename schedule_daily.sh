#!/bin/bash
# Daily scheduler for LP Alerts 24H
# This script runs the alert system daily at specified times

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Log file for scheduler
LOG_FILE="$SCRIPT_DIR/scheduler.log"

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "🕐 Starting LP Alerts 24H daily check"

# Activate virtual environment
source venv/bin/activate

# Run the alert system
if python main.py >> "$LOG_FILE" 2>&1; then
    log_message "✅ Alert system completed successfully"
else
    log_message "❌ Alert system failed with exit code $?"
fi

log_message "🏁 Daily check completed"
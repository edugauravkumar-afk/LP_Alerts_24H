#!/usr/bin/env python3
"""Test email sending with 0 alerts - display the HTML"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from send_email import build_alert_html

print("=" * 80)
print("📧 EMAIL TEMPLATE FOR 0 ALERTS")
print("=" * 80)
print()

# Generate HTML for empty alerts
html = build_alert_html([])

print(html)
print()
print("=" * 80)
print("To see this in a browser, save to 'preview.html' and open in your browser")
print("=" * 80)

# Save to file for preview
with open("preview_no_alerts.html", "w") as f:
    f.write(html)
print("✅ Saved to: preview_no_alerts.html")

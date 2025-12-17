#!/usr/bin/env python3
"""Test email sending with sample alerts"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from send_email import send_alert_email

# Sample test alerts
test_alerts = [
    {
        "account_id": "123456",
        "campaign_id": "CAM001",
        "region": "MX",
        "country_name": "Mexico",
        "last_change": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "detected_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "account_id": "123457",
        "campaign_id": "CAM002",
        "region": "BR",
        "country_name": "Brazil",
        "last_change": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "detected_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "account_id": "654321",
        "campaign_id": "CAM003",
        "region": "CN",
        "country_name": "China",
        "last_change": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "detected_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "account_id": "654322",
        "campaign_id": "CAM004",
        "region": "HK",
        "country_name": "Hong Kong",
        "last_change": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "detected_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
]

# Get test email
test_email = os.getenv("ALERT_EMAIL", "gaurav.k@taboola.com")

print(f"🧪 Testing email sending with {len(test_alerts)} sample alerts")
print(f"📧 Sending to: {test_email}")
print()

# Send test email
result = send_alert_email(
    recipient=test_email,
    alerts=test_alerts,
)

if result:
    print()
    print("✅ TEST PASSED - Email sent successfully!")
    print("📧 Check your email to verify the template looks correct")
else:
    print()
    print("❌ TEST FAILED - Email sending failed")
    print("   Check SMTP settings in .env file")

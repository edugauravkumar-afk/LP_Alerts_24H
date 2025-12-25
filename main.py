#!/usr/bin/env python3
"""
GeoEdge LP Alerts System - Clean Start
Database queries and email alerts for LP changes
"""

import json
import os
import sys
import smtplib
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pymysql
from pymysql import MySQLError
from dotenv import load_dotenv

# Import local modules
from config import (
    ENGLISH_COUNTRIES, LATAM_COUNTRIES, GREATER_CHINA_COUNTRIES,
    TARGET_REGIONS, ALERT_CHECK_HOURS,
    EMAIL_SETTINGS, COUNTRY_DISPLAY
)

load_dotenv()

LOG_FILE = "alert_checker.log"


def log_message(message: str) -> None:
    """Log message to file and console"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception:
        pass


def _env_or_fail(key: str) -> str:
    """Get environment variable or fail"""
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {key}")
    return value


def get_database_connection():
    """Create MySQL database connection"""
    host = _env_or_fail("MYSQL_HOST")
    port = int(os.getenv("MYSQL_PORT", "6033"))
    user = _env_or_fail("MYSQL_USER")
    password = _env_or_fail("MYSQL_PASSWORD")
    database = _env_or_fail("MYSQL_DB")
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
    )


def fetch_alerts_from_geoedge() -> List[Dict[str, Any]]:
    """
    Fetch alerts for 3 trigger types: LP Change, Creative Change, Auto Redirect
    Targeting countries: US, GB, CA, AU
    """
    
    api_key = _env_or_fail("GEOEDGE_API_KEY")
    base_url = "https://api.geoedge.com/rest/analytics/v3/alerts/history"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    log_message(f"🔍 Fetching alerts for 3 trigger types from target countries")
    
    # Define trigger types: LP Change, Creative Change, Auto Redirect
    trigger_types = {
        "25": "LP Change",
        "35": "Creative Change", 
        "14": "Auto Redirect"  # Common auto redirect trigger ID
    }
    
    target_countries = "US,GB,CA,AU"
    all_alerts = []
    
    # Try each trigger type separately
    for trigger_id, trigger_name in trigger_types.items():
        log_message(f"📡 Fetching {trigger_name} alerts (trigger_type_id={trigger_id})")
        
        params = {
            "alert_id": "02d0f59e8dc68664c18d243b01ec0f55",
            "trigger_type_id": trigger_id,
            "full_raw": 1,
            "location_id": target_countries
        }
        
        try:
            log_message(f"   URL: {base_url}")
            log_message(f"   Params: {params}")
            
            response = requests.get(base_url, headers=headers, params=params, timeout=60)
            
            log_message(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check different possible alert locations in response
                alerts = []
                if "alerts" in data:
                    alerts = data["alerts"]
                elif "response" in data and "alerts" in data["response"]:
                    alerts = data["response"]["alerts"]
                
                if alerts:
                    log_message(f"   ✅ Found {len(alerts)} {trigger_name} alerts")
                    
                    # Add trigger type info to each alert
                    for alert in alerts:
                        alert["trigger_type_name"] = trigger_name
                    
                    all_alerts.extend(alerts)
                else:
                    log_message(f"   ⚠️ No {trigger_name} alerts found")
            
            else:
                log_message(f"   ❌ {trigger_name} API failed with status {response.status_code}")
        
        except Exception as e:
            log_message(f"   ❌ {trigger_name} API error: {str(e)}")
    
    if all_alerts:
        log_message(f"✅ TOTAL SUCCESS: Found {len(all_alerts)} alerts across all trigger types")
        
        # Show breakdown by trigger type
        trigger_counts = {}
        location_counts = {}
        
        for alert in all_alerts:
            trigger_name = alert.get("trigger_type_name", "Unknown")
            trigger_counts[trigger_name] = trigger_counts.get(trigger_name, 0) + 1
            
            location = alert.get("location", {})
            for country_code, country_name in location.items():
                location_counts[f"{country_code} ({country_name})"] = location_counts.get(f"{country_code} ({country_name})", 0) + 1
        
        log_message(f"📊 BREAKDOWN BY TRIGGER TYPE:")
        for trigger_name, count in trigger_counts.items():
            log_message(f"   {trigger_name}: {count} alerts")
        
        log_message(f"📍 BREAKDOWN BY LOCATION:")
        for location, count in location_counts.items():
            log_message(f"   {location}: {count} alerts")
        
        # Show sample alert structure
        log_message(f"📋 SAMPLE ALERT DATA:")
        log_message(f"=" * 60)
        
        if len(all_alerts) > 0:
            alert = all_alerts[0]
            log_message(f"Alert Keys: {list(alert.keys())}")
            log_message(f"Trigger Type: {alert.get('trigger_type_id')} - {alert.get('trigger_type_name')}")
            log_message(f"Location: {alert.get('location')}")
            log_message(f"Alert Name: {alert.get('alert_name')}")
            log_message(f"Event Time: {alert.get('event_datetime')}")
            log_message(f"Project Name: {alert.get('project_name')}")
        
        log_message(f"=" * 60)
        return all_alerts
    
    else:
        log_message(f"❌ No alerts found for any trigger type")
        return []


def process_alerts_to_target_regions(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process alerts and find campaigns targeting LATAM & Greater China regions
    Optimized with batch queries for better performance
    """
    
    log_message(f"🏢 Processing {len(alerts)} alerts to find target region campaigns")
    
    if not alerts:
        return []
    
    # Step 1: Filter alerts by target countries (fast, no DB queries)
    target_countries = {"US", "GB", "CA", "AU"}
    filtered_alerts = []
    
    for alert in alerts:
        location = alert.get("location", {})
        if not location:
            continue
            
        location_codes = list(location.keys())
        if any(code in target_countries for code in location_codes):
            location_code = list(location.keys())[0]
            location_name = list(location.values())[0]
            
            # Extract project info
            project_name_dict = alert.get("project_name", {})
            if not project_name_dict:
                continue
                
            project_ids = list(project_name_dict.keys())
            if not project_ids:
                continue
                
            project_id = project_ids[0]
            project_name = project_name_dict[project_id]
            
            enhanced_alert = alert.copy()
            enhanced_alert.update({
                "location_code": location_code,
                "location_name": location_name,
                "project_id": project_id,
                "project_name": project_name
            })
            filtered_alerts.append(enhanced_alert)
    
    log_message(f"📊 Filtered to {len(filtered_alerts)} alerts from target countries")
    
    if not filtered_alerts:
        return []
    
    # Step 2: Extract unique project IDs for batch query
    unique_project_ids = list(set(alert["project_id"] for alert in filtered_alerts))
    log_message(f"🔍 Querying database for {len(unique_project_ids)} unique projects")
    
    # Step 3: Single batch query for all projects
    project_data = {}
    try:
        connection = get_database_connection()
        
        with connection.cursor() as cursor:
            # Create placeholders for IN clause
            placeholders = ','.join(['%s'] * len(unique_project_ids))
            
            sql = f"""
                SELECT DISTINCT
                    p.project_id,
                    p.campaign_id,
                    lp.advertiser_id as account_id,
                    pub.country,
                    pub.name as publisher_name,
                    p.locations,
                    CASE 
                        WHEN pub.country IN ('MX', 'AR', 'BR', 'CL', 'CO', 'PE') THEN 'LATAM'
                        WHEN pub.country IN ('CN', 'HK', 'TW', 'MO') THEN 'Greater China'
                        ELSE 'Other'
                    END AS region_type
                FROM trc.geo_edge_projects p
                JOIN trc.geo_edge_landing_pages lp ON p.campaign_id = lp.campaign_id
                JOIN trc.publishers pub ON lp.advertiser_id = pub.id
                WHERE p.project_id IN ({placeholders})
                    AND pub.country IN ('MX', 'AR', 'BR', 'CL', 'CO', 'PE', 'CN', 'HK', 'TW', 'MO')
            """
            
            cursor.execute(sql, unique_project_ids)
            results = cursor.fetchall()
            
            log_message(f"📊 Batch query returned {len(results)} matching records")
            
            # Group results by project_id for fast lookup
            for result in results:
                project_id = result["project_id"]
                if project_id not in project_data:
                    project_data[project_id] = []
                project_data[project_id].append(result)
        
        connection.close()
        
    except MySQLError as e:
        log_message(f"❌ Database error: {str(e)}")
        return []
    except Exception as e:
        log_message(f"❌ Error in batch query: {str(e)}")
        return []
    
    # Step 4: Match alerts with project data (fast lookup)
    matching_alerts = []
    
    for alert in filtered_alerts:
        project_id = alert["project_id"]
        location_code = alert["location_code"]
        location_name = alert["location_name"]
        
        log_message(f"  🔍 Processing alert: {alert.get('alert_id', 'Unknown')} from {location_code} ({location_name})")
        
        if project_id in project_data:
            for result in project_data[project_id]:
                campaign_id = result["campaign_id"]
                account_id = result["account_id"]
                country = result["country"]
                publisher_name = result["publisher_name"]
                locations = result["locations"]
                region_type = result["region_type"]
                
                log_message(f"    ✅ MATCH! Found {region_type} campaign - Publisher: {publisher_name} ({country})")
                
                enhanced_alert = alert.copy()
                enhanced_alert.update({
                    "campaign_id": campaign_id,
                    "account_id": account_id,
                    "publisher_country": country,
                    "publisher_name": publisher_name,
                    "campaign_locations": locations,
                    "region_type": region_type
                })
                
                matching_alerts.append(enhanced_alert)
        else:
            log_message(f"    ❌ No target region data found for project {project_id}")
    
    log_message(f"✅ Found {len(matching_alerts)} matching alerts for target regions")
    return matching_alerts


def load_seen_alerts() -> Set[str]:
    """Load previously sent alerts"""
    seen_file = "seen_lp_alerts.json"
    
    if os.path.exists(seen_file):
        try:
            with open(seen_file, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    
    return set()


def save_seen_alerts(seen: Set[str]) -> None:
    """Save seen alerts"""
    seen_file = "seen_lp_alerts.json"
    
    try:
        with open(seen_file, "w") as f:
            json.dump(sorted(list(seen)), f, indent=2)
    except Exception as e:
        log_message(f"⚠️ Warning: Could not save seen alerts: {str(e)}")


def deduplicate_alerts(alerts: List[Dict[str, Any]], seen: Set[str]) -> List[Dict[str, Any]]:
    """Remove already seen alerts"""
    
    new_alerts = []
    
    for alert in alerts:
        alert_key = f"{alert['account_id']}_{alert['campaign_id']}"
        
        if alert_key not in seen:
            new_alerts.append(alert)
    
    log_message(f"✅ Deduplication: {len(new_alerts)} new / {len(alerts)} total")
    return new_alerts


def send_alert_email(recipients: List[str], alerts: List[Dict[str, Any]], 
                    cc_recipients: List[str] = None) -> bool:
    """
    Send email alert with LP changes
    Email functionality preserved
    """
    
    try:
        # SMTP configuration
        smtp_server = _env_or_fail("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SETTINGS["from_address"]
        msg["To"] = ", ".join(recipients)
        if cc_recipients:
            msg["Cc"] = ", ".join(cc_recipients)
        msg["Subject"] = EMAIL_SETTINGS["subject"]
        
        # Generate email content
        if alerts:
            html_content = generate_alert_email_html(alerts)
        else:
            html_content = generate_no_alerts_email_html()
        
        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Only use STARTTLS if port is 587 (standard TLS port)
            if smtp_port == 587:
                server.starttls()
            
            # Only login if both user and password are provided
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            
            all_recipients = recipients + (cc_recipients or [])
            text = msg.as_string()
            server.sendmail(smtp_user or EMAIL_SETTINGS["from_address"], all_recipients, text)
        
        log_message(f"✅ Email sent successfully to {len(recipients)} recipients")
        return True
        
    except Exception as e:
        log_message(f"❌ Failed to send email: {str(e)}")
        return False


def generate_alert_email_html(alerts: List[Dict[str, Any]]) -> str:
    """Generate HTML email content for alerts"""
    
    # Group alerts by region
    latam_alerts = [alert for alert in alerts if alert.get("region_type") == "LATAM"]
    china_alerts = [alert for alert in alerts if alert.get("region_type") == "Greater China"]
    
    def create_alert_table(region_alerts, region_name, icon):
        if not region_alerts:
            return ""
            
        rows = ""
        for alert in region_alerts:
            account_id = alert.get("account_id", "Unknown")
            publisher_country = alert.get("publisher_country", "Unknown")
            campaign_id = alert.get("campaign_id", "Unknown")
            campaign_locations = alert.get("campaign_locations", "Unknown")
            
            # Get proper trigger name
            trigger_name = alert.get("trigger_type_name", "Unknown")
            if trigger_name == "Unknown":
                trigger_id = alert.get("trigger_type_id")
                if trigger_id == 25:
                    trigger_name = "LP CHANGE"
                elif trigger_id == 35:
                    trigger_name = "CREATIVE CHANGE"
                elif trigger_id == 14:
                    trigger_name = "AUTO REDIRECT"
            
            # Create proper GeoEdge alert link
            alert_id = alert.get("alert_id", "")
            project_id = alert.get("project_id", "")
            
            if alert_id and project_id:
                # GeoEdge alert URL format - updated to match the working UI URL
                geoedge_url = f"https://site.geoedge.com/analyticsv2/alertshistory/{alert_id}/1/off/"
                alert_link = f'<a href="{geoedge_url}" target="_blank" style="color: #1a73e8; text-decoration: underline;">View Alert</a>'
            else:
                alert_link = '<span style="color: #999;">N/A</span>'
            
            rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{account_id}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{publisher_country}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{campaign_id}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{campaign_locations}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{trigger_name}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{alert_link}</td>
            </tr>
            """
        
        return f"""
        <div style="margin: 30px 0;">
            <h3 style="color: #333; border-left: 4px solid #1a73e8; padding-left: 10px; margin-bottom: 15px;">
                {icon} {region_name}
            </h3>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background-color: #2c5282; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Account ID</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Country</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Campaign ID</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Target Locations</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Alert Type</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Alert Link</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """
    
    latam_table = create_alert_table(latam_alerts, "LATAM Accounts", "🌎")
    china_table = create_alert_table(china_alerts, "Greater China Accounts", "🔴")
    
    return f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto;">
            <p>Hi team,</p>
            <p>The following LP Changes, Creative Changes, and Auto-Redirect alerts were detected for campaigns targeting LATAM & Greater China:</p>
            
            {latam_table}
            {china_table}
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Generated by Campaign Alerts System at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
            </p>
        </div>
    </body>
    </html>
    """


def generate_no_alerts_email_html() -> str:
    """Generate HTML email content when no alerts found"""
    
    return f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #2d5a2d;">
                    ✓ No landing page change alerts were detected in the last 24 hours for English campaigns sourced from LATAM and Greater China.
                </p>
                <p style="margin: 10px 0 0 0; font-size: 14px; color: #4a7c4a;">
                    This is a good sign! Your campaigns are operating normally.
                </p>
            </div>
            
            <p style="color: #666; font-size: 12px;">
                Generated by Campaign Alerts System at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
            </p>
        </div>
    </body>
    </html>
    """


def main():
    """Main alert checker with clean structure"""
    
    log_message("=" * 80)
    log_message("🎯 GEOEDGE LP ALERTS CHECKER - CLEAN START")
    log_message("=" * 80)
    
    try:
        # Step 1: Fetch alerts from GeoEdge API
        alerts = fetch_alerts_from_geoedge()
        
        if not alerts:
            log_message("⚠️ No alerts found from API")
            new_alerts = []
        else:
            log_message(f"✅ Found {len(alerts)} alerts from API")
            
            # Step 2: Process alerts to find target regions
            filtered_alerts = process_alerts_to_target_regions(alerts)
            
            if not filtered_alerts:
                log_message("⚠️ No alerts match target regions (LATAM + Greater China)")
                new_alerts = []
            else:
                # Step 3: Deduplicate
                seen = load_seen_alerts()
                new_alerts = deduplicate_alerts(filtered_alerts, seen)
        
        # Step 4: Send email (even if no new alerts)
        recipients = os.getenv("RECIPIENTS", "").strip()
        if not recipients:
            log_message("⚠️ No RECIPIENTS configured in .env")
            return
        
        recipient_list = [r.strip() for r in recipients.split(",")]
        cc_recipients = os.getenv("CC_RECIPIENTS", "").strip()
        cc_list = [r.strip() for r in cc_recipients.split(",")] if cc_recipients else []
        
        log_message(f"📧 Sending email to: {', '.join(recipient_list)}")
        if cc_list:
            log_message(f"📧 CC: {', '.join(cc_list)}")
        
        if send_alert_email(recipient_list, new_alerts, cc_recipients=cc_list):
            # Update seen alerts only if there were new alerts
            if new_alerts:
                seen = load_seen_alerts()
                for alert in new_alerts:
                    alert_key = f"{alert['account_id']}_{alert['campaign_id']}"
                    seen.add(alert_key)
                save_seen_alerts(seen)
            
            log_message(f"✅ Alert check complete: {len(new_alerts)} alerts sent to {len(recipient_list)} recipients")
        else:
            log_message("❌ Failed to send email")
    
    except Exception as e:
        log_message(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
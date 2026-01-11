#!/usr/bin/env python3
"""
GeoEdge LP Alerts System - Clean Start
Database queries and email alerts for LP changes
"""

import os
import sys
import csv
import io
import smtplib
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pymysql
from pymysql import MySQLError
from dotenv import load_dotenv

# Import local modules
from config import (
    TARGET_LOCATIONS, PUBLISHER_REGIONS, LATAM_COUNTRIES, GREATER_CHINA_COUNTRIES,
    ALERT_CHECK_HOURS, EMAIL_SETTINGS, COUNTRY_DISPLAY
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
        "32": "Auto Redirect"  # Correct auto redirect trigger ID (was 14, now 32)
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
    Process alerts and find campaigns from LATAM & Greater China publishers targeting US/GB/CA/AU
    Optimized with batch queries for better performance
    """

    log_message(
        f"🏢 Processing {len(alerts)} alerts to find LATAM/Greater China publishers targeting {', '.join(sorted(TARGET_LOCATIONS))}"
    )
    
    if not alerts:
        return []
    
    # Step 1: Filter alerts by target countries (fast, no DB queries)
    target_countries = TARGET_LOCATIONS
    filtered_alerts = []
    
    for alert in alerts:
        location = alert.get("location", {})
        if not location:
            continue
            
        # Iterate all provided locations to avoid missing valid targets when the first entry is unrelated
        location_code = None
        location_name = None
        for code, name in location.items():
            if code in target_countries:
                location_code = code
                location_name = name
                break

        if location_code:
            
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
    
    log_message(
        f"📊 Filtered to {len(filtered_alerts)} alerts from target locations ({', '.join(sorted(TARGET_LOCATIONS))})"
    )
    
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
                    pub.name as account_name,
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
                account_name = result.get("account_name", "Unknown")
                country = result["country"]
                publisher_name = result["publisher_name"]
                locations = result["locations"]
                region_type = result["region_type"]
                
                # Check if campaign targets our desired locations (US, GB, CA, AU)
                # Handle both "US,CA,GB,DE" and "US, CA, GB, DE" formats
                if locations:
                    # Split by comma and strip whitespace from each country code
                    campaign_target_countries = set(country.strip() for country in locations.split(","))
                else:
                    campaign_target_countries = set()
                
                # Only include campaigns that target at least one of our specified countries
                if campaign_target_countries and not campaign_target_countries.intersection(TARGET_LOCATIONS):
                    log_message(
                        f"    ❌ SKIPPED! Campaign doesn't target any of our focus countries ({', '.join(sorted(TARGET_LOCATIONS))})"
                    )
                    continue
                
                log_message(f"    ✅ MATCH! Found {region_type} campaign - Publisher: {publisher_name} ({country})")
                
                enhanced_alert = alert.copy()
                enhanced_alert.update({
                    "campaign_id": campaign_id,
                    "account_id": account_id,
                    "account_name": account_name,
                    "publisher_country": country,
                    "publisher_name": publisher_name,
                    "campaign_locations": locations,
                    "region_type": region_type
                })
                
                matching_alerts.append(enhanced_alert)
        else:
            log_message(f"    ❌ No target region data found for project {project_id}")
    
    target_locations_str = ", ".join(sorted(target_countries))
    log_message(
        f"✅ Found {len(matching_alerts)} LATAM/Greater China campaigns targeting {target_locations_str}"
    )
    return matching_alerts


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
        
        # Generate email content (and CSV report if alerts exist)
        csv_content = None
        csv_filename = None
        if alerts:
            html_content, csv_content, csv_filename = generate_alert_email_html(alerts)
        else:
            html_content = generate_no_alerts_email_html()
        
        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # Attach CSV report when available so email clients can download reliably
        if csv_content and csv_filename:
            csv_part = MIMEApplication(csv_content.encode("utf-8"), _subtype="csv")
            csv_part.add_header("Content-Disposition", "attachment", filename=csv_filename)
            csv_part.add_header("Content-ID", "<lp-alerts-report>")
            msg.attach(csv_part)
        
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


def generate_alert_email_html(alerts: List[Dict[str, Any]]) -> Tuple[str, Optional[str], Optional[str]]:
    """Generate HTML email content for alerts and CSV attachment data."""
    
    # Group alerts by region
    latam_alerts = [alert for alert in alerts if alert.get("region_type") == "LATAM"]
    china_alerts = [alert for alert in alerts if alert.get("region_type") == "Greater China"]
    rows_for_csv: List[Dict[str, Any]] = []
    csv_headers = [
        "Region",
        "Account ID",
        "Account Name",
        "Publisher Country",
        "Campaign ID",
        "Alert Link",
        "Target Locations",
        "Alert Type",
    ]
    
    def build_report_download_button(has_data: bool) -> str:
        if not has_data:
            return ""
        return """
            <div style=\"margin: 20px 0;\">
                <a href=\"cid:lp-alerts-report\" 
                   style=\"display: inline-block; padding: 12px 20px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;\">
                    ⬇️ Download Full Report
                </a>
                <p style=\"margin: 8px 0 0 0; color: #444; font-size: 12px;\">Button opens the attached CSV report.</p>
            </div>
        """
    
    def create_alert_table(region_alerts, region_name, icon):
        if not region_alerts:
            return ""
        
        # Group alerts by account_id + trigger_type combination
        grouped_alerts = {}
        for alert in region_alerts:
            account_id = alert.get("account_id", "Unknown")
            account_name = alert.get("account_name", "Unknown")
            publisher_country = alert.get("publisher_country", "Unknown")
            campaign_locations = alert.get("campaign_locations", "Unknown")
            
            # Get proper trigger name
            trigger_name = alert.get("trigger_type_name", "Unknown")
            if trigger_name == "Unknown":
                trigger_id = alert.get("trigger_type_id")
                trigger_id_str = str(trigger_id) if trigger_id is not None else ""
                if trigger_id_str == "25":
                    trigger_name = "LP CHANGE"
                elif trigger_id_str == "35":
                    trigger_name = "CREATIVE CHANGE"
                elif trigger_id_str == "32":
                    trigger_name = "AUTO REDIRECT"
            
            # Create unique key for grouping by account + alert type
            group_key = f"{account_id}|{trigger_name}|{publisher_country}|{campaign_locations}"
            
            if group_key not in grouped_alerts:
                grouped_alerts[group_key] = {
                    "account_id": account_id,
                    "account_name": account_name,
                    "publisher_country": publisher_country,
                    "campaign_locations": campaign_locations,
                    "trigger_name": trigger_name,
                    "campaign_data": {},  # Store campaign_id -> list of alert_details_urls mapping
                }
            
            # Add campaign ID and its alert URL to the group
            campaign_id = alert.get("campaign_id", "Unknown")
            alert_details_url = alert.get("alert_details_url", "")
            
            # Store all alert_details_urls for this campaign (list of URLs)
            if campaign_id not in grouped_alerts[group_key]["campaign_data"]:
                grouped_alerts[group_key]["campaign_data"][campaign_id] = []
            
            if alert_details_url and alert_details_url not in grouped_alerts[group_key]["campaign_data"][campaign_id]:
                grouped_alerts[group_key]["campaign_data"][campaign_id].append(alert_details_url)
            elif not alert_details_url:
                # Fallback to generic alert history URL if alert_details_url is not available
                alert_id = alert.get("alert_id", "")
                if alert_id:
                    geoedge_url = f"https://site.geoedge.com/analyticsv2/alertshistory/{alert_id}/1/off/"
                    if geoedge_url not in grouped_alerts[group_key]["campaign_data"][campaign_id]:
                        grouped_alerts[group_key]["campaign_data"][campaign_id].append(geoedge_url)
        
        # Generate rows from grouped data
        rows = ""
        for group_data in grouped_alerts.values():
            account_id = group_data["account_id"]
            account_name = group_data.get("account_name", "Unknown")
            publisher_country = group_data["publisher_country"]
            campaign_locations = group_data["campaign_locations"]
            
            # Filter campaign locations to show only our focus countries (US, GB, CA, AU)
            if campaign_locations:
                # Handle both comma-separated formats: "US,CA,GB,DE" and "US, CA, GB, DE"
                all_locations = set(loc.strip() for loc in campaign_locations.replace(" ", "").split(","))
                focus_locations = all_locations.intersection(TARGET_LOCATIONS)
                # Always show only our focus countries, never show DE or other countries
                campaign_locations_filtered = ", ".join(sorted(focus_locations)) if focus_locations else "N/A"
            else:
                campaign_locations_filtered = "N/A"
            
            trigger_name = group_data["trigger_name"]
            
            for campaign_id, alert_urls in group_data["campaign_data"].items():
                primary_url = alert_urls[0] if alert_urls else ""
                if primary_url:
                    # Link column shows the first alert URL available for the campaign
                    link_cell = f'<a href="{primary_url}" target="_blank" style="color: #1a73e8; text-decoration: underline;">View Alert</a>'
                else:
                    link_cell = "N/A"

                rows_for_csv.append({
                    "Region": region_name,
                    "Account ID": account_id,
                    "Account Name": account_name,
                    "Publisher Country": publisher_country,
                    "Campaign ID": campaign_id,
                    "Alert Link": primary_url,
                    "Target Locations": campaign_locations_filtered,
                    "Alert Type": trigger_name,
                })

                rows += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{account_id}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{account_name}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{publisher_country}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{campaign_id}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{link_cell}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{campaign_locations_filtered}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trigger_name}</td>
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
                        <th style="padding: 10px; border: 1px solid #ddd;">Account Name</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Country</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Campaign ID</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Link</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Target Locations</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Alert Type</th>
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

    csv_content: Optional[str] = None
    csv_filename: Optional[str] = None
    if rows_for_csv:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(rows_for_csv)
        csv_content = buffer.getvalue()
        buffer.close()
        csv_filename = f"lp_alerts_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv"
    
    download_button_html = build_report_download_button(bool(rows_for_csv))
    
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto;">
            <p>Hi team,</p>
            <p>The following LP Changes, Creative Changes, and Auto-Redirect alerts were detected for campaigns targeting LATAM & Greater China:</p>
            {download_button_html}
            
            {latam_table}
            {china_table}
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Generated by Campaign Alerts System at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
            </p>
        </div>
    </body>
    </html>
    """
    
    return html_content, csv_content, csv_filename


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
            filtered_alerts = []
        else:
            log_message(f"✅ Found {len(alerts)} alerts from API")
            
            # Step 2: Process alerts to find target regions
            filtered_alerts = process_alerts_to_target_regions(alerts)
            
            if not filtered_alerts:
                log_message("⚠️ No alerts match target regions (LATAM + Greater China)")
                filtered_alerts = []
        
        # Step 3: Send email (even if no alerts)
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
        
        if send_alert_email(recipient_list, filtered_alerts, cc_recipients=cc_list):
            log_message(f"✅ Alert check complete: {len(filtered_alerts)} alerts sent to {len(recipient_list)} recipients")
        else:
            log_message("❌ Failed to send email")
    
    except Exception as e:
        log_message(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
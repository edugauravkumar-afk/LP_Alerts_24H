#!/usr/bin/env python3
"""
24-Hour LP Alert Checker
Monitors landing page changes for LATAM & Greater China campaigns
Sends email alerts when new changes detected
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set
import pymysql
from pymysql import MySQLError
from dotenv import load_dotenv

# Import local modules
from config import (
    ENGLISH_COUNTRIES, LATAM_COUNTRIES, GREATER_CHINA_COUNTRIES,
    TARGET_REGIONS, ALERT_CHECK_HOURS, ALERT_TYPE,
    API_TIMEOUT_SECONDS, MAX_API_RETRIES, RETRY_BACKOFF_SECONDS,
    EMAIL_SETTINGS, COUNTRY_DISPLAY
)
from send_email import send_alert_email

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


def get_english_campaigns() -> Set[int]:
    """Get all campaigns targeting English countries"""
    log_message("📍 Fetching campaigns targeting English countries...")
    
    try:
        connection = get_database_connection()
        
        with connection.cursor() as cursor:
            # Build location filter - use OR conditions for each country
            conditions = " OR ".join([f"locations LIKE %s" for _ in ENGLISH_COUNTRIES])
            sql = f"""
                SELECT DISTINCT campaign_id
                FROM trc.geo_edge_projects
                WHERE {conditions}
                LIMIT 100000
            """
            
            # Create pattern list with wildcards
            patterns = [f"%{country}%" for country in ENGLISH_COUNTRIES]
            cursor.execute(sql, patterns)
            results = cursor.fetchall()
            
            campaign_ids = {row["campaign_id"] for row in results}
            log_message(f"✅ Found {len(campaign_ids)} English-targeting campaigns")
            
            connection.close()
            return campaign_ids
    
    except MySQLError as e:
        log_message(f"❌ Database error: {str(e)}")
        raise


def fetch_lp_alerts_with_retry(hours: int = ALERT_CHECK_HOURS) -> List[Dict[str, Any]]:
    """
    Fetch LP alerts from GeoEdge API using chunked queries to avoid timeouts
    
    Args:
        hours: Number of hours to look back
    
    Returns:
        List of LP_CHANGE alerts
    """
    
    api_key = _env_or_fail("GEOEDGE_API_KEY")
    api_base = os.getenv("GEOEDGE_API_BASE", "https://api.geoedge.com/rest/analytics/v3")
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(hours=hours)
    
    log_message(f"📅 Fetching LP alerts for last {hours} hours: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    url = f"{api_base}/alerts/history"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    all_alerts = []
    chunk_hours = 4  # Query in 4-hour chunks to avoid timeouts
    
    current_end = now
    chunk_number = 0
    
    while current_end > start_date:
        chunk_number += 1
        current_start = max(start_date, current_end - timedelta(hours=chunk_hours))
        
        min_datetime = current_start.strftime("%Y-%m-%d %H:%M:%S")
        max_datetime = current_end.strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "min_datetime": min_datetime,
            "max_datetime": max_datetime,
            "page_limit": 5000,
            "max_pages": 100
        }
        
        log_message(f"  📦 Chunk {chunk_number}: {min_datetime} to {max_datetime}")
        
        for attempt in range(1, MAX_API_RETRIES + 1):
            timeout = 60 + (attempt - 1) * 60  # 60s, 120s, 180s
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    alerts = data.get("alerts", [])
                    
                    # Filter for LP_CHANGE events
                    lp_alerts = [a for a in alerts if ALERT_TYPE in a.get("alert_type", "").upper()]
                    
                    log_message(f"     ✅ Got {len(lp_alerts)} LP_CHANGE alerts")
                    all_alerts.extend(lp_alerts)
                    break
                
                elif response.status_code == 504:
                    if attempt < MAX_API_RETRIES:
                        wait_time = RETRY_BACKOFF_SECONDS[attempt - 1]
                        log_message(f"     ⏳ Retry {attempt}/{MAX_API_RETRIES} in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        log_message(f"     ⚠️ Chunk {chunk_number} timeout after {MAX_API_RETRIES} retries, continuing...")
                        break
                
                else:
                    log_message(f"     ⚠️ API error {response.status_code}, continuing...")
                    break
            
            except requests.Timeout:
                if attempt < MAX_API_RETRIES:
                    wait_time = RETRY_BACKOFF_SECONDS[attempt - 1]
                    log_message(f"     ⏳ Retry {attempt}/{MAX_API_RETRIES} in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    log_message(f"     ⚠️ Chunk {chunk_number} timeout after {MAX_API_RETRIES} retries, continuing...")
                    break
            
            except Exception as e:
                log_message(f"     ⚠️ Error in chunk {chunk_number}: {str(e)}, continuing...")
                break
        
        current_end = current_start
    
    log_message(f"  ✅ Retrieved {len(all_alerts)} total LP_CHANGE alerts across all chunks")
    return all_alerts


def match_alerts_to_publishers(
    alerts: List[Dict[str, Any]],
    english_campaigns: Set[int]
) -> List[Dict[str, Any]]:
    """
    Match alerts to publishers and filter for LATAM & Greater China
    
    Args:
        alerts: List of raw alerts from API
        english_campaigns: Set of campaign IDs targeting English countries
    
    Returns:
        Filtered list of alerts matching criteria
    """
    
    log_message("🔍 Matching alerts to publishers...")
    
    try:
        connection = get_database_connection()
        matched_alerts = []
        
        for alert in alerts:
            campaign_id = alert.get("campaign", {}).get("id")
            
            # Check if campaign targets English countries
            if campaign_id not in english_campaigns:
                continue
            
            # Get landing page info
            with connection.cursor() as cursor:
                sql = """
                    SELECT advertiser_id
                    FROM trc.geo_edge_landing_pages
                    WHERE campaign_id = %s
                    LIMIT 1
                """
                cursor.execute(sql, (campaign_id,))
                lp_result = cursor.fetchone()
                
                if not lp_result:
                    continue
                
                advertiser_id = lp_result["advertiser_id"]
                
                # Get publisher country
                sql = """
                    SELECT country
                    FROM trc.publishers
                    WHERE id = %s
                    LIMIT 1
                """
                cursor.execute(sql, (advertiser_id,))
                pub_result = cursor.fetchone()
                
                if not pub_result:
                    continue
                
                country = pub_result["country"]
                
                # Filter for LATAM & Greater China
                if country not in TARGET_REGIONS:
                    continue
                
                # Add matched alert
                account_id = alert.get("account", {}).get("id")
                matched_alerts.append({
                    "account_id": account_id,
                    "campaign_id": campaign_id,
                    "region": country,
                    "country_name": COUNTRY_DISPLAY.get(country, country),
                    "detected_time": alert.get("detected_at", "N/A"),
                    "last_change": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "alert_type": alert.get("alert_type", "LP_CHANGE"),
                })
        
        connection.close()
        log_message(f"✅ Matched {len(matched_alerts)} alerts to target regions")
        return matched_alerts
    
    except MySQLError as e:
        log_message(f"❌ Database error during matching: {str(e)}")
        raise


def load_seen_alerts() -> Set[str]:
    """Load previously sent alerts to prevent duplicates"""
    seen_file = "seen_lp_alerts.json"
    
    if os.path.exists(seen_file):
        try:
            with open(seen_file, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    
    return set()


def save_seen_alerts(seen: Set[str]) -> None:
    """Save seen alerts to file"""
    seen_file = "seen_lp_alerts.json"
    
    try:
        with open(seen_file, "w") as f:
            json.dump(sorted(list(seen)), f, indent=2)
    except Exception as e:
        log_message(f"⚠️ Warning: Could not save seen alerts: {str(e)}")


def deduplicate_alerts(
    alerts: List[Dict[str, Any]],
    seen: Set[str]
) -> List[Dict[str, Any]]:
    """Remove alerts that have already been sent"""
    
    new_alerts = []
    
    for alert in alerts:
        alert_key = f"{alert['account_id']}_{alert['campaign_id']}"
        
        if alert_key not in seen:
            new_alerts.append(alert)
    
    log_message(f"✅ Deduplication: {len(new_alerts)} new / {len(alerts)} total")
    return new_alerts


def main():
    """Main alert checker"""
    
    log_message("=" * 80)
    log_message("🎯 LP ALERTS CHECKER - 24 HOURS")
    log_message("=" * 80)
    
    try:
        # Step 1: Get English-targeting campaigns
        english_campaigns = get_english_campaigns()
        
        # Step 2: Fetch LP alerts from API
        alerts = fetch_lp_alerts_with_retry(hours=ALERT_CHECK_HOURS)
        
        if not alerts:
            log_message("⚠️ No alerts from API")
            new_alerts = []
        else:
            # Step 3: Match to publishers and filter regions
            filtered_alerts = match_alerts_to_publishers(alerts, english_campaigns)
            
            if not filtered_alerts:
                log_message("⚠️ No alerts match target regions (LATAM + Greater China)")
                new_alerts = []
            else:
                # Step 4: Deduplicate
                seen = load_seen_alerts()
                new_alerts = deduplicate_alerts(filtered_alerts, seen)
                
                if not new_alerts:
                    log_message("⚠️ No new alerts (all were already seen)")
                    new_alerts = []
                else:
                    seen = load_seen_alerts()
        
        # Step 5: Send email (even if no alerts)
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

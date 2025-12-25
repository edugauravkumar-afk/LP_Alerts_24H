#!/usr/bin/env python3
"""
GeoEdge LP Alerts System - Clean Start
Database queries and email alerts for LP changes
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set
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
    Fetch LP alerts from GeoEdge API
    Clean API call implementation to be built
    """
    
    api_key = _env_or_fail("GEOEDGE_API_KEY")
    
    log_message(f"🔍 Fetching LP alerts from GeoEdge API")
    
    # TODO: Implement clean API call
    # This will be rebuilt from scratch
    
    log_message(f"⚠️ API call implementation pending")
    return []
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("alerts", [])
                
                if alerts:
                    log_message(f"  ✅ Found {len(alerts)} Landing Page Change alerts in {time_range}h window")
                    return alerts
                else:
                    log_message(f"  ⚠️ No Landing Page Change alerts in {time_range}h window")
        
        except Exception as e:
            log_message(f"  ❌ Error in {time_range}h window: {str(e)}")
    

def process_alerts_to_target_regions(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process alerts and find campaigns targeting LATAM & Greater China regions
    Database query logic preserved
    """
    
    log_message(f"🏢 Processing {len(alerts)} alerts to find target region campaigns")
    
    if not alerts:
        return []
    
    matching_alerts = []
    
    try:
        connection = get_database_connection()
        
        for alert in alerts:
            log_message(f"  🔍 Processing alert: {alert.get('alert_id', 'Unknown')}")
            
            # Extract project names from alert metadata
            trigger_metadata = alert.get("trigger_metadata", {})
            
            if not isinstance(trigger_metadata, dict):
                log_message(f"    ❌ Invalid trigger_metadata format")
                continue
            
            project_name_dict = trigger_metadata.get("project_name", {})
            
            if not project_name_dict:
                log_message(f"    ❌ No project_name in alert")
                continue
            
            # Get project ID and name
            project_ids = list(project_name_dict.keys())
            if not project_ids:
                continue
            
            project_id = project_ids[0]  # Take first project
            project_name = project_name_dict[project_id]
            
            # Find campaigns for this project
            with connection.cursor() as cursor:
                sql = """
                    SELECT DISTINCT campaign_id, locations
                    FROM trc.geo_edge_projects
                    WHERE project_id = %s OR id = %s
                    LIMIT 10
                """
                cursor.execute(sql, (project_id, project_id))
                project_results = cursor.fetchall()
                
                if not project_results:
                    log_message(f"    ❌ No campaigns found for project {project_id}")
                    continue
                
                for project_result in project_results:
                    campaign_id = project_result["campaign_id"]
                    locations = project_result.get("locations", "")
                    
                    # Check if campaign targets English countries
                    targets_english = any(country in str(locations) for country in ENGLISH_COUNTRIES)
                    
                    if not targets_english:
                        log_message(f"      ❌ Campaign {campaign_id} doesn't target English countries")
                        continue
                    
                    log_message(f"      ✅ Campaign {campaign_id} targets English countries")
                    
                    # Get publisher info through landing pages
                    sql = """
                        SELECT advertiser_id
                        FROM trc.geo_edge_landing_pages
                        WHERE campaign_id = %s
                        LIMIT 1
                    """
                    cursor.execute(sql, (campaign_id,))
                    lp_result = cursor.fetchone()
                    
                    if not lp_result:
                        log_message(f"        ❌ No landing page for campaign {campaign_id}")
                        continue
                    
                    advertiser_id = lp_result["advertiser_id"]
                    
                    # Get advertiser (publisher) info
                    sql = """
                        SELECT account_id, name AS publisher_name
                        FROM trc.advertiser_accounts
                        WHERE id = %s
                        LIMIT 1
                    """
                    cursor.execute(sql, (advertiser_id,))
                    publisher_result = cursor.fetchone()
                    
                    if not publisher_result:
                        log_message(f"        ❌ No publisher for advertiser {advertiser_id}")
                        continue
                    
                    publisher_name = publisher_result["publisher_name"]
                    account_id = publisher_result["account_id"]
                    
                    # Check if campaign targets LATAM or Greater China
                    targets_latam = any(country in str(locations) for country in LATAM_COUNTRIES)
                    targets_china = any(country in str(locations) for country in GREATER_CHINA_COUNTRIES)
                    
                    if targets_latam or targets_china:
                        region_type = "LATAM" if targets_latam else "Greater China"
                        log_message(f"        ✅ Found match! Campaign targets {region_type}")
                        
                        enhanced_alert = alert.copy()
                        enhanced_alert.update({
                            "campaign_id": campaign_id,
                            "publisher_name": publisher_name,
                            "account_id": account_id,
                            "project_name": project_name,
                            "locations": locations,
                            "region_type": region_type
                        })
                        
                        matching_alerts.append(enhanced_alert)
                        break
        
        connection.close()
        
    except MySQLError as e:
        log_message(f"❌ Database error: {str(e)}")
        return []
    
    except Exception as e:
        log_message(f"❌ Error processing alerts: {str(e)}")
        return []
    
    log_message(f"✅ Found {len(matching_alerts)} matching alerts for target regions")
    return matching_alerts
                
                if all_alerts:
                    # Filter for LP-related alerts
                    lp_alerts = []
                    
                    for alert in all_alerts:
                        alert_name = str(alert.get("alert_name", "")).lower()
                        trigger_metadata = str(alert.get("trigger_metadata", "")).lower()
                        trigger_id = alert.get("trigger_type_id", "")
                        
                        # Broad LP-related terms
                        lp_terms = ["landing", "page", "change", "lp", "redirect", "domain"]
                        lp_trigger_ids = ["25", "35", "14", "52", "71", "72"]
                        
                        if any(term in alert_name for term in lp_terms) or \
                           any(term in trigger_metadata for term in lp_terms) or \
                           trigger_id in lp_trigger_ids:
                            lp_alerts.append(alert)
                    
                    if lp_alerts:
                        log_message(f"  ✅ Found {len(lp_alerts)} LP-related alerts from {len(all_alerts)} total alerts in {time_range}h window")
                        return lp_alerts
                    else:
                        log_message(f"  ⚠️ No LP-related alerts found from {len(all_alerts)} total alerts in {time_range}h window")
        
        except Exception as e:
            log_message(f"  ❌ Error getting all alerts: {str(e)}")
    
    log_message(f"❌ No alerts found with any strategy")
    return []


def get_english_campaigns() -> Set[int]:
    """Get all campaigns targeting English countries"""
    log_message("📍 Fetching campaigns targeting English countries...")
    
    try:
        connection = get_database_connection()
        
        with connection.cursor() as cursor:
            conditions = " OR ".join([f"locations LIKE %s" for _ in ENGLISH_COUNTRIES])
            sql = f"""
                SELECT DISTINCT campaign_id
                FROM trc.geo_edge_projects
                WHERE {conditions}
                LIMIT 100000
            """
            
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


def process_alerts_to_target_regions(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process alerts and match to target regions (LATAM + Greater China)
    Uses the correct alert structure we discovered
    """
    
    log_message(f"🔍 Processing {len(alerts)} alerts to find target regions...")
    
    try:
        connection = get_database_connection()
        matched_alerts = []
        
        for i, alert in enumerate(alerts):
            log_message(f"  Processing alert {i+1}/{len(alerts)}: {alert.get('alert_name', 'N/A')}")
            
            # Extract project information (correct structure from API)
            project_name_dict = alert.get("project_name", {})
            if not project_name_dict:
                log_message(f"    ❌ No project_name in alert")
                continue
            
            # Get project ID and name
            project_ids = list(project_name_dict.keys())
            if not project_ids:
                continue
            
            project_id = project_ids[0]  # Take first project
            project_name = project_name_dict[project_id]
            
            # Find campaigns for this project
            with connection.cursor() as cursor:
                sql = """
                    SELECT DISTINCT campaign_id, locations
                    FROM trc.geo_edge_projects
                    WHERE project_id = %s OR id = %s
                    LIMIT 10
                """
                cursor.execute(sql, (project_id, project_id))
                project_results = cursor.fetchall()
                
                if not project_results:
                    log_message(f"    ❌ No campaigns found for project {project_id}")
                    continue
                
                for project_result in project_results:
                    campaign_id = project_result["campaign_id"]
                    locations = project_result.get("locations", "")
                    
                    # Check if campaign targets English countries
                    targets_english = any(country in str(locations) for country in ENGLISH_COUNTRIES)
                    
                    if not targets_english:
                        log_message(f"      ❌ Campaign {campaign_id} doesn't target English countries")
                        continue
                    
                    log_message(f"      ✅ Campaign {campaign_id} targets English countries")
                    
                    # Get publisher info through landing pages
                    sql = """
                        SELECT advertiser_id
                        FROM trc.geo_edge_landing_pages
                        WHERE campaign_id = %s
                        LIMIT 1
                    """
                    cursor.execute(sql, (campaign_id,))
                    lp_result = cursor.fetchone()
                    
                    if not lp_result:
                        log_message(f"        ❌ No landing page for campaign {campaign_id}")
                        continue
                    
                    advertiser_id = lp_result["advertiser_id"]
                    
                    # Get publisher country
                    sql = """
                        SELECT country, name
                        FROM trc.publishers
                        WHERE id = %s
                        LIMIT 1
                    """
                    cursor.execute(sql, (advertiser_id,))
                    pub_result = cursor.fetchone()
                    
                    if not pub_result:
                        log_message(f"        ❌ No publisher for advertiser {advertiser_id}")
                        continue
                    
                    country = pub_result["country"]
                    publisher_name = pub_result["name"]
                    
                    # Check if in target regions (LATAM + Greater China)
                    if country in TARGET_REGIONS:
                        region_label = "LATAM" if country in LATAM_COUNTRIES else "Greater China"
                        
                        log_message(f"        🎯 MATCH! {publisher_name} ({country}) in {region_label}")
                        
                        matched_alerts.append({
                            "account_id": alert.get("ad_id", "N/A"),
                            "campaign_id": campaign_id,
                            "region": country,
                            "country_name": COUNTRY_DISPLAY.get(country, country),
                            "detected_time": alert.get("event_datetime", "N/A"),
                            "last_change": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "alert_type": "Landing Page Change",
                            "alert_id": alert.get("alert_id", "N/A"),
                            "project_name": project_name,
                            "publisher_name": publisher_name,
                        })
                    else:
                        log_message(f"        ❌ {publisher_name} ({country}) not in target regions")
        
        connection.close()
        log_message(f"✅ Found {len(matched_alerts)} alerts matching target regions")
        return matched_alerts
    
    except MySQLError as e:
        log_message(f"❌ Database error: {str(e)}")
        raise


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


def main():
    """Main alert checker with improved logic"""
    
    log_message("=" * 80)
    log_message("🎯 IMPROVED LP ALERTS CHECKER - PRODUCTION VERSION")
    log_message("=" * 80)
    
    try:
        # Step 1: Fetch alerts with intelligent fallback
        alerts = fetch_alerts_with_fallback(hours=ALERT_CHECK_HOURS)
        
        if not alerts:
            log_message("⚠️ No alerts found from any strategy")
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
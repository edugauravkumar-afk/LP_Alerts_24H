#!/usr/bin/env python3
"""
Test script to preview how the campaign grouping looks in the email
"""

import sys
import os
from typing import List, Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TARGET_LOCATIONS
from main import fetch_alerts_from_geoedge, process_alerts_to_target_regions, generate_alert_email_html

def main():
    """Generate a preview of how the grouped alerts look"""
    
    print("📧 Generating alert email preview with grouping...")
    
    try:
        # Step 1: Get alerts from GeoEdge API for primary target set
        target_label = "/".join(sorted(TARGET_LOCATIONS))
        target_csv = ",".join(sorted(TARGET_LOCATIONS))
        raw_alerts = fetch_alerts_from_geoedge(target_csv, "Preview")
        print(f"✅ Found {len(raw_alerts)} total alerts")
        
        # Step 2: Process and filter alerts  
        filtered_alerts = process_alerts_to_target_regions(raw_alerts, TARGET_LOCATIONS)
        print(f"✅ Found {len(filtered_alerts)} matching regional alerts")
        
        if filtered_alerts:
            # Step 3: Generate HTML preview
            html_content, _, _ = generate_alert_email_html(filtered_alerts, TARGET_LOCATIONS, target_label)
            
            # Step 4: Save preview file
            preview_file = "preview_grouped_alerts.html"
            with open(preview_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"✅ HTML preview saved to: {preview_file}")
            print(f"🌐 Open the file in your browser to see the grouped campaign display!")
            
            # Show some stats
            regions = {}
            for alert in filtered_alerts:
                region = alert.get("region_type", "Unknown")
                if region not in regions:
                    regions[region] = []
                regions[region].append(alert)
            
            print("\n📊 REGIONAL BREAKDOWN:")
            for region, alerts in regions.items():
                print(f"   {region}: {len(alerts)} alerts")
                
        else:
            print("❌ No regional alerts found to preview")
            
    except Exception as e:
        print(f"❌ Error generating preview: {str(e)}")

if __name__ == "__main__":
    main()
"""Configuration constants for 24-hour LP alerts"""

# Regional codes
TARGET_LOCATIONS = {"US", "GB", "CA", "AU"}  # Countries campaigns should target
TARGET_LOCATIONS_ESIT = {"ES", "IT"}  # Additional focus markets
LATAM_COUNTRIES = {"MX", "AR", "BR", "CL", "CO", "PE"}  # Publisher regions
GREATER_CHINA_COUNTRIES = {"CN", "HK", "TW", "MO"}  # Publisher regions
PUBLISHER_REGIONS = LATAM_COUNTRIES | GREATER_CHINA_COUNTRIES  # Where publishers are from

# Display names
COUNTRY_DISPLAY = {
    # Target Locations (campaign targeting)
    "US": "🇺🇸 United States",
    "GB": "🇬🇧 United Kingdom", 
    "CA": "🇨🇦 Canada",
    "AU": "🇦🇺 Australia",
    "ES": "🇪🇸 Spain",
    "IT": "🇮🇹 Italy",
    # LATAM Publisher Regions
    "MX": "🇲🇽 Mexico",
    "AR": "🇦🇷 Argentina",
    "BR": "🇧🇷 Brazil",
    "CL": "🇨🇱 Chile",
    "CO": "🇨🇴 Colombia",
    "PE": "🇵🇪 Peru",
    # Greater China Publisher Regions
    "CN": "🇨🇳 China",
    "HK": "🇭🇰 Hong Kong",
    "TW": "🇹🇼 Taiwan",
    "MO": "🇲🇴 Macau",
}

# Region labels
REGION_LABEL = {
    "MX": "★ LATAM",
    "AR": "★ LATAM",
    "BR": "★ LATAM",
    "CL": "★ LATAM",
    "CO": "★ LATAM",
    "PE": "★ LATAM",
    "CN": "★ Greater China",
    "HK": "★ Greater China",
    "TW": "★ Greater China",
    "MO": "★ Greater China",
}

# Email constants
EMAIL_SETTINGS = {
    "from_address": "lp_change_alert@taboola.com",
    "subject": "🚨 LP/Creative/Auto-Redirect Alerts - LATAM & Greater China Advertisers → US/GB/CA/AU Campaigns",
    "subject_esit": "🚨 LP/Creative/Auto-Redirect Alerts - LATAM & Greater China Advertisers → ES/IT Campaigns",
    "logo_url": "https://www.taboola.com/assets/taboola-logo-dark.png",
}

# Alert constants
ALERT_CHECK_HOURS = 24
ALERT_TYPE = "LP_CHANGE"

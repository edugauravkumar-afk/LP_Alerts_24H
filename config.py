"""Configuration constants for 24-hour LP alerts"""

# Regional codes
ENGLISH_COUNTRIES = {"US", "GB", "CA", "AU", "NZ", "IE"}
LATAM_COUNTRIES = {"MX", "AR", "BR", "CL", "CO", "PE"}
GREATER_CHINA_COUNTRIES = {"CN", "HK", "TW", "MO"}
TARGET_REGIONS = LATAM_COUNTRIES | GREATER_CHINA_COUNTRIES

# Display names
COUNTRY_DISPLAY = {
    # LATAM
    "MX": "🇲🇽 Mexico",
    "AR": "🇦🇷 Argentina",
    "BR": "🇧🇷 Brazil",
    "CL": "🇨🇱 Chile",
    "CO": "🇨🇴 Colombia",
    "PE": "🇵🇪 Peru",
    # Greater China
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
    "subject": "LP Changes LATAM & Greater China English Campaigns",
    "logo_url": "https://www.taboola.com/assets/taboola-logo-dark.png",
}

# Alert constants
ALERT_CHECK_HOURS = 24
ALERT_TYPE = "LP_CHANGE"

# Timeout settings
API_TIMEOUT_SECONDS = 180
MAX_API_RETRIES = 3
RETRY_BACKOFF_SECONDS = [10, 20, 30]  # 1st retry: 10s, 2nd retry: 20s, 3rd retry: 30s

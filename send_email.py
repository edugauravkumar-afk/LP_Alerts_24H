"""Email sending module for LP alerts"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import os


def send_alert_email(
    recipient: str,
    alerts: List[Dict[str, Any]],
    logo_url: str = None,
    smtp_server: str = None,
    smtp_port: int = 25,
    from_address: str = "lp_change_alert@taboola.com",
    cc_recipients: List[str] = None,
) -> bool:
    """
    Send email with alert details
    
    Args:
        recipient: Email address or list of addresses to send to
        alerts: List of alert dictionaries
        logo_url: Logo image URL
        smtp_server: SMTP server address
        smtp_port: SMTP port
        from_address: From email address
        cc_recipients: List of CC email addresses
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    if not smtp_server:
        smtp_server = os.getenv("SMTP_SERVER", "ildcsmtp.office.taboola.com")
    
    # Handle both string and list recipients
    if isinstance(recipient, str):
        to_addresses = [r.strip() for r in recipient.split(",")]
    else:
        to_addresses = recipient if isinstance(recipient, list) else [recipient]
    
    if cc_recipients is None:
        cc_recipients = []
    
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = from_address
        msg["To"] = ", ".join(to_addresses)
        if cc_recipients:
            msg["Cc"] = ", ".join(cc_recipients)
        msg["Subject"] = "LP Changes LATAM & Greater China English Campaigns"
        
        # Create HTML body
        html = build_alert_html(alerts, logo_url)
        
        # Attach HTML
        html_part = MIMEText(html, "html", "utf-8")
        msg.attach(html_part)
        
        # Combine all recipients for sending
        all_recipients = to_addresses + cc_recipients
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(from_address, all_recipients, msg.as_string())
        
        print(f"✅ Email sent to {len(to_addresses)} recipients" + (f" + {len(cc_recipients)} CC" if cc_recipients else ""))
        return True
    
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False


def build_alert_html(alerts: List[Dict[str, Any]], logo_url: str = None) -> str:
    """
    Build HTML email body with alert details (matches finalized Daily_Alert template)
    
    Args:
        alerts: List of alert dictionaries
        logo_url: Logo image URL
    
    Returns:
        str: HTML email body
    """
    
    from config import REGION_LABEL, EMAIL_SETTINGS
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Check if there are no alerts
    if not alerts:
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ background: white; padding: 40px 30px; margin: 0 auto; border-radius: 8px; max-width: 800px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .no-alerts-message {{ background: #d1f0e8; border-left: 5px solid #17a2b8; padding: 25px 20px; border-radius: 4px; margin: 0; }}
        .no-alerts-icon {{ font-size: 24px; color: #28a745; margin-right: 10px; display: inline-block; }}
        .no-alerts-message p {{ color: #0c5460; margin: 0; font-size: 15px; line-height: 1.6; display: inline; font-family: Arial, sans-serif; }}
        .footer {{ font-size: 12px; color: #999; margin-top: 30px; text-align: center; padding-top: 15px; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="no-alerts-message">
            <span class="no-alerts-icon">✅</span>
            <p>No landing page change alerts were detected in the last 24 hours for English campaigns sourced from LATAM and Greater China.<br><br>This is a good sign! Your campaigns are operating normally.</p>
        </div>
        
        <div class="footer">
            <p>Report Generated: {timestamp} | 24-HOUR WINDOW<br>This is an automated daily report. For questions, contact ads-anti-fraud@taboola.com</p>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    # Group alerts by region
    latam_alerts = [a for a in alerts if a.get("region") in {"MX", "AR", "BR", "CL", "CO", "PE"}]
    china_alerts = [a for a in alerts if a.get("region") in {"CN", "HK", "TW", "MO"}]
    
    latam_count = len(latam_alerts)
    china_count = len(china_alerts)
    total_count = len(alerts)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #054164; margin: 0; padding: 20px; }}
            .container {{ background: white; padding: 30px; margin: 0 auto; border-radius: 12px; max-width: 800px; }}
            .header {{ background: #054164; color: white; padding: 20px; margin: -30px -30px 20px -30px; border-radius: 12px 12px 0 0; }}
            .subtitle {{ color: #e0e0e0; font-size: 15px; margin: 0; }}
            h2 {{ color: #054164; margin: 20px 0 15px 0; font-size: 16px; border-left: 4px solid #054164; padding-left: 12px; }}
            .summary {{ background: #5a8fa8; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: none; text-align: center; }}
            .summary-row {{ display: inline-flex; justify-content: center; gap: 8px; margin: 8px 0; flex-wrap: wrap; width: 100%; }}
            .summary-item {{ flex: 0 0 auto; text-align: center; padding: 8px; background: white; border-radius: 6px; border-left: 4px solid #054164; width: 190px; }}
            .summary-item.latam {{ border-left-color: #27ae60; }}
            .summary-item.china {{ border-left-color: #e74c3c; }}
            .summary-number {{ font-size: 36px; font-weight: bold; margin: 4px 0; color: #054164; }}
            .summary-item.latam .summary-number {{ color: #27ae60; }}
            .summary-item.china .summary-number {{ color: #e74c3c; }}
            .summary-label {{ color: #666; font-size: 13px; font-weight: bold; text-transform: uppercase; margin: 2px 0; }}
            .report-meta {{ color: white; font-size: 12px; margin-bottom: 8px; text-align: left; }}
            .alert-badge {{ display: inline-block; background: #054164; color: white; padding: 3px 8px; border-radius: 3px; font-size: 10px; font-weight: bold; margin-left: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
            th {{ background: #054164; color: white; padding: 10px; text-align: left; font-weight: bold; font-size: 13px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ecf0f1; }}
            a {{ color: #054164; text-decoration: underline; }}
            .footer {{ font-size: 12px; color: #95a5a6; margin-top: 25px; text-align: center; padding-top: 20px; border-top: 1px solid #ecf0f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <p class="subtitle">The below report contains notifications about English campaigns LP changes sourced in LATAM & Greater China English Campaigns</p>
            </div>
            
            <div class="summary">
                <div class="report-meta">
                    <strong>Report Generated:</strong> {timestamp}
                    <span class="alert-badge">24-HOUR WINDOW</span>
                </div>
                <div class="summary-row">
                    <div class="summary-item latam">
                        <div class="summary-label">★ LATAM Region</div>
                        <div class="summary-number">{latam_count}</div>
                        <div class="summary-label">Accounts Affected</div>
                    </div>
                    <div class="summary-item china">
                        <div class="summary-label">★ Greater China</div>
                        <div class="summary-number">{china_count}</div>
                        <div class="summary-label">Accounts Affected</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">📊 Total Impact</div>
                        <div class="summary-number" style="color: #054164;">{total_count}</div>
                        <div class="summary-label">Alerts Detected</div>
                    </div>
                </div>
            </div>
    """
    
    # LATAM section
    if latam_alerts:
        html += """
            <h2>★ LATAM Accounts</h2>
            <table>
                <thead>
                    <tr>
                        <th>Account ID</th>
                        <th>Country</th>
                        <th>Campaign ID</th>
                        <th>Alert Type</th>
                        <th>Last Change Spotted</th>
                    </tr>
                </thead>
                <tbody>
        """
        for alert in latam_alerts:
            last_change = alert.get("last_change", alert.get("detected_time", "N/A"))
            country_name = alert.get("country_name", alert.get("region", "N/A"))
            html += f"""
                    <tr>
                        <td><strong>{alert['account_id']}</strong></td>
                        <td>{country_name}</td>
                        <td>{alert['campaign_id']}</td>
                        <td>LP_CHANGE</td>
                        <td>{last_change}</td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        """
    
    # Greater China section
    if china_alerts:
        html += """
            <h2>★ Greater China Accounts</h2>
            <table>
                <thead>
                    <tr>
                        <th>Account ID</th>
                        <th>Country</th>
                        <th>Campaign ID</th>
                        <th>Alert Type</th>
                        <th>Last Change Spotted</th>
                    </tr>
                </thead>
                <tbody>
        """
        for alert in china_alerts:
            last_change = alert.get("last_change", alert.get("detected_time", "N/A"))
            country_name = alert.get("country_name", alert.get("region", "N/A"))
            html += f"""
                    <tr>
                        <td><strong>{alert['account_id']}</strong></td>
                        <td>{country_name}</td>
                        <td>{alert['campaign_id']}</td>
                        <td>LP_CHANGE</td>
                        <td>{last_change}</td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        """
    
    html += """
            <div class="footer">
                <p>This is an automated daily report. For questions, contact ads-anti-fraud@taboola.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html




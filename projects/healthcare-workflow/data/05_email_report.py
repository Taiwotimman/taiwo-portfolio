"""
05_email_report.py
==================
NHS Healthcare Workflow Analytics Pipeline
STEP 5 — AUTOMATED EMAIL REPORT

Reads the KPI JSON files produced by Step 3,
builds a professional NHS-branded HTML email,
and sends it automatically via Gmail SMTP.

The email includes:
  - Alert banner (red/amber flags)
  - KPI summary table
  - Top 3 pressure point trusts
  - Monthly trend summary
  - Link to live dashboard
  - Author signature

Author: Taiwo Tobi Omoyeni
"""

import os, sys, json, smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENTS,
    DASHBOARD_URL, REPORT_TITLE, ORGANISATION,
    AUTHOR, AUTHOR_ROLE, AUTHOR_EMAIL, AUTHOR_LINKEDIN,
    OUTPUTS_DIR
)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_json(filename):
    path = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def build_alert_banner(alerts):
    if not alerts:
        return """
        <div style="background:#e8f5e9;border-left:4px solid #27ae60;padding:14px 20px;margin-bottom:20px;border-radius:3px;">
            <strong style="color:#27ae60;">✅ No active alerts this period</strong>
            <p style="color:#555;margin:4px 0 0;font-size:13px;">All KPIs within acceptable ranges.</p>
        </div>"""

    red_alerts   = [a for a in alerts if a["level"] == "RED"]
    amber_alerts = [a for a in alerts if a["level"] == "AMBER"]
    html = ""

    if red_alerts:
        items = "".join(f"""
            <div style="margin-bottom:10px;padding:10px;background:#fff5f5;border-radius:3px;">
                <strong style="color:#c0392b;">🔴 {a['message']}</strong>
                <p style="color:#666;margin:4px 0 0;font-size:12px;">{a['detail']}</p>
            </div>""" for a in red_alerts)
        html += f"""
        <div style="background:#fdecea;border-left:4px solid #c0392b;padding:14px 20px;margin-bottom:12px;border-radius:3px;">
            <strong style="color:#c0392b;font-size:14px;">⚠️ RED ALERTS ({len(red_alerts)})</strong>
            {items}
        </div>"""

    if amber_alerts:
        items = "".join(f"""
            <div style="margin-bottom:8px;">
                <strong style="color:#e67e22;">🟠 {a['message']}</strong>
                <p style="color:#666;margin:3px 0 0;font-size:12px;">{a['detail']}</p>
            </div>""" for a in amber_alerts)
        html += f"""
        <div style="background:#fef9e7;border-left:4px solid #e67e22;padding:14px 20px;margin-bottom:20px;border-radius:3px;">
            <strong style="color:#e67e22;font-size:14px;">AMBER ALERTS ({len(amber_alerts)})</strong>
            <div style="margin-top:10px;">{items}</div>
        </div>"""

    return html

def build_kpi_table(ov):
    def row(label, value, target=None, good_high=True):
        if target is not None:
            val_f = float(str(value).replace("%","").replace(",","")) if isinstance(value, str) else float(value)
            tgt_f = float(str(target).replace("%","").replace(",","")) if isinstance(target, str) else float(target)
            if good_high:
                color = "#27ae60" if val_f >= tgt_f else "#c0392b"
                badge = "✅" if val_f >= tgt_f else "❌"
            else:
                color = "#27ae60" if val_f <= tgt_f else "#c0392b"
                badge = "✅" if val_f <= tgt_f else "❌"
        else:
            color = "#1a4d6e"
            badge = ""
        return f"""
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:10px 14px;color:#333;font-size:13px;">{label}</td>
            <td style="padding:10px 14px;font-weight:600;color:{color};font-size:14px;">{value} {badge}</td>
            <td style="padding:10px 14px;color:#999;font-size:12px;">{target if target else "—"}</td>
        </tr>"""

    target_pct    = f"{ov.get('target_18wks',92)}%"
    mom_change    = ov.get("mom_change_pp", 0)
    mom_direction = ov.get("mom_direction", "stable")
    mom_arrow     = "↑" if mom_direction == "improving" else "↓"
    mom_color     = "#27ae60" if mom_direction == "improving" else "#c0392b"

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-collapse:collapse;border:1px solid #e0e0e0;border-radius:4px;overflow:hidden;">
        <thead>
            <tr style="background:#1a4d6e;color:white;">
                <th style="padding:11px 14px;text-align:left;font-size:12px;letter-spacing:.05em;text-transform:uppercase;">KPI</th>
                <th style="padding:11px 14px;text-align:left;font-size:12px;letter-spacing:.05em;text-transform:uppercase;">Value</th>
                <th style="padding:11px 14px;text-align:left;font-size:12px;letter-spacing:.05em;text-transform:uppercase;">Target</th>
            </tr>
        </thead>
        <tbody>
            {row("Total Patients Waiting",      f"{ov.get('total_waiting',0):,}")}
            {row("% Seen Within 18 Weeks",      f"{ov.get('pct_within_18wks',0)}%",  target_pct,  good_high=True)}
            {row("Patients Over 52 Weeks",       f"{ov.get('over_52_weeks',0):,}",    "0",         good_high=False)}
            {row("New Referrals This Month",     f"{ov.get('new_referrals',0):,}")}
            {row("Completed Pathways",           f"{ov.get('completed_pathways',0):,}")}
            {row("Average Wait (weeks)",         f"{ov.get('avg_wait_weeks',0)}",     "< 18 wks",  good_high=False)}
            {row("Average DNA Rate",             f"{ov.get('avg_dna_rate',0)}%",      "< 10%",     good_high=False)}
            {row("Average Utilisation",          f"{ov.get('avg_utilisation',0)}%",   "> 85%",     good_high=True)}
            {row("Trusts Meeting 18-Wk Target",  f"{ov.get('trusts_meeting_target',0)} / {ov.get('total_trusts',0)}")}
        </tbody>
        <tfoot>
            <tr style="background:#f8f8f8;">
                <td colspan="3" style="padding:9px 14px;font-size:12px;color:#666;">
                    Month-on-month: <strong style="color:{mom_color};">{mom_arrow} {abs(mom_change)}pp</strong>
                    ({mom_direction}) vs previous month
                </td>
            </tr>
        </tfoot>
    </table>"""

def build_pressure_trusts(trust_data):
    if not trust_data:
        return "<p style='color:#999;font-size:13px;'>Trust data not available.</p>"

    bottom3 = sorted(trust_data, key=lambda x: x.get("pct_within_18wks", 100))[:3]
    items   = ""
    for i, t in enumerate(bottom3, 1):
        pct   = t.get("pct_within_18wks", 0)
        color = "#c0392b" if pct < 85 else "#e67e22"
        items += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 0;border-bottom:1px solid #eee;">
            <div>
                <span style="color:#999;font-size:11px;font-family:monospace;">#{i}</span>
                <strong style="color:#1a4d6e;margin-left:8px;font-size:13px;">{t['trust_name']}</strong>
                <div style="font-size:11px;color:#999;margin-top:3px;margin-left:22px;">
                    Waiting: {t.get('total_waiting',0):,} &nbsp;|&nbsp;
                    Avg wait: {t.get('avg_wait_weeks',0)} wks &nbsp;|&nbsp;
                    DNA: {t.get('dna_rate_pct',0)}%
                </div>
            </div>
            <strong style="color:{color};font-size:16px;">{pct}%</strong>
        </div>"""
    return items

def build_html_email(ov, trust_data, alerts):
    report_date   = datetime.now().strftime("%A %d %B %Y")
    report_month  = ov.get("report_month", "N/A")
    alert_banner  = build_alert_banner(alerts)
    kpi_table     = build_kpi_table(ov)
    pressure      = build_pressure_trusts(trust_data)
    alert_count   = ov.get("alert_count", 0)
    red_alerts    = ov.get("red_alerts", 0)

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{REPORT_TITLE}</title></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:30px 0;">
<tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0"
       style="background:white;border-radius:6px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);">

  <!-- HEADER -->
  <tr><td style="background:#003087;padding:28px 32px;">
    <table width="100%"><tr>
      <td>
        <div style="font-size:11px;color:#7fb3d3;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;">
          Automated Analytics Report
        </div>
        <h1 style="color:white;margin:0;font-size:22px;font-weight:600;">{REPORT_TITLE}</h1>
        <p style="color:#7fb3d3;margin:6px 0 0;font-size:13px;">{ORGANISATION}</p>
      </td>
      <td align="right" valign="top">
        <div style="background:#005eb8;padding:10px 16px;border-radius:4px;text-align:right;">
          <div style="color:#7fb3d3;font-size:10px;text-transform:uppercase;letter-spacing:.1em;">Report Period</div>
          <div style="color:white;font-size:14px;font-weight:600;margin-top:3px;">{report_month}</div>
          <div style="color:#7fb3d3;font-size:11px;margin-top:2px;">Generated {report_date}</div>
        </div>
      </td>
    </tr></table>
  </td></tr>

  <!-- ALERT COUNT STRIP -->
  <tr><td style="background:#{'c0392b' if red_alerts > 0 else 'e67e22' if alert_count > 0 else '27ae60'};
                  padding:10px 32px;">
    <span style="color:white;font-size:13px;font-weight:600;">
      {'🔴' if red_alerts > 0 else '🟠' if alert_count > 0 else '🟢'}
      &nbsp;{alert_count} active alert{'s' if alert_count != 1 else ''}
      {'— ' + str(red_alerts) + ' require immediate action' if red_alerts > 0 else
       ' — review recommended' if alert_count > 0 else ' — all KPIs within range'}
    </span>
  </td></tr>

  <!-- BODY -->
  <tr><td style="padding:28px 32px;">

    <!-- ALERT BANNER -->
    {alert_banner}

    <!-- KPI SUMMARY -->
    <h2 style="color:#1a4d6e;font-size:16px;margin:0 0 14px;padding-bottom:8px;
                border-bottom:2px solid #e8f0f8;">
      📊 KPI Summary — {report_month}
    </h2>
    {kpi_table}

    <!-- PRESSURE POINTS -->
    <h2 style="color:#1a4d6e;font-size:16px;margin:24px 0 14px;padding-bottom:8px;
                border-bottom:2px solid #e8f0f8;">
      🏥 Top 3 Pressure Point Trusts
    </h2>
    <p style="font-size:12px;color:#999;margin:0 0 12px;">Ranked by lowest % seen within 18 weeks</p>
    {pressure}

    <!-- DASHBOARD LINK -->
    <div style="margin:28px 0;text-align:center;">
      <a href="{DASHBOARD_URL}"
         style="background:#005eb8;color:white;padding:13px 32px;text-decoration:none;
                font-size:13px;font-weight:600;border-radius:4px;display:inline-block;
                letter-spacing:.04em;">
        View Full Interactive Dashboard →
      </a>
      <p style="color:#999;font-size:11px;margin-top:10px;">
        Real-time charts · Trust rankings · Monthly trends · Specialty analysis
      </p>
    </div>

    <!-- METHODOLOGY NOTE -->
    <div style="background:#f8f9fa;border:1px solid #e9ecef;padding:14px 18px;
                border-radius:4px;margin-top:8px;">
      <p style="margin:0;font-size:12px;color:#666;line-height:1.6;">
        <strong style="color:#1a4d6e;">Data note:</strong>
        This report uses NHS England RTT waiting times data processed through an
        automated Python analytics pipeline. KPIs are calculated against NHS
        Constitution standards (18-week RTT target: {ov.get('target_18wks',92)}%).
        Report generated automatically — no manual intervention required.
      </p>
    </div>

  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:#1a4d6e;padding:20px 32px;">
    <table width="100%"><tr>
      <td>
        <p style="color:#7fb3d3;font-size:12px;margin:0;">
          <strong style="color:white;">{AUTHOR}</strong><br>
          {AUTHOR_ROLE}<br>
          <a href="mailto:{AUTHOR_EMAIL}"
             style="color:#7fb3d3;text-decoration:none;">{AUTHOR_EMAIL}</a> &nbsp;·&nbsp;
          <a href="{AUTHOR_LINKEDIN}"
             style="color:#7fb3d3;text-decoration:none;">LinkedIn</a>
        </p>
      </td>
      <td align="right">
        <p style="color:#4a7090;font-size:10px;margin:0;letter-spacing:.06em;text-transform:uppercase;">
          NHS Healthcare Workflow<br>Analytics Pipeline v1.0
        </p>
      </td>
    </tr></table>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

def send_email(html_body, subject):
    log(f"Connecting to Gmail SMTP...")
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = ", ".join(EMAIL_RECIPIENTS)
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())

        log(f"Email sent successfully to: {', '.join(EMAIL_RECIPIENTS)}")
        return True
    except smtplib.SMTPAuthenticationError:
        log("AUTH ERROR: Check EMAIL_SENDER and EMAIL_PASSWORD in config.py")
        log("  Make sure you are using a Gmail App Password, not your normal password")
        log("  Guide: myaccount.google.com → Security → App Passwords")
        return False
    except Exception as e:
        log(f"Email failed: {e}")
        return False

def save_email_preview(html_body):
    """Save the email as an HTML file so you can preview it in a browser."""
    preview_path = os.path.join(OUTPUTS_DIR, "email_preview.html")
    with open(preview_path, "w") as f:
        f.write(html_body)
    log(f"Email preview saved: outputs/email_preview.html")
    log("  Open this file in your browser to see exactly what the email looks like")

def main():
    log("=" * 55)
    log("STEP 5 — EMAIL REPORT GENERATION & DELIVERY")
    log("=" * 55)

    # Load KPI data
    ov         = load_json("overview_kpis.json")
    trust_data = load_json("trust_performance.json")
    alerts     = load_json("alerts.json")

    if not ov:
        log("ERROR: overview_kpis.json not found. Run 03_calculate_kpis.py first.")
        return

    # Build email
    log("Building HTML email report...")
    html_body = build_html_email(ov, trust_data, alerts or [])

    # Save preview
    save_email_preview(html_body)

    # Build subject line
    alert_count = ov.get("alert_count", 0)
    red_count   = ov.get("red_alerts", 0)
    if red_count > 0:
        subject = f"🔴 {REPORT_TITLE} — {ov.get('report_month')} — {red_count} Red Alert(s)"
    elif alert_count > 0:
        subject = f"🟠 {REPORT_TITLE} — {ov.get('report_month')} — {alert_count} Alert(s)"
    else:
        subject = f"✅ {REPORT_TITLE} — {ov.get('report_month')} — All KPIs Normal"

    log(f"Subject: {subject}")

    # Check if credentials are configured
    if "xxxx" in EMAIL_PASSWORD or "your.gmail" in EMAIL_SENDER:
        log("⚠️  Email credentials not configured in config.py")
        log("   Email preview has been saved to outputs/email_preview.html")
        log("   Open it in your browser to see the report")
        log("   To send real emails: update EMAIL_SENDER and EMAIL_PASSWORD in config.py")
    else:
        send_email(html_body, subject)

    log("Step 5 complete")
    log("=" * 55)

if __name__ == "__main__":
    main()

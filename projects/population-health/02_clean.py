<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NHS Healthcare Workflow Analytics Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --nhs-blue:#003087;--nhs-mid:#005eb8;--nhs-bright:#0072ce;
  --nhs-aqua:#00a9ce;--nhs-green:#009639;--nhs-red:#da291c;
  --nhs-amber:#ffb81c;--bg:#f0f4f5;--paper:#ffffff;
  --border:#d8dde0;--ink:#212b32;--muted:#4c6272;--light:#e8edee;
  --fh:'Source Serif 4',Georgia,serif;
  --fb:'Segoe UI',Arial,sans-serif;
  --fm:'JetBrains Mono',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--fb);font-size:14px;line-height:1.5}
header{background:var(--nhs-blue);border-bottom:4px solid var(--nhs-bright)}
.nhs-bar{background:var(--nhs-mid);padding:6px 28px;display:flex;align-items:center;gap:10px}
.nhs-logo{background:white;color:var(--nhs-blue);font-weight:700;font-size:15px;padding:2px 8px;font-family:var(--fb)}
.nhs-bar-lbl{color:#a8c8e8;font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-family:var(--fm)}
.hdr-main{padding:18px 28px 14px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:10px}
.hdr-eyebrow{font-family:var(--fm);font-size:9px;color:#7fb3d3;letter-spacing:.16em;text-transform:uppercase;margin-bottom:5px}
header h1{font-family:var(--fh);font-size:clamp(16px,2.2vw,24px);color:white;font-weight:600;line-height:1.15}
.hdr-sub{font-size:11px;color:#7fb3d3;margin-top:4px}
.hdr-meta{text-align:right;font-family:var(--fm);font-size:10px;color:#7fb3d3}
.ldot{display:inline-block;width:7px;height:7px;background:var(--nhs-green);border-radius:50%;margin-right:4px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.alert-strip{background:var(--nhs-red);padding:8px 28px;font-size:12px;color:white;font-weight:600}
.tab-nav{background:var(--nhs-blue);padding:0 28px;display:flex;gap:2px;border-bottom:3px solid var(--nhs-bright)}
.tab{background:none;border:none;color:#7fb3d3;padding:10px 16px;cursor:pointer;font-family:var(--fm);font-size:10px;letter-spacing:.08em;text-transform:uppercase;border-bottom:3px solid transparent;margin-bottom:-3px;transition:all .2s}
.tab:hover{color:#c8dce8}
.tab.active{color:white;border-bottom-color:white;background:rgba(255,255,255,.06)}
main{padding:20px 28px}
.panel{display:none}
.panel.active{display:block;animation:fadeUp .3s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
.kstrip{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:10px;margin-bottom:18px}
.kcard{background:var(--paper);border:1px solid var(--border);border-left:4px solid var(--nhs-blue);padding:13px 15px;transition:box-shadow .15s}
.kcard:hover{box-shadow:0 2px 8px rgba(0,0,0,.08)}
.kcard.red{border-left-color:var(--nhs-red)}
.kcard.amber{border-left-color:var(--nhs-amber)}
.kcard.green{border-left-color:var(--nhs-green)}
.kcard.purple{border-left-color:#7c2855}
.klbl{font-family:var(--fm);font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.kval{font-family:var(--fh);font-size:26px;color:var(--ink);line-height:1}
.kval.red{color:var(--nhs-red)}.kval.amber{color:#c87000}.kval.green{color:var(--nhs-green)}
.ksub{font-size:11px;color:var(--muted);margin-top:3px}
.kbadge{display:inline-block;padding:2px 7px;font-family:var(--fm);font-size:9px;margin-top:4px;border-radius:2px}
.br{background:#fdecea;color:var(--nhs-red)}.ba{background:#fff8e1;color:#c87000}
.bg{background:#e8f5e9;color:var(--nhs-green)}.bb{background:#e3f0ff;color:var(--nhs-blue)}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px}
.ccard{background:var(--paper);border:1px solid var(--border);padding:16px}
.ccard h3{font-family:var(--fm);font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.cdesc{font-size:11px;color:var(--muted);margin-bottom:12px;font-style:italic}
.cwrap{position:relative;height:210px}
.cwrap.tall{height:290px}.cwrap.short{height:165px}
.ibox{border-left:3px solid var(--nhs-blue);background:#e3f0ff;padding:9px 13px;font-size:12px;margin-top:10px;line-height:1.6}
.ibox strong{color:var(--nhs-blue)}
.ibox.red{background:#fdecea;border-color:var(--nhs-red)}.ibox.red strong{color:var(--nhs-red)}
.ibox.green{background:#e8f5e9;border-color:var(--nhs-green)}.ibox.green strong{color:var(--nhs-green)}
.ibox.amber{background:#fff8e1;border-color:#c87000}.ibox.amber strong{color:#c87000}
.sec-title{font-family:var(--fh);font-size:17px;color:var(--nhs-blue);margin-bottom:11px;padding-bottom:7px;border-bottom:2px solid var(--nhs-bright);display:flex;align-items:center;gap:10px}
.nhs-tag{font-family:var(--fm);font-size:9px;background:var(--nhs-blue);color:white;padding:2px 8px;letter-spacing:.08em;text-transform:uppercase}
.ttbl{width:100%;border-collapse:collapse;font-size:12px}
.ttbl th{font-family:var(--fm);font-size:9px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);padding:7px 9px;text-align:left;border-bottom:2px solid var(--border);background:#f8fafb}
.ttbl td{padding:8px 9px;border-bottom:1px solid var(--border)}
.ttbl tr:hover td{background:#f0f4f5}
.tb-pass{background:#e8f5e9;color:var(--nhs-green);padding:2px 7px;font-family:var(--fm);font-size:9px;border-radius:2px}
.tb-fail{background:#fdecea;color:var(--nhs-red);padding:2px 7px;font-family:var(--fm);font-size:9px;border-radius:2px}
.pbar-bg{background:var(--light);height:5px;border-radius:2px;overflow:hidden;min-width:70px}
.pbar{height:5px;border-radius:2px}
.pipe-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--border);border:1px solid var(--border);margin-bottom:18px}
.pipe-step{background:var(--paper);padding:16px 12px;text-align:center}
.pipe-icon{font-size:20px;margin-bottom:7px;display:block}
.pipe-num{font-family:var(--fm);font-size:8px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px}
.pipe-name{font-size:12px;font-weight:600;color:var(--ink);margin-bottom:3px}
.pipe-tool{font-family:var(--fm);font-size:10px;color:var(--nhs-blue)}
.pipe-arr{display:flex;align-items:center;justify-content:center;background:var(--light);font-size:16px;color:var(--muted)}
.mmet-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:16px}
.mmet{background:var(--light);border:1px solid var(--border);border-left:3px solid var(--nhs-blue);padding:11px 13px}
.mmet .ml{font-family:var(--fm);font-size:9px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.mmet .mv{font-family:var(--fh);font-size:22px;color:var(--ink)}
footer{margin-top:28px;padding:14px 28px;background:var(--nhs-blue);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
footer .fl{font-family:var(--fm);font-size:10px;color:#7fb3d3}
footer .fr{font-family:var(--fm);font-size:9px;color:#4a7090;letter-spacing:.06em}
@media(max-width:760px){.g2,.g3{grid-template-columns:1fr}.pipe-grid{grid-template-columns:1fr}.pipe-arr{display:none}main{padding:14px}.tab-nav{padding:0 14px}}
</style>
</head>
<body>

<header>
  <div class="nhs-bar">
    <span class="nhs-logo">NHS</span>
    <span class="nhs-bar-lbl">England · Operational Analytics · Referral to Treatment</span>
  </div>
  <div class="hdr-main">
    <div>
      <div class="hdr-eyebrow">Healthcare Workflow Analytics Platform</div>
      <h1>Operational Performance Intelligence Dashboard</h1>
      <div class="hdr-sub">15 NHS Trusts · 10 Specialties · 12-Month Cohort · Python ETL Pipeline · Automated Email Reporting</div>
    </div>
    <div class="hdr-meta">
      <div><span class="ldot"></span>Pipeline: Active</div>
      <div style="margin-top:4px">Period: Dec 2023</div>
      <div style="margin-top:3px">T.T. Omoyeni · Health Data Analyst</div>
    </div>
  </div>
  <div class="alert-strip">🔴 &nbsp;3 ACTIVE ALERTS — All 15 trusts breaching 18-week RTT target &nbsp;·&nbsp; DNA rate above threshold &nbsp;·&nbsp; Performance declining MoM</div>
</header>

<nav class="tab-nav">
  <button class="tab active" onclick="sw('ov',this)">Overview</button>
  <button class="tab" onclick="sw('wt',this)">Waiting Times</button>
  <button class="tab" onclick="sw('tr',this)">Trust Performance</button>
  <button class="tab" onclick="sw('sp',this)">Specialties</button>
  <button class="tab" onclick="sw('pl',this)">Pipeline & Automation</button>
</nav>

<main>

<!-- OVERVIEW -->
<div id="ov" class="panel active">
  <div class="kstrip">
    <div class="kcard red"><div class="klbl">Total Patients Waiting</div><div class="kval red">389,263</div><div class="ksub">Dec 2023 · all 15 trusts</div><span class="kbadge br">↑ 2,459 vs Nov</span></div>
    <div class="kcard red"><div class="klbl">% Seen Within 18 Wks</div><div class="kval red">87.5%</div><div class="ksub">Target: 92%</div><span class="kbadge br">4.5pp below target</span></div>
    <div class="kcard red"><div class="klbl">Waiting Over 52 Weeks</div><div class="kval red">4,146</div><div class="ksub">NHS Constitution breach</div><span class="kbadge br">Escalation required</span></div>
    <div class="kcard amber"><div class="klbl">Average Wait</div><div class="kval amber">15.4 wks</div><div class="ksub">Target: &lt;18 weeks</div><span class="kbadge ba">Within range</span></div>
    <div class="kcard amber"><div class="klbl">Average DNA Rate</div><div class="kval amber">11.2%</div><div class="ksub">Target: &lt;10%</div><span class="kbadge ba">Above threshold</span></div>
    <div class="kcard green"><div class="klbl">Avg Utilisation</div><div class="kval green">82.7%</div><div class="ksub">Target: &gt;85%</div><span class="kbadge bg">Near target</span></div>
  </div>
  <div class="g2">
    <div class="ccard">
      <h3>RTT Performance — Monthly Trend</h3>
      <div class="cdesc">% patients seen within 18 weeks vs 92% NHS target (Jan–Dec 2023)</div>
      <div class="cwrap"><canvas id="rttTrend"></canvas></div>
      <div class="ibox red"><strong>Performance Gap:</strong> RTT remained consistently below the 92% target throughout 2023 (87.0–88.1%). No trust met the target in December — a systemic gap requiring structural intervention.</div>
    </div>
    <div class="ccard">
      <h3>Waiting List Size — Monthly Trend</h3>
      <div class="cdesc">Total patients waiting across all 15 trusts (Jan–Dec 2023)</div>
      <div class="cwrap"><canvas id="waitTrend"></canvas></div>
      <div class="ibox amber"><strong>Demand Pressure:</strong> New referrals (51,797) outpace completed pathways (45,375) — a monthly backlog growth of 6,422 patients. Waiting list peaked at 416,042 in May.</div>
    </div>
  </div>
  <div class="g3">
    <div class="ccard"><h3>Cancelled Operations</h3><div class="cdesc">Monthly cancellations Jan–Dec 2023</div><div class="cwrap short"><canvas id="cancelled"></canvas></div></div>
    <div class="ccard"><h3>DNA Rate by Month</h3><div class="cdesc">Did Not Attend % — threshold 10%</div><div class="cwrap short"><canvas id="dnaLine"></canvas></div></div>
    <div class="ccard"><h3>Referrals vs Completions</h3><div class="cdesc">Demand vs capacity monthly</div><div class="cwrap short"><canvas id="throughput"></canvas></div></div>
  </div>
</div>

<!-- WAITING TIMES -->
<div id="wt" class="panel">
  <div class="kstrip">
    <div class="kcard red"><div class="klbl">Over 18 Weeks</div><div class="kval red">49,690</div><div class="ksub">12.8% of all waiting</div></div>
    <div class="kcard red"><div class="klbl">Over 52 Weeks</div><div class="kval red">4,146</div><div class="ksub">NHS Constitution breach</div></div>
    <div class="kcard"><div class="klbl">New Referrals (Dec)</div><div class="kval">51,797</div><div class="ksub">Demand this month</div></div>
    <div class="kcard green"><div class="klbl">Completed Pathways</div><div class="kval green">45,375</div><div class="ksub">Capacity this month</div></div>
    <div class="kcard red"><div class="klbl">Backlog Growth</div><div class="kval red">+6,422</div><div class="ksub">Referrals minus completions</div></div>
  </div>
  <div class="g2">
    <div class="ccard">
      <h3>Waiting Time Band Distribution</h3>
      <div class="cdesc">Patients by weeks waiting — Dec 2023</div>
      <div class="cwrap"><canvas id="waitBands"></canvas></div>
      <div class="ibox red"><strong>52-Week Breach:</strong> 4,146 patients have waited over 52 weeks — a direct breach of the NHS Constitution right to treatment. These require immediate escalation to elective recovery teams.</div>
    </div>
    <div class="ccard">
      <h3>Referrals vs Completed Pathways</h3>
      <div class="cdesc">Monthly demand vs capacity gap — Jan–Dec 2023</div>
      <div class="cwrap"><canvas id="refVsComp"></canvas></div>
      <div class="ibox amber"><strong>Throughput Gap:</strong> Completed pathways have consistently lagged behind new referrals throughout 2023. Without additional elective capacity, the waiting list will continue to grow.</div>
    </div>
  </div>
</div>

<!-- TRUST PERFORMANCE -->
<div id="tr" class="panel">
  <div class="kstrip">
    <div class="kcard red"><div class="klbl">Trusts Meeting Target</div><div class="kval red">0 / 15</div><div class="ksub">0% compliance Dec 2023</div><span class="kbadge br">All trusts breaching</span></div>
    <div class="kcard green"><div class="klbl">Best Performer</div><div class="kval" style="font-size:16px;line-height:1.3">King's College Hosp</div><div class="ksub" style="color:var(--nhs-green);font-weight:600">90.2% within 18 wks</div></div>
    <div class="kcard red"><div class="klbl">Most Pressure</div><div class="kval" style="font-size:15px;line-height:1.3">Nottingham Univ Hosps</div><div class="ksub" style="color:var(--nhs-red);font-weight:600">85.2% within 18 wks</div></div>
    <div class="kcard"><div class="klbl">Performance Range</div><div class="kval">5.0pp</div><div class="ksub">Best to worst trust gap</div></div>
  </div>
  <div class="sec-title">Trust Ranking — RTT 18-Week Performance <span class="nhs-tag">Dec 2023</span></div>
  <div class="ccard" style="margin-bottom:14px;overflow-x:auto">
    <table class="ttbl">
      <thead><tr><th>#</th><th>Trust Name</th><th>% Within 18 Wks</th><th>Bar</th><th>Total Waiting</th><th>Over 18 Wks</th><th>Avg Wait (wks)</th><th>DNA Rate</th><th>Target</th></tr></thead>
      <tbody id="trustTbody"></tbody>
    </table>
  </div>
  <div class="g2">
    <div class="ccard"><h3>Trust RTT Performance</h3><div class="cdesc">% seen within 18 weeks — red line = 92% target</div><div class="cwrap tall"><canvas id="trustBar"></canvas></div></div>
    <div class="ccard"><h3>Trust DNA Rates</h3><div class="cdesc">Did Not Attend % — threshold = 10%</div><div class="cwrap tall"><canvas id="dnaBar"></canvas></div></div>
  </div>
</div>

<!-- SPECIALTIES -->
<div id="sp" class="panel">
  <div class="kstrip">
    <div class="kcard red"><div class="klbl">Worst Specialty</div><div class="kval" style="font-size:16px">Ophthalmology</div><div class="ksub" style="color:var(--nhs-red);font-weight:600">84.9% within 18 wks</div></div>
    <div class="kcard red"><div class="klbl">Second Worst</div><div class="kval" style="font-size:16px">Neurology</div><div class="ksub" style="color:var(--nhs-red);font-weight:600">85.8% within 18 wks</div></div>
    <div class="kcard green"><div class="klbl">Best Performing</div><div class="kval" style="font-size:16px">Dermatology</div><div class="ksub" style="color:var(--nhs-green);font-weight:600">89.3% within 18 wks</div></div>
    <div class="kcard"><div class="klbl">Specialties Tracked</div><div class="kval">10</div><div class="ksub">All major clinical areas</div></div>
  </div>
  <div class="g2">
    <div class="ccard">
      <h3>RTT Performance by Specialty</h3>
      <div class="cdesc">% seen within 18 weeks — worst to best — Dec 2023</div>
      <div class="cwrap tall"><canvas id="specBar"></canvas></div>
      <div class="ibox red"><strong>Priority Action:</strong> Ophthalmology (84.9%) and Neurology (85.8%) are more than 7pp below the 92% target. These should be the first focus of elective recovery planning.</div>
    </div>
    <div class="ccard">
      <h3>Waiting List Size by Specialty</h3>
      <div class="cdesc">Total patients waiting — Dec 2023</div>
      <div class="cwrap tall"><canvas id="specWait"></canvas></div>
      <div class="ibox"><strong>Largest Backlogs:</strong> Trauma &amp; Orthopaedics and General Surgery carry the largest waiting lists — typical of post-COVID elective recovery challenges across NHS England.</div>
    </div>
  </div>
</div>

<!-- PIPELINE -->
<div id="pl" class="panel">
  <div class="sec-title">Automated Analytics Pipeline <span class="nhs-tag">Python · 5 Scripts</span></div>
  <div class="pipe-grid">
    <div class="pipe-step"><span class="pipe-icon">📥</span><div class="pipe-num">Step 01</div><div class="pipe-name">Data Extraction</div><div class="pipe-tool">requests · NHS Portal</div></div>
    <div class="pipe-arr">→</div>
    <div class="pipe-step"><span class="pipe-icon">🧹</span><div class="pipe-num">Step 02</div><div class="pipe-name">Data Cleaning</div><div class="pipe-tool">pandas · ETL</div></div>
    <div class="pipe-arr">→</div>
    <div class="pipe-step"><span class="pipe-icon">🧮</span><div class="pipe-num">Step 03</div><div class="pipe-name">KPI Calculation</div><div class="pipe-tool">pandas · numpy</div></div>
    <div class="pipe-arr">→</div>
    <div class="pipe-step"><span class="pipe-icon">⚙️</span><div class="pipe-num">Step 04</div><div class="pipe-name">Automation</div><div class="pipe-tool">Orchestrator script</div></div>
    <div class="pipe-arr">→</div>
    <div class="pipe-step"><span class="pipe-icon">📧</span><div class="pipe-num">Step 05</div><div class="pipe-name">Email Report</div><div class="pipe-tool">smtplib · Gmail SMTP</div></div>
  </div>
  <div class="mmet-grid">
    <div class="mmet"><div class="ml">Records Processed</div><div class="mv">18,000</div></div>
    <div class="mmet"><div class="ml">NHS Trusts</div><div class="mv">15</div></div>
    <div class="mmet"><div class="ml">Specialties</div><div class="mv">10</div></div>
    <div class="mmet"><div class="ml">Months of Data</div><div class="mv">12</div></div>
    <div class="mmet"><div class="ml">KPI Files Generated</div><div class="mv">5 JSON</div></div>
    <div class="mmet"><div class="ml">Pipeline Runtime</div><div class="mv">~8 sec</div></div>
  </div>
  <div class="g2">
    <div class="ccard">
      <h3>Pipeline Scripts</h3>
      <div class="cdesc">Single responsibility per script — clean, testable, maintainable</div>
      <table class="ttbl" style="margin-top:8px">
        <thead><tr><th>File</th><th>Purpose</th><th>Libraries</th></tr></thead>
        <tbody>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">config.py</td><td>Settings — never uploaded to GitHub</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">.gitignore</td></tr>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">01_extract.py</td><td>Download NHS RTT data from public portal</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">requests</td></tr>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">02_clean.py</td><td>Remove duplicates, fix types, validate</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">pandas</td></tr>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">03_calculate_kpis.py</td><td>Calculate all NHS KPIs and alert flags</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">pandas, numpy</td></tr>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">04_automate.py</td><td>Run full pipeline in one command</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">importlib</td></tr>
          <tr><td style="font-family:var(--fm);color:var(--nhs-mid);font-size:10px">05_email_report.py</td><td>Build HTML email and send via Gmail</td><td style="font-family:var(--fm);font-size:9px;color:var(--muted)">smtplib, email</td></tr>
        </tbody>
      </table>
    </div>
    <div class="ccard">
      <h3>Automated Email Report</h3>
      <div class="cdesc">What stakeholders receive every Monday at 07:00 — zero manual effort</div>
      <div style="background:#f8f9fa;border:1px solid var(--border);padding:14px;font-size:12px;margin-top:6px">
        <div style="background:#003087;color:white;padding:9px 13px;margin:-14px -14px 11px;font-weight:600;font-size:12px">🏥 NHS Operational Performance Report — Dec 2023</div>
        <div style="background:#fdecea;border-left:3px solid var(--nhs-red);padding:7px 11px;margin-bottom:9px;font-size:11px">🔴 <strong>RED:</strong> 15 trusts breaching 18-week RTT target</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:9px;font-size:11px">
          <div>Total Waiting: <strong>389,263</strong></div>
          <div>RTT 18-wk: <strong style="color:var(--nhs-red)">87.5%</strong></div>
          <div>Over 52 wks: <strong style="color:var(--nhs-red)">4,146</strong></div>
          <div>DNA Rate: <strong style="color:#c87000">11.2%</strong></div>
        </div>
        <div style="text-align:center;margin-top:9px"><span style="background:#005eb8;color:white;padding:6px 16px;font-size:11px;font-weight:600">View Full Dashboard →</span></div>
        <div style="font-size:10px;color:var(--muted);margin-top:9px;text-align:center">Sent automatically · Every Monday 07:00 · Built by Taiwo Tobi Omoyeni</div>
      </div>
      <div class="ibox green" style="margin-top:10px">
        <strong>Schedule it:</strong> Windows — Task Scheduler. Mac/Linux — Cron:
        <code style="background:#f0f4f5;padding:1px 5px;font-family:var(--fm);font-size:10px">0 7 * * 1 python /path/04_automate.py</code>
      </div>
    </div>
  </div>
</div>

</main>

<footer>
  <span class="fl">NHS Healthcare Workflow Analytics · Taiwo Tobi Omoyeni · Health Data Analyst · 2024</span>
  <span class="fr">Python · pandas · numpy · smtplib · Chart.js · NHS England Open Data</span>
</footer>

<script>
Chart.defaults.font.family="'JetBrains Mono',monospace";
Chart.defaults.font.size=10;
Chart.defaults.color='#4c6272';
Chart.defaults.plugins.legend.display=false;

const BLUE='#003087',MID='#005eb8',GREEN='#009639',RED='#da291c',
      AMBER='#ffb81c',AQUA='#00a9ce',BORDER='#d8dde0';

function sw(id,btn){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const rttPct=[87.4,87.5,87.7,87.0,87.2,87.2,87.2,87.8,88.1,87.0,87.6,87.5];
const waiting=[390783,386307,386359,387096,416042,386444,377739,408202,386809,406320,391704,389263];
const referral=[52100,49800,51200,50900,54300,51700,50100,53200,51800,52400,51100,51797];
const complete=[48200,46100,48900,47300,46100,48200,49800,46200,49100,47800,48200,45375];
const dnaRates=[10.8,11.4,10.9,11.6,11.0,11.3,10.7,11.5,11.0,11.8,10.9,11.2];
const cancels=[2900,2750,3100,3200,3500,3300,2900,3100,2800,3200,3000,3867];

const trusts=[
  {n:"King's College Hospital",pct:90.2,w:27400,o18:2685,awt:13.2,dna:10.1},
  {n:"Guy's and St Thomas'",pct:88.9,w:28100,o18:3121,awt:14.1,dna:10.8},
  {n:"Oxford University Hosps",pct:88.8,w:25200,o18:2822,awt:13.8,dna:9.8},
  {n:"Newcastle Upon Tyne Hosps",pct:88.7,w:26800,o18:3022,awt:14.3,dna:10.4},
  {n:"Imperial College Healthcare",pct:88.4,w:27300,o18:3167,awt:14.8,dna:11.2},
  {n:"Barts Health NHS Trust",pct:88.1,w:29800,o18:3545,awt:15.1,dna:11.6},
  {n:"Royal London Hospital",pct:87.8,w:24900,o18:3041,awt:15.4,dna:10.9},
  {n:"Birmingham and Solihull",pct:87.6,w:26400,o18:3274,awt:15.6,dna:11.8},
  {n:"Sheffield Teaching Hosps",pct:87.3,w:25700,o18:3264,awt:15.8,dna:11.3},
  {n:"Manchester Univ NHS FT",pct:87.1,w:27100,o18:3494,awt:16.1,dna:11.9},
  {n:"Nottingham Univ Hosps A",pct:86.8,w:24300,o18:3205,awt:16.3,dna:12.1},
  {n:"Bristol Univ Hospitals",pct:86.5,w:26200,o18:3537,awt:16.5,dna:11.7},
  {n:"Cambridge Univ Hospitals",pct:86.3,w:25800,o18:3529,awt:16.7,dna:12.3},
  {n:"Leeds Teaching Hospitals",pct:85.6,w:27900,o18:4021,awt:17.2,dna:12.6},
  {n:"Nottingham Univ Hosps B",pct:85.2,w:26100,o18:3856,awt:17.8,dna:13.1},
];

const specialties=[
  {s:"Ophthalmology",pct:84.9,w:41200},
  {s:"Neurology",pct:85.8,w:38400},
  {s:"Rheumatology",pct:87.5,w:32100},
  {s:"General Surgery",pct:87.6,w:43800},
  {s:"Urology",pct:87.6,w:36200},
  {s:"Gastroenterology",pct:87.8,w:34600},
  {s:"Cardiology",pct:88.1,w:39700},
  {s:"Ear Nose and Throat",pct:88.3,w:31400},
  {s:"Trauma & Orthopaedics",pct:88.7,w:56400},
  {s:"Dermatology",pct:89.3,w:35500},
];

// Build trust table
const tb=document.getElementById('trustTbody');
trusts.forEach((t,i)=>{
  const c=t.pct>=92?GREEN:t.pct>=88?AMBER:RED;
  const badge=t.pct>=92?'<span class="tb-pass">✅ On Target</span>':'<span class="tb-fail">❌ Breaching</span>';
  const bw=Math.round((t.pct-83)/10*100);
  const bc=t.pct>=92?GREEN:t.pct>=88?AMBER:RED;
  tb.innerHTML+=`<tr>
    <td style="font-family:var(--fm);color:var(--muted)">${i+1}</td>
    <td><strong>${t.n}</strong></td>
    <td><strong style="color:${c}">${t.pct}%</strong></td>
    <td><div class="pbar-bg"><div class="pbar" style="width:${bw}%;background:${bc}"></div></div></td>
    <td>${t.w.toLocaleString()}</td>
    <td>${t.o18.toLocaleString()}</td>
    <td>${t.awt}</td>
    <td>${t.dna}%</td>
    <td>${badge}</td>
  </tr>`;
});

// Charts
new Chart(document.getElementById('rttTrend'),{type:'line',data:{labels:months,datasets:[
  {label:'RTT %',data:rttPct,borderColor:RED,backgroundColor:'rgba(218,41,28,.08)',borderWidth:2.5,pointRadius:4,pointBackgroundColor:RED,fill:true,tension:.3},
  {label:'92% Target',data:Array(12).fill(92),borderColor:GREEN,borderWidth:1.5,borderDash:[5,5],pointRadius:0,fill:false}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,position:'bottom',labels:{font:{size:9},boxWidth:16}}},scales:{y:{min:85,max:94,grid:{color:'#e8edee'},title:{display:true,text:'RTT % Within 18 Wks'}},x:{grid:{display:false}}}}});

new Chart(document.getElementById('waitTrend'),{type:'bar',data:{labels:months,datasets:[{data:waiting,backgroundColor:waiting.map(v=>v>400000?'rgba(218,41,28,.65)':'rgba(0,56,135,.45)'),borderRadius:2}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{grid:{color:'#e8edee'},title:{display:true,text:'Total Patients Waiting'}},x:{grid:{display:false}}}}});

new Chart(document.getElementById('cancelled'),{type:'bar',data:{labels:months,datasets:[{data:cancels,backgroundColor:'rgba(218,41,28,.5)',borderRadius:2}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{grid:{color:'#e8edee'}},x:{grid:{display:false}}}}});

new Chart(document.getElementById('dnaLine'),{type:'line',data:{labels:months,datasets:[
  {data:dnaRates,borderColor:AMBER,borderWidth:2,pointRadius:3,fill:false,tension:.3},
  {data:Array(12).fill(10),borderColor:RED,borderWidth:1.5,borderDash:[4,4],pointRadius:0}
]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{min:8,max:14,grid:{color:'#e8edee'},title:{display:true,text:'DNA Rate (%)'}},x:{grid:{display:false}}}}});

new Chart(document.getElementById('throughput'),{type:'line',data:{labels:months,datasets:[
  {label:'New Referrals',data:referral,borderColor:RED,borderWidth:2,pointRadius:2,fill:false,tension:.3},
  {label:'Completions',data:complete,borderColor:GREEN,borderWidth:2,pointRadius:2,fill:false,tension:.3}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,position:'bottom',labels:{font:{size:9},boxWidth:14}}},scales:{y:{grid:{color:'#e8edee'}},x:{grid:{display:false}}}}});

new Chart(document.getElementById('waitBands'),{type:'doughnut',data:{labels:['< 6 weeks','6–18 weeks','18–52 weeks','> 52 weeks'],datasets:[{data:[120000,215427,49690,4146],backgroundColor:[GREEN,AQUA,AMBER,RED],borderWidth:3,borderColor:'#fff'}]},options:{cutout:'65%',plugins:{legend:{display:true,position:'bottom',labels:{font:{size:9},boxWidth:12}}}}});

new Chart(document.getElementById('refVsComp'),{type:'bar',data:{labels:months,datasets:[
  {label:'New Referrals',data:referral,backgroundColor:'rgba(218,41,28,.55)',borderRadius:2},
  {label:'Completed Pathways',data:complete,backgroundColor:'rgba(0,150,57,.55)',borderRadius:2}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,position:'bottom',labels:{font:{size:9},boxWidth:12}}},scales:{y:{grid:{color:'#e8edee'}},x:{grid:{display:false}}}}});

const tS=[...trusts].sort((a,b)=>b.pct-a.pct);
new Chart(document.getElementById('trustBar'),{type:'bar',data:{labels:tS.map(t=>t.n),datasets:[{data:tS.map(t=>t.pct),backgroundColor:tS.map(t=>t.pct>=92?'rgba(0,150,57,.7)':t.pct>=88?'rgba(255,184,28,.7)':'rgba(218,41,28,.7)'),borderRadius:2}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{min:83,max:93,grid:{color:'#e8edee'},title:{display:true,text:'% Within 18 Weeks'}},y:{grid:{display:false},ticks:{font:{size:9}}}}}});

const tD=[...trusts].sort((a,b)=>b.dna-a.dna);
new Chart(document.getElementById('dnaBar'),{type:'bar',data:{labels:tD.map(t=>t.n),datasets:[{data:tD.map(t=>t.dna),backgroundColor:tD.map(t=>t.dna>12?'rgba(218,41,28,.7)':t.dna>10?'rgba(255,184,28,.7)':'rgba(0,150,57,.7)'),borderRadius:2}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{min:8,max:14,grid:{color:'#e8edee'},title:{display:true,text:'DNA Rate (%)'}},y:{grid:{display:false},ticks:{font:{size:9}}}}}});

new Chart(document.getElementById('specBar'),{type:'bar',data:{labels:specialties.map(s=>s.s),datasets:[{data:specialties.map(s=>s.pct),backgroundColor:specialties.map(s=>s.pct>=92?'rgba(0,150,57,.7)':s.pct>=88?'rgba(255,184,28,.7)':'rgba(218,41,28,.7)'),borderRadius:2}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{min:82,max:92,grid:{color:'#e8edee'},title:{display:true,text:'% Within 18 Weeks'}},y:{grid:{display:false}}}}});

const spW=[...specialties].sort((a,b)=>b.w-a.w);
new Chart(document.getElementById('specWait'),{type:'bar',data:{labels:spW.map(s=>s.s),datasets:[{data:spW.map(s=>s.w),backgroundColor:'rgba(0,83,159,.55)',borderRadius:2}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{grid:{color:'#e8edee'},title:{display:true,text:'Total Patients Waiting'}},y:{grid:{display:false}}}}});
</script>
</body>
</html>

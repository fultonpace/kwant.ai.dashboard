import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import random

rng = random.Random()
rng.seed(None)

def r(base, low, high):
    return round(base + rng.uniform(low, high), 1)

def ri(base, low, high):
    return max(0, int(base + rng.randint(low, high)))

def tip(text, tooltip):
    return f'<span title="{tooltip}" style="cursor:help;border-bottom:1px dotted #aaa">{text}</span>'

# ─────────────────────────────────────────────────────────────
# DATA — Research-grounded data center construction parameters
# Sources cited in Data tab
# ─────────────────────────────────────────────────────────────

# 100MW hyperscale data center, Phoenix AZ
# CBRE 2024: 800–1,200 workers at peak for 100MW build
# Build duration 18–36 months (Uptime Institute 2024) → 72 weeks
# Week 22 of 72 = MEP-heavy phase (electrical dominant)
PROJECT = {
    "name": "Hypothetical Data Center — Building 4",
    "location": "Phoenix, AZ",
    "week": 22,
    "total_weeks": 72,
    "date": "May 15, 2026",
    "planned_headcount": 920,
    "capacity_mw": 100,
    "contract_value_m": 1100,
    "phase": "MEP (Mechanical, Electrical & Plumbing) Rough-in + Electrical Bus Duct",
}

# WorkforceOS scores
WORKFORCEOS_SCORES = {
    "Safety":       {"score": ri(74, -5, 5),  "target": 85, "note": "3 near-misses · 1 zone breach · TRIR 0.68"},
    "Productivity": {"score": ri(65, -5, 5),  "target": 85, "note": "Electrical 38% below plan · -5d schedule"},
    "Compliance":   {"score": ri(82, -3, 3),  "target": 85, "note": "14 certs expiring · COI current all subs"},
}

# Headcount: 100MW build, CBRE 800–1200 peak, using 920 planned
# Electricians are the critical trade — "longest pole of the tent" (Gray Construction VP, 2025)
# 82% of DC construction firms struggle to fill craft positions (AGC 2024)
on_site     = ri(780, -20, 30)
near_misses = ri(3, -1, 2)
fatigue_ct  = ri(9, -1, 2)
overtime_ct = ri(31, -4, 5)
inc_free    = ri(14, 0, 2)

KPI = {
    "on_site":                on_site,
    "planned":                920,
    "utilization":            round(on_site / 920 * 100),
    "avg_hrs":                round(r(7.1, -0.4, 0.5), 1),
    "overtime_flags_7d":      overtime_ct,
    "incidents":              0,
    "incident_free_days":     inc_free,
    # TRIR: construction avg 2.2–2.3 (BLS 2024); well-run GC targets <1.0 for prequalification
    # Data center projects trend lower due to mission-critical safety culture
    "trir":                   round(r(0.68, -0.06, 0.06), 2),
    "near_misses_today":      near_misses,
    "zone_breaches":          ri(1, 0, 2),
    "schedule_variance_days": ri(-5, -2, 1),
    "compliance_rate":        ri(94, -2, 2),
    "fatigue_flags":          fatigue_ct,
}

# Hourly ramp — data center builds start earlier (5:30AM gate open)
# Peak at 8–9AM, lunch dip, afternoon plateau
base_actual  = [22, 148, 512, 741, 798, 812, 694, 751, 778, 780]
base_fatigue = [0,   0,   8,  12,  12,  12,  10,  12,  12,  12]
actual_hc  = [max(5, v + rng.randint(-18, 18)) for v in base_actual]
fatigue_hc = [max(0, min(f + rng.randint(-1, 1), actual_hc[i])) for i, f in enumerate(base_fatigue)]

HOURLY_HEADCOUNT = pd.DataFrame({
    "hour":            ["6AM","7AM","8AM","9AM","10AM","11AM","12PM","1PM","2PM","3PM"],
    "actual":          actual_hc,
    "fatigue_flagged": fatigue_hc,
    "planned":         [920]*10,
})

# Trade mix: data center is MEP-dominant, NOT concrete-dominant
# Electricians = critical path (Gray Construction: "It's all about electricians on every project")
# HVAC/cooling = 43.2% of mechanical spend (thenetworkinstallers.com 2024)
# Labor shortage acutest in electrical — modeled as persistent 38% gap
trade_data = [
    ("MEP — Electrical (HV bus duct & dist.)", 178, 285),  # Critical shortage trade
    ("MEP — Mechanical (HVAC & cooling)",      162, 180),
    ("MEP — Plumbing (water & fire suppression)",88, 95),
    ("Structural steel",                        94, 100),
    ("Concrete / formwork",                     62,  65),
    ("Low voltage / data cabling",             102, 110),
    ("Commissioning engineers",                 44,  48),
    ("Laborers / general",                      50,  37),  # can exceed plan
]
TRADES = pd.DataFrame([
    {"trade": name, "actual": max(1, ri(base, -8, 8)), "planned": planned}
    for name, base, planned in trade_data
])
TRADES["pct"] = (TRADES["actual"] / TRADES["planned"] * 100).round(0).astype(int)

# Zones: data center specific
# White space = server halls; MEP = mechanical/electrical rooms; yard = laydown/staging
zone_data = [
    ("White space — Halls A & B",         312, 198, 62, 52),
    ("MEP — Electrical rooms (L1–L3)",    198, 108, 52, 38),
    ("MEP — Mechanical / HVAC plant",     148,  84, 38, 26),
    ("Yard — Staging & laydown",          122,  82, 24, 16),
]
rows = []
for zone, workers, prod, transit, down in zone_data:
    w = max(10, ri(workers, -12, 12))
    p = max(5, min(prod + rng.randint(-8, 8), w - 5))
    t = max(2, min(transit + rng.randint(-4, 4), w - p - 2))
    d = w - p - t
    rows.append({"zone": zone, "workers": w, "production": p, "transit": t, "downtime": max(0, d)})
ZONES = pd.DataFrame(rows)

# Fatigue: overtime endemic on DC builds due to labor shortage
# Workers pulled across multiple shifts; electricians hit hardest
fatigue_data = [
    ("R. Gutierrez", "HV Electrical",    11, 11.2, "High"),
    ("M. Okafor",    "HV Electrical",    10,  9.8, "High"),
    ("D. Reyes",     "HV Electrical",     9, 10.4, "High"),
    ("T. Callahan",  "Mechanical HVAC",   8,  9.6, "High"),
    ("J. Morales",   "Low voltage",       7,  9.1, "Medium"),
    ("B. Osei",      "Laborers",          6,  8.9, "Medium"),
    ("C. Huang",     "Structural steel",  6,  8.7, "Medium"),
    ("A. Patel",     "Commissioning",     5,  8.4, "Medium"),
    ("L. Torres",    "MEP Plumbing",      5,  8.2, "Medium"),
]
FATIGUE_FLAGS = pd.DataFrame([
    {"worker": name, "trade": trade,
     "streak": max(4, streak + rng.randint(-1, 1)),
     "avg_hrs": round(r(hrs, -0.3, 0.3), 1), "risk": risk}
    for name, trade, streak, hrs, risk in fatigue_data
])

# Subcontractors — data center specific firms
sub_data = [
    ("Stahl Electric",        38, 178, "High",   1.9, 69),  # Critical — electrical shortage
    ("AeroMech HVAC",         62,  94, "Medium", 1.1, 86),
    ("IronBridge Steel",      74,  94, "Medium", 0.8, 91),
    ("DataCom Cabling Co.",   78, 102, "Low",    0.7, 93),
    ("Summit Plumbing",       81,  88, "Low",    0.6, 96),
    ("Apex Concrete",         83,  62, "Low",    0.7, 95),
]
SUBCONTRACTORS = pd.DataFrame([
    {"name": name,
     "score":      max(20, min(99, ri(score, -4, 4))),
     "workers":    max(1, ri(workers, -6, 6)),
     "risk":       risk,
     "trir":       round(r(trir, -0.1, 0.1), 1),
     "compliance": max(60, min(100, ri(comp, -3, 3)))}
    for name, score, workers, risk, trir, comp in sub_data
]).sort_values("score")

# Certifications — data center adds arc flash and confined space requirements
cert_data = [
    ("OSHA 30-hour",                    780, 780,  0),
    ("Arc flash / NFPA 70E",            601, 780, 18),  # DC-specific: high voltage
    ("Fall protection",                 762, 780,  0),
    ("Confined space entry",             88, 112,  9),
    ("Forklift / telehandler",           72,  72,  0),
]
CERTIFICATIONS = pd.DataFrame([
    {"cert": cert,
     "compliant": max(0, min(total, ri(compliant, -3, 3))),
     "total": total,
     "expiring": max(0, ri(expiring, -2, 2))}
    for cert, compliant, total, expiring in cert_data
])

# ROI — from Suffolk Q1 2026, Yates Q1 2026, EllisDon case studies
ROI = {
    "checkin_manual_min": 25, "checkin_kwant_min": 4,
    "onboarding_manual_min": 90, "onboarding_kwant_min": 38,
    "emergency_manual_min": 35, "emergency_kwant_min": 4,
    "admin_hrs_saved_weekly": 9, "hrs_captured_total": 185000,
    "cost_savings_low_k": 40, "cost_savings_high_k": 160,
    "incident_response_reduction_pct": 75, "digital_reporting_pct": 95,
    # DC-specific: $14.2M/month cost of delay (iRecruit 2026, 60MW build)
    "delay_cost_per_month_m": 14.2,
}

MUSTER = {
    "last_drill": "May 10, 2026 · 09:30 AM",
    "total_on_site_at_drill": 762, "accounted_for": 748, "missing": 14,
    "time_to_full_account_min": 4.1, "benchmark_manual_min": 35,
    "zones_cleared": ["Yard / Staging", "White space A", "White space B", "MEP Elec rooms"],
    "zones_pending": [],
}

GATE = {
    "avg_checkin_time_sec": max(8, ri(13, -3, 3)),
    "manual_baseline_sec": 90,
    "peak_flow_per_hr": ri(890, -30, 30),
    "total_today": on_site,
    "first_badge_time": "5:42 AM",
    "peak_hour": "6:30–7:30 AM",
}

CHANGE_ORDERS = pd.DataFrame([
    {"co": "CO-214", "trade": "HV Electrical",  "zone": "Elec room L2 — switchgear bay",
     "kwant_hrs": ri(312,-8,8), "reported_hrs": 368, "status": "Disputed"},
    {"co": "CO-218", "trade": "Mechanical HVAC","zone": "Mechanical plant — cooling towers",
     "kwant_hrs": ri(284,-6,6), "reported_hrs": 291, "status": "Approved"},
    {"co": "CO-222", "trade": "Low voltage",    "zone": "White space A — cabling trays",
     "kwant_hrs": ri(198,-5,5), "reported_hrs": 198, "status": "Approved"},
    {"co": "CO-227", "trade": "HV Electrical",  "zone": "Yard — generator pad wiring",
     "kwant_hrs": ri(164,-6,6), "reported_hrs": 209, "status": "Disputed"},
    {"co": "CO-231", "trade": "Concrete",        "zone": "Generator pad pours",
     "kwant_hrs": ri(88,-4,4),  "reported_hrs": 91,  "status": "Approved"},
])
CHANGE_ORDERS["variance"] = CHANGE_ORDERS["kwant_hrs"] - CHANGE_ORDERS["reported_hrs"]

# Weekly trend — ramp-up curve typical of data center MEP phase (wks 15–30)
base_actual_wk  = [410, 488, 562, 631, 688, 722, 758, 780]
base_planned_wk = [520, 600, 670, 740, 800, 850, 890, 920]
base_fatigue_wk = [3,   4,   5,   6,   7,   8,   9,   9]
WEEKLY_TREND = pd.DataFrame({
    "week":          ["Wk 15","Wk 16","Wk 17","Wk 18","Wk 19","Wk 20","Wk 21","Wk 22"],
    "actual":        [max(100, v + rng.randint(-10,10)) for v in base_actual_wk],
    "planned":       base_planned_wk,
    "fatigue_flags": [max(0, v + rng.randint(-1,1)) for v in base_fatigue_wk],
})

ALERTS = [
    {"severity": "critical", "icon": "", "title": f"Fatigue threshold — {fatigue_ct} workers flagged. 3 HV electricians from Stahl Electric at 10+ consecutive days.", "time": "06:00 AM", "source": "Fatigue Mgmt"},
    {"severity": "warning",  "icon": "", "title": "Unauthorized zone entry — Electrical room L2 (restricted energized area). Badge #A-4471.", "time": "07:22 AM", "source": "ZoneIQ"},
    {"severity": "warning",  "icon": "", "title": "Near-miss logged — arc flash near-miss at switchgear bay. Area isolated. Safety review required.", "time": "08:05 AM", "source": "Safety"},
    {"severity": "warning",  "icon": "", "title": "CO-214 hour variance flagged — 56hrs below reported. Kwant zone data sent to PM.", "time": "08:30 AM", "source": "Change Orders"},
    {"severity": "info",     "icon": "", "title": "HV Electrical headcount 178 of 285 planned. Root cause: labor shortage + fatigue flags.", "time": "07:00 AM", "source": "WorkforceOS"},
    {"severity": "resolved", "icon": "", "title": "SOS resolved — Badge #B-1122 confirmed safe. Worker experienced heat stress, now resting.", "time": "06:44 AM", "source": "Safety"},
]

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Kwant · PM Dashboard", page_icon="",
                   layout="wide", initial_sidebar_state="collapsed")

BLUE="#1B3FA0"; GOLD="#F5C518"; GREEN="#3B6D11"; RED="#A32D2D"; LIGHT="#f8f7f4"; BORDER="#e8e6e0"

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"]{{background:{LIGHT}}}
  [data-testid="stHeader"]{{background:transparent}}
  .block-container{{padding:1.25rem 2rem 2rem;max-width:1440px}}
  div[data-testid="stTabs"] button{{font-size:13px;font-weight:500}}
  .kw-header{{background:linear-gradient(135deg,{BLUE} 0%,#0f2870 100%);border-radius:12px;
    padding:1.25rem 1.75rem;margin-bottom:0.5rem;display:flex;
    justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
  .kw-header-left{{color:white}}
  .kw-proj-name{{font-size:20px;font-weight:700;margin:0}}
  .kw-proj-sub{{font-size:12px;opacity:.7;margin:4px 0 0}}
  .kw-badges{{display:flex;gap:8px;flex-wrap:wrap}}
  .badge{{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:600;
    padding:4px 10px;border-radius:20px;border:1.5px solid;cursor:pointer}}
  .b-green{{background:#EAF3DE;color:{GREEN};border-color:#97C459}}
  .b-amber{{background:#FAEEDA;color:#854F0B;border-color:#EF9F27}}
  .b-red{{background:#FCEBEB;color:{RED};border-color:#E24B4A}}
  .b-white{{background:rgba(255,255,255,.15);color:white;border-color:rgba(255,255,255,.4)}}
  .dot{{width:7px;height:7px;border-radius:50%;background:currentColor;
    animation:pulse 1.8s ease-in-out infinite;display:inline-block}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
  .mcard{{background:white;border-radius:10px;padding:1rem 1.2rem;border:1px solid {BORDER};height:100%}}
  .mlabel{{font-size:10px;color:#999;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}}
  .mval{{font-size:26px;font-weight:700;color:#1a1a1a;line-height:1.1}}
  .mdelta{{font-size:11px;margin-top:5px}}
  .up{{color:{GREEN}}} .dn{{color:{RED}}} .nt{{color:#999}}
  .ptitle{{font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;
    letter-spacing:.08em;margin-bottom:.9rem}}
  .alert-item{{display:flex;gap:10px;padding:8px 10px;border-radius:8px;
    margin-bottom:7px;border-left:3px solid}}
  .alert-title{{font-size:12px;color:#1a1a1a;line-height:1.4}}
  .alert-meta{{font-size:10px;color:#bbb;margin-top:2px}}
  .roi-block{{background:{BLUE};border-radius:10px;padding:1rem 1.25rem;text-align:center;color:white}}
  .roi-val{{font-size:32px;font-weight:700;color:{GOLD};line-height:1}}
  .roi-label{{font-size:11px;opacity:.8;margin-top:5px}}
  .roi-sub{{font-size:10px;opacity:.55;margin-top:3px}}
  [title]{{cursor:help}}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
pct = round(PROJECT["week"] / PROJECT["total_weeks"] * 100)
st.markdown(f"""
<div class="kw-header">
  <div class="kw-header-left">
    <div class="kw-proj-name">{PROJECT['name']}</div>
    <div class="kw-proj-sub">
      {PROJECT['location']} &nbsp;·&nbsp; {PROJECT['capacity_mw']}MW hyperscale &nbsp;·&nbsp;
      <span title="Current week of construction vs total project duration">{PROJECT['week']} of {PROJECT['total_weeks']} weeks ({pct}% complete)</span>
      &nbsp;·&nbsp; Phase: <span title="MEP = Mechanical, Electrical & Plumbing — the dominant trade category on a data center build. Electrical bus duct = high-voltage power distribution infrastructure running through the facility.">{PROJECT['phase']}</span>
      &nbsp;·&nbsp; {PROJECT['date']} &nbsp;·&nbsp; Updated 2 min ago
    </div>
  </div>
  <div class="kw-badges">
    <span class="badge b-white" title="Dashboard is receiving live badge and sensor data from the jobsite"><span class="dot"></span> Live</span>
    <span class="badge b-amber" title="Alerts requiring action from the project team">3 open alerts</span>
    <span class="badge b-red" title="Workers who have exceeded consecutive workday or hour thresholds — elevated accident risk">{fatigue_ct} fatigue flags</span>
    <span class="badge b-amber" title="Change orders where Kwant-verified hours differ from subcontractor-reported hours by more than 5%">2 CO disputes</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Alert dropdown (always visible below header) ──────────────
with st.expander("View all active alerts", expanded=False):
    sev_style = {
        "critical": ("#FCEBEB","#E24B4A"),
        "warning":  ("#FAEEDA","#EF9F27"),
        "info":     ("#E6F1FB","#85B7EB"),
        "resolved": ("#EAF3DE","#97C459"),
    }
    sev_tooltip = {
        "critical": "Immediate action required — safety or compliance threshold breached",
        "warning":  "Attention needed — potential risk identified",
        "info":     "Informational — no immediate action required",
        "resolved": "Alert has been addressed and closed",
    }
    col_a, col_b = st.columns(2)
    for i, a in enumerate(ALERTS):
        bg, bc = sev_style.get(a["severity"], ("#f5f5f5","#ccc"))
        tt = sev_tooltip.get(a["severity"], "")
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
            <div class="alert-item" style="background:{bg};border-color:{bc}" title="{tt}">
              <div>
                <div class="alert-title">{a['icon']} {a['title']}</div>
                <div class="alert-meta">{a['time']} · {a['source']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:0.75rem'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", "Workforce & Fatigue",
    "Safety & Zones", "Compliance & Change Orders",
    "Kwant ROI", "Data & Methods"
])

# ═══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════
with tab1:
    st.markdown(f"""<div class="ptitle">
      {tip("WorkforceOS", "Kwant's AI operating system that aggregates safety, productivity, and compliance data into a single composite risk score for the project")}
      — AI project risk scores (target ≥85 · black line = threshold)
    </div>""", unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    score_tooltips = {
        "Safety":       "Composite score based on incident rate, near-misses, zone breaches, and fatigue flags. Lower = higher risk.",
        "Productivity": "Measures actual headcount vs planned by trade, schedule variance, and production time vs downtime across zones.",
        "Compliance":   "Tracks certification currency, COI status across subcontractors, and onboarding completion rates.",
    }
    score_meta = {
        "Safety":       ("#BA7517", "#FAEEDA"),
        "Productivity": ("#BA7517", "#FAEEDA"),
        "Compliance":   ("#BA7517", "#FAEEDA"),
    }
    for col, (label, data) in zip([sc1,sc2,sc3], WORKFORCEOS_SCORES.items()):
        bar_c, bg_c = score_meta[label]
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=data["score"],
                gauge={"axis":{"range":[0,100],"tickwidth":0,"tickcolor":"white"},
                       "bar":{"color":bar_c,"thickness":0.65},
                       "bgcolor":"#f0ede8","borderwidth":0,
                       "threshold":{"line":{"color":"#1a1a1a","width":2},"thickness":0.75,"value":data["target"]}},
                number={"font":{"size":38,"color":bar_c}},
            ))
            fig.update_layout(height=150, margin=dict(t=20,b=5,l=20,r=20),
                paper_bgcolor="white", font={"family":"sans-serif"})
            st.plotly_chart(fig, use_container_width=True, key=f"g_{label}")
            st.markdown(f"""
            <div style="background:{bg_c};border-radius:8px;padding:7px 10px;margin-top:-8px;margin-bottom:6px"
                 title="{score_tooltips[label]}">
              <div style="font-size:12px;font-weight:600;color:#1a1a1a">{label} — {data['score']}/100</div>
              <div style="font-size:11px;color:#666;margin-top:2px">{data['note']}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="ptitle">Today at a glance</div>', unsafe_allow_html=True)
    k = KPI
    kpis = [
        ("On-site now",        str(k["on_site"]),
         "Workers currently badged in via Kwant access control", f"of {k['planned']} planned", "nt"),
        ("Utilization",        f"{k['utilization']}%",
         "Percentage of planned headcount (920) actually on site. Below 90% = understaffed vs schedule. Data center builds run 82% fill rate on craft positions (AGC 2024).", f"vs {k['planned']} planned", "nt"),
        ("TRIR",               str(k["trir"]),
         "Total Recordable Incident Rate — OSHA-recordable injuries per 100 FTE workers/year. Construction avg 2.2 (BLS 2024). Well-run GCs target <1.0 for prequalification.", "Target < 1.0 ", "up"),
        ("Incident-free days", str(k["incident_free_days"]),
         "Consecutive days without a recordable safety incident on this jobsite", "0 recordable incidents", "up"),
        ("Near-misses today",  str(k["near_misses_today"]),
         "Events that could have caused injury but didn't. Leading indicator — arc flash near-misses are especially tracked on data center builds.", "↑ +1 vs 7-day avg", "dn"),
        ("Fatigue flags",      str(k["fatigue_flags"]),
         "Workers exceeding Kwant's fatigue threshold. Fatigued workers are 70% more likely to be involved in accidents (NSC). Electricians hardest hit due to labor shortage.", f"{k['fatigue_flags']} workers at threshold", "dn"),
        ("Overtime flags (7d)",str(k["overtime_flags_7d"]),
         "Workers who logged overtime in the past 7 days. Overtime is endemic on DC builds — labor shortage forces workers across multiple shifts.", "↑ +8 vs prior week", "dn"),
        ("Schedule variance",  f"{k['schedule_variance_days']}d",
         "Days behind schedule vs baseline. A 60MW DC delay costs $14.2M/month (iRecruit 2026). Electrical shortfall is primary driver here.", "Behind plan", "dn"),
    ]
    cols = st.columns(8)
    for col, (label, val, tooltip, delta, direction) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="mcard" title="{tooltip}">
              <div class="mlabel">{label}</div>
              <div class="mval">{val}</div>
              <div class="mdelta {direction}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ch1, ch2 = st.columns([2,1])
    with ch1:
        st.markdown(f"""<div class="ptitle">
          {tip("Hourly headcount", "Workers badged in each hour. Red = fatigue-flagged workers within total. Dashed = planned (920). DC builds start earlier — gate opens 5:30AM.")} — today vs planned
        </div>""", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["actual"]-HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Workforce", marker_color="#378ADD")
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Fatigue-flagged", marker_color="#E24B4A")
        fig.add_scatter(x=HOURLY_HEADCOUNT["hour"], y=HOURLY_HEADCOUNT["planned"],
                        name="Planned (920)", mode="lines",
                        line=dict(color="#bbb", dash="dash", width=1.5))
        fig.update_layout(barmode="stack", height=260, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            yaxis=dict(range=[0,1050], gridcolor="#f5f3ef", tickfont=dict(size=11)),
            xaxis=dict(tickfont=dict(size=11), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig, use_container_width=True, key="hc_today")

    with ch2:
        st.markdown('<div class="ptitle">Active alerts</div>', unsafe_allow_html=True)
        for a in ALERTS:
            bg, bc = sev_style.get(a["severity"], ("#f5f5f5","#ccc"))
            tt = sev_tooltip.get(a["severity"], "")
            st.markdown(f"""
            <div class="alert-item" style="background:{bg};border-color:{bc}" title="{tt}">
              <div>
                <div class="alert-title">{a['icon']} {a['title']}</div>
                <div class="alert-meta">{a['time']} · {a['source']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class="ptitle">
      {tip("8-week workforce trend", "Rolling headcount vs plan over the last 8 weeks during MEP ramp-up phase. Red bars (right axis) show fatigue accumulating as overtime pressure builds.")}
    </div>""", unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_scatter(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["planned"],
                     name="Planned", line=dict(color="#bbb", dash="dash", width=1.5), mode="lines")
    fig2.add_scatter(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["actual"],
                     name="Actual", line=dict(color="#378ADD", width=2.5), mode="lines+markers",
                     marker=dict(size=7))
    fig2.add_bar(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["fatigue_flags"],
                 name="Fatigue flags", marker_color="#E24B4A", opacity=0.7, yaxis="y2")
    fig2.update_layout(height=220, margin=dict(t=5,b=5,l=5,r=5),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
        yaxis=dict(range=[0,1050], gridcolor="#f5f3ef", tickfont=dict(size=11)),
        yaxis2=dict(range=[0,30], overlaying="y", side="right",
                    showgrid=False, tickfont=dict(size=10), title="Fatigue flags"),
        xaxis=dict(tickfont=dict(size=11), showgrid=False),
        font=dict(family="sans-serif"))
    st.plotly_chart(fig2, use_container_width=True, key="weekly")

# ═══════════════════════════════════════════════
# TAB 2 — WORKFORCE & FATIGUE
# ═══════════════════════════════════════════════
with tab2:
    w1, w2 = st.columns(2)
    with w1:
        st.markdown(f"""<div class="ptitle">
          {tip("Workforce by trade", "Actual vs planned headcount per trade. Red = critical shortfall (<75% of plan). Electricians are the critical path on every DC build — 'It's all about electricians' (Gray Construction VP, 2025). 82% of DC firms can't fill craft positions (AGC 2024).")} — actual vs planned
        </div>""", unsafe_allow_html=True)
        colors = ["#E24B4A" if p < 75 else "#EF9F27" if p < 90 else "#378ADD" for p in TRADES["pct"]]
        fig = go.Figure()
        fig.add_bar(y=TRADES["trade"], x=TRADES["planned"], orientation="h",
                    name="Planned", marker_color="#e8e6e0")
        fig.add_bar(y=TRADES["trade"], x=TRADES["actual"], orientation="h",
                    name="Actual", marker_color=colors,
                    text=[f"{a}/{p}  ({round(a/p*100)}%)" for a,p in zip(TRADES["actual"], TRADES["planned"])],
                    textposition="outside", textfont=dict(size=11))
        fig.update_layout(barmode="overlay", height=340, margin=dict(t=5,b=5,l=5,r=90),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig, use_container_width=True, key="trades")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Gate throughput", "Kwant passive badge detection replaces stop-and-scan. On a 920-worker site, continuous flow vs. manual scanning saves hundreds of hours per week. Yates Construction moved 5,000 workers through in 30 min using Kwant.")} — today
        </div>""", unsafe_allow_html=True)
        g = GATE
        gate_kpis = [
            ("Avg check-in time", f"{g['avg_checkin_time_sec']}s",
             "Time from badge detection to access granted. Kwant passive detection vs manual scanner baseline of 90 seconds. Suffolk saved 27,000 hours over 296 workdays.",
             f"Manual baseline: {g['manual_baseline_sec']}s", "up"),
            ("Peak flow",         f"{g['peak_flow_per_hr']}/hr",
             "Max workers processed per hour at peak entry time. Critical on DC builds where 800+ workers converge in a 30-minute window.",
             f"Peak: {g['peak_hour']}", "nt"),
            ("First badge",       g["first_badge_time"],
             "Time of first worker badge scan — DC builds start early, gate opens 5:30AM in Phoenix heat.",
             "Continuous gate flow", "nt"),
        ]
        gcols = st.columns(3)
        for col, (label, val, tooltip, delta, direction) in zip(gcols, gate_kpis):
            with col:
                st.markdown(f"""
                <div class="mcard" title="{tooltip}">
                  <div class="mlabel">{label}</div>
                  <div class="mval" style="font-size:20px">{val}</div>
                  <div class="mdelta {direction}">{delta}</div>
                </div>""", unsafe_allow_html=True)

    with w2:
        st.markdown(f"""<div class="ptitle">
          {tip("Fatigue management", "Kwant monitors consecutive workdays and avg daily hours per worker. Workers exceeding thresholds flagged before entering high-risk areas. Electricians hit hardest on DC builds due to labor shortage forcing extended shifts. Fatigued workers are 70% more likely to be involved in accidents (NSC).")} — flagged workers
        </div>""", unsafe_allow_html=True)
        for _, row in FATIGUE_FLAGS.iterrows():
            bg     = "#FCEBEB" if row["risk"] == "High" else "#FAEEDA"
            color  = "#A32D2D" if row["risk"] == "High" else "#854F0B"
            border = "#E24B4A" if row["risk"] == "High" else "#EF9F27"
            icon   = "" if row["risk"] == "High" else ""
            risk_tt = "High risk: worker has exceeded fatigue threshold. Recommend immediate schedule review or rest day." if row["risk"] == "High" else "Medium risk: approaching threshold. Monitor closely."
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:9px 12px;border-radius:8px;background:{bg};
                        border:1px solid {border};margin-bottom:7px" title="{risk_tt}">
              <div>
                <div style="font-size:13px;font-weight:600;color:#1a1a1a">{icon} {row['worker']}</div>
                <div style="font-size:11px;color:#888;margin-top:2px">
                  {row['trade']} &nbsp;·&nbsp;
                  <span title="Average hours per day on site over their current streak">{row['avg_hrs']}h avg/day</span>
                </div>
              </div>
              <div style="text-align:right" title="Consecutive days worked without a rest day">
                <div style="font-size:18px;font-weight:700;color:{color}">{row['streak']}</div>
                <div style="font-size:10px;color:{color}">consec. days</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Subcontractor risk score", "WorkforceOS composite score (0–100) weighting safety incidents, fatigue flags, compliance rate, and headcount reliability. Lower = higher risk.")}
        </div>""", unsafe_allow_html=True)
        colors_sub = ["#E24B4A" if s < 55 else "#EF9F27" if s < 72 else "#639922" for s in SUBCONTRACTORS["score"]]
        fig3 = go.Figure(go.Bar(
            x=SUBCONTRACTORS["score"], y=SUBCONTRACTORS["name"],
            orientation="h", marker_color=colors_sub,
            text=[f"{s}  ({w}w · TRIR {t})" for s,w,t in zip(SUBCONTRACTORS["score"], SUBCONTRACTORS["workers"], SUBCONTRACTORS["trir"])],
            textposition="outside", textfont=dict(size=11),
        ))
        fig3.update_layout(height=280, margin=dict(t=5,b=5,l=5,r=110),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(range=[0,130], showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig3, use_container_width=True, key="subs")

# ═══════════════════════════════════════════════
# TAB 3 — SAFETY & ZONES
# ═══════════════════════════════════════════════
with tab3:
    s1, s2 = st.columns([1,1])
    with s1:
        st.markdown(f"""<div class="ptitle">
          {tip("ZoneIQ", "Kwant's real-time indoor location system. Tracks which zone each worker is in and categorizes time as productive work, transit, or idle. On data centers, electrical rooms are restricted — unauthorized entry triggers immediate alert.")} — production / transit / downtime
        </div>""", unsafe_allow_html=True)
        for _, row in ZONES.iterrows():
            total = row["workers"]
            p = round(row["production"]/total*100)
            t = round(row["transit"]/total*100)
            d = 100-p-t
            prod_color = "#378ADD" if p >= 60 else "#EF9F27" if p >= 45 else "#E24B4A"
            st.markdown(f"""
            <div style="background:white;border:1px solid {BORDER};border-radius:10px;
                        padding:12px 14px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                <span style="font-size:13px;font-weight:600;color:#1a1a1a">{row['zone']}</span>
                <span style="font-size:12px;color:#aaa" title="Workers currently detected in this zone by Kwant sensors">{total} workers</span>
              </div>
              <div style="display:flex;height:12px;border-radius:6px;overflow:hidden;gap:2px">
                <div style="flex:{p};background:{prod_color};border-radius:6px 0 0 6px"
                     title="Active work time in zone"></div>
                <div style="flex:{t};background:#EF9F27"
                     title="Moving between zones or waiting"></div>
                <div style="flex:{d};background:#e0ddd7;border-radius:0 6px 6px 0"
                     title="Idle — present but not actively working"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:#aaa;margin-top:5px">
                <span style="color:{prod_color};font-weight:600">{p}% production</span>
                <span>{t}% transit</span>
                <span>{d}% downtime</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Near-miss trend", "Unplanned events with injury potential. Arc flash near-misses are the highest-severity type on data center builds — energized equipment at scale. Rising trend = leading indicator of future incidents.")} — last 8 weeks
        </div>""", unsafe_allow_html=True)
        nm_data = [1,1,2,2,3,2,2,3]
        fig_nm = go.Figure(go.Scatter(
            x=WEEKLY_TREND["week"], y=nm_data, mode="lines+markers",
            line=dict(color="#E24B4A", width=2), marker=dict(size=8, color="#E24B4A"),
            fill="tozeroy", fillcolor="rgba(226,75,74,0.08)"
        ))
        fig_nm.update_layout(height=180, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(gridcolor="#f5f3ef", tickfont=dict(size=11), dtick=1),
            xaxis=dict(tickfont=dict(size=11), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_nm, use_container_width=True, key="nm_trend")

    with s2:
        m = MUSTER
        time_saved = m["benchmark_manual_min"] - m["time_to_full_account_min"]
        st.markdown(f"""<div class="ptitle">
          {tip("Muster point", "Emergency assembly location. Kwant tracks who is accounted for in real time vs manual roll call. Critical on a 780-person site — manual roll call can take 35+ minutes.")} — last drill results
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="font-size:11px;color:#aaa;margin-bottom:12px" title="Date and time of most recent drill">{m['last_drill']}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
            <div style="text-align:center" title="Workers confirmed at muster point or located via Kwant badge data">
              <div style="font-size:38px;font-weight:700;color:{GREEN}">{m['accounted_for']}</div>
              <div style="font-size:11px;color:#aaa">Accounted for</div>
            </div>
            <div style="text-align:center" title="Workers on site at drill time not immediately at muster — located via badge data">
              <div style="font-size:38px;font-weight:700;color:{RED}">{m['missing']}</div>
              <div style="font-size:11px;color:#aaa">Initially missing</div>
            </div>
            <div style="text-align:center" title="Time from drill start to 100% accountability. Benchmark: manual 35 min → Kwant 4.1 min">
              <div style="font-size:38px;font-weight:700;color:{BLUE}">{m['time_to_full_account_min']}m</div>
              <div style="font-size:11px;color:#aaa">Full accountability</div>
            </div>
          </div>
          <div style="background:#EAF3DE;border-radius:8px;padding:10px 14px;margin-bottom:10px"
               title="Time saved vs manual roll call. Suffolk benchmark: manual 20–45 min → Kwant under 5 min.">
            <div style="font-size:13px;font-weight:600;color:{GREEN}">
               {time_saved:.0f} min faster than manual ({m['benchmark_manual_min']} min → {m['time_to_full_account_min']} min)
            </div>
          </div>
          <div style="font-size:11px;color:#aaa;margin-bottom:6px;font-weight:600" title="Zones confirmed clear — all workers accounted for">ZONES CLEARED</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            {''.join([f"<span style='background:#EAF3DE;color:{GREEN};border:1px solid #97C459;border-radius:5px;padding:3px 9px;font-size:11px'> {z}</span>" for z in m['zones_cleared']])}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Safety KPIs at a glance</div>', unsafe_allow_html=True)
        safety_kpis = [
            ("TRIR", str(KPI["trir"]),
             "Total Recordable Incident Rate. Formula: (incidents × 200,000) ÷ total hours worked. Construction avg 2.2 (BLS 2024). Under 1.0 = excellent and required for most GC prequalification.",
             "Target < 1.0 ", "up"),
            ("Incident-free days", str(KPI["incident_free_days"]),
             "Consecutive days without an OSHA-recordable incident", "0 recordable incidents", "up"),
            ("Zone breaches today", str(KPI["zone_breaches"]),
             "Unauthorized entries into restricted zones — electrical rooms on DC builds are energized and strictly access-controlled.",
             "Restricted area entries", "dn"),
            ("Near-misses today", str(KPI["near_misses_today"]),
             "Unplanned near-miss events logged today. Arc flash near-miss logged this morning is highest severity.",
             "+1 vs 7-day avg", "dn"),
        ]
        scols = st.columns(2)
        for i, (label, val, tooltip, delta, direction) in enumerate(safety_kpis):
            with scols[i%2]:
                st.markdown(f"""
                <div class="mcard" style="margin-bottom:10px" title="{tooltip}">
                  <div class="mlabel">{label}</div>
                  <div class="mval">{val}</div>
                  <div class="mdelta {direction}">{delta}</div>
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 4 — COMPLIANCE & CHANGE ORDERS
# ═══════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="ptitle">
          {tip("Certification compliance", "Tracks active safety certs for every worker. Arc flash (NFPA 70E) is DC-specific — required for anyone working near energized equipment. Kwant auto-flags expiring certs and can block site access until renewed.")}
        </div>""", unsafe_allow_html=True)
        cert_tooltips = {
            "OSHA 30-hour":         "30-hour OSHA safety training required for all supervisors and foremen",
            "Arc flash / NFPA 70E": "Data center-specific: required for all workers near energized electrical equipment. Covers arc flash hazards, PPE selection, and safe work practices on high-voltage systems.",
            "Fall protection":       "Required for anyone working at heights over 6 feet",
            "Confined space entry":  "Required for vaults, cable tunnels, and enclosed mechanical spaces",
            "Forklift / telehandler":"Required for operating powered industrial trucks and material handlers",
        }
        for _, row in CERTIFICATIONS.iterrows():
            pct = round(row["compliant"]/row["total"]*100)
            bar_c = "#E24B4A" if pct < 80 else "#EF9F27" if row["expiring"] > 0 else "#639922"
            badge = (f'<span style="background:#FAEEDA;color:#854F0B;border:1px solid #EF9F27;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px" '
                     f'title="Workers whose certification expires within 30 days — Kwant sends automated renewal reminders">'
                     f' {row["expiring"]} expiring</span>') if row["expiring"] > 0 else \
                    (f'<span style="background:#EAF3DE;color:{GREEN};border:1px solid #97C459;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px" '
                     f'title="All workers hold valid, current certification"> Current</span>')
            cert_tt = cert_tooltips.get(row["cert"], "")
            st.markdown(f"""
            <div style="padding:10px 0;border-bottom:1px solid {BORDER}" title="{cert_tt}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:13px;color:#1a1a1a;font-weight:500">{row['cert']}</span>
                {badge}
              </div>
              <div style="display:flex;align-items:center;gap:10px">
                <div style="flex:1;height:8px;background:#f0ede8;border-radius:4px;overflow:hidden">
                  <div style="width:{pct}%;height:100%;background:{bar_c};border-radius:4px"></div>
                </div>
                <span style="font-size:11px;color:#aaa;width:55px;text-align:right">{row['compliant']}/{row['total']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Overall compliance rate", "Composite % of workers with all required certifications current. Target 95%+. Arc flash cert gap is primary driver of current shortfall.")}
        </div>""", unsafe_allow_html=True)
        fig_c = go.Figure(go.Indicator(
            mode="gauge+number", value=KPI["compliance_rate"],
            gauge={"axis":{"range":[0,100],"tickwidth":0},
                   "bar":{"color":"#EF9F27","thickness":0.65},
                   "bgcolor":"#f0ede8","borderwidth":0,
                   "threshold":{"line":{"color":"#1a1a1a","width":2},"thickness":0.75,"value":95}},
            number={"font":{"size":40,"color":"#EF9F27"},"suffix":"%"},
        ))
        fig_c.update_layout(height=160, margin=dict(t=10,b=5,l=20,r=20),
            paper_bgcolor="white", font={"family":"sans-serif"})
        st.plotly_chart(fig_c, use_container_width=True, key="compliance_gauge")

    with c2:
        st.markdown(f"""<div class="ptitle">
          {tip("Change order validation", "COs adjust contract scope and payment. Kwant's zone data verifies actual hours worked vs subcontractor-reported hours. A variance >5% triggers a dispute flag. EllisDon used this to prevent a false injury claim and verify CO work.")} — Kwant hrs vs reported hrs
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#E6F1FB;border-radius:8px;padding:9px 12px;margin-bottom:12px;font-size:12px;color:#0C447C"
             title="Kwant zone sensor data is compared against subcontractor billing. Disputes auto-flagged when variance exceeds 5%.">
          ℹ Kwant location data validates hours worked by zone. Disputes auto-flagged when variance &gt; 5%.
        </div>""", unsafe_allow_html=True)
        for _, row in CHANGE_ORDERS.iterrows():
            is_disputed = row["status"] == "Disputed"
            bg   = "#FCEBEB" if is_disputed else "#EAF3DE"
            bc   = "#E24B4A" if is_disputed else "#97C459"
            icon = "" if is_disputed else ""
            var_c = RED if row["variance"] < -5 else GREEN
            co_tt = "Kwant verified hours significantly below subcontractor report — flagged for PM review before payment." if is_disputed else "Kwant data and subcontractor report within acceptable variance — approved for payment."
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {bc};border-radius:10px;
                        padding:12px 14px;margin-bottom:10px" title="{co_tt}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div style="font-size:13px;font-weight:700;color:#1a1a1a">{icon} {row['co']} — {row['trade']}</div>
                  <div style="font-size:11px;color:#aaa;margin-top:2px">{row['zone']}</div>
                </div>
                <span style="background:{'#FCEBEB' if is_disputed else '#EAF3DE'};
                             color:{'#A32D2D' if is_disputed else '#27500A'};
                             border-radius:5px;padding:3px 9px;font-size:11px;font-weight:600">
                  {row['status']}
                </span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px">
                <div style="text-align:center" title="Hours Kwant zone sensors recorded workers in this area">
                  <div style="font-size:18px;font-weight:700;color:#1B3FA0">{row['kwant_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Kwant verified</div>
                </div>
                <div style="text-align:center" title="Hours subcontractor reported on their change order billing">
                  <div style="font-size:18px;font-weight:700;color:#aaa">{row['reported_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Sub reported</div>
                </div>
                <div style="text-align:center" title="Difference: negative = sub billed more than Kwant recorded">
                  <div style="font-size:18px;font-weight:700;color:{var_c}">{row['variance']:+d}h</div>
                  <div style="font-size:10px;color:#aaa">Variance</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        total_disputed = CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum()
        st.markdown(f"""
        <div style="background:{BLUE};border-radius:10px;padding:12px 16px;color:white;margin-top:4px"
             title="Total hours in dispute — Kwant data is the GC's evidence to deny or negotiate payment">
          <div style="font-size:12px;opacity:.7">Total hours in dispute — protected by Kwant data</div>
          <div style="font-size:28px;font-weight:700;color:{GOLD}">{int(total_disputed)} hrs</div>
          <div style="font-size:11px;opacity:.6;margin-top:2px">
            Equivalent to ~${int(total_disputed * 95 / 1000)}K at blended DC labor rate ($95/hr)
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 5 — KWANT ROI
# ═══════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{BLUE} 0%,#0f2870 100%);border-radius:12px;
                padding:1.25rem 1.75rem;margin-bottom:1.5rem;color:white">
      <div style="font-size:16px;font-weight:700">Kwant ROI — {PROJECT['name']}</div>
      <div style="font-size:12px;opacity:.65;margin-top:4px">
        Benchmarks sourced from Suffolk (Q1 2026), Yates Construction (Q1 2026), and EllisDon case studies.
        Figures are illustrative projections based on published outcomes.
      </div>
    </div>""", unsafe_allow_html=True)

    ro = ROI
    st.markdown('<div class="ptitle">Process efficiency — manual baseline vs Kwant</div>', unsafe_allow_html=True)
    pe1, pe2, pe3 = st.columns(3)

    def efficiency_card(col, title, manual, kwant, unit, source, tooltip):
        improvement = round((manual - kwant) / manual * 100)
        with col:
            st.markdown(f"""
            <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.1rem"
                 title="{tooltip}">
              <div style="font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">{title}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
                <div style="text-align:center;background:#f5f3ef;border-radius:8px;padding:10px">
                  <div style="font-size:24px;font-weight:700;color:#aaa">{manual}{unit}</div>
                  <div style="font-size:10px;color:#bbb;margin-top:3px">Manual</div>
                </div>
                <div style="text-align:center;background:#EAF3DE;border-radius:8px;padding:10px">
                  <div style="font-size:24px;font-weight:700;color:{GREEN}">{kwant}{unit}</div>
                  <div style="font-size:10px;color:{GREEN};margin-top:3px">Kwant</div>
                </div>
              </div>
              <div style="background:{BLUE};border-radius:6px;padding:7px 10px;text-align:center">
                <span style="color:{GOLD};font-weight:700;font-size:16px">{improvement}% faster</span>
              </div>
              <div style="font-size:10px;color:#bbb;margin-top:7px;text-align:center">Source: {source}</div>
            </div>""", unsafe_allow_html=True)

    efficiency_card(pe1, "Gate check-in time",
        ro["checkin_manual_min"], ro["checkin_kwant_min"], " min", "Suffolk ROI Study Q1 2026",
        "Manual: 25 min avg including badge scan + verification. Kwant: passive detection, worker walks through without stopping. Suffolk saved 27,000 hours over 296 workdays.")
    efficiency_card(pe2, "Worker onboarding",
        ro["onboarding_manual_min"], ro["onboarding_kwant_min"], " min", "Suffolk ROI Study Q1 2026",
        "Manual: paper forms, cert checks, manual data entry — 90 min avg. Kwant: mobile-first, completed before arriving on site. Suffolk saved 1,811 hours across 2,415 workers.")
    efficiency_card(pe3, "Emergency accountability",
        ro["emergency_manual_min"], ro["emergency_kwant_min"], " min", "Yates / Suffolk case studies",
        "Manual roll call: 20–45 min to account for all workers. Kwant: real-time badge location shows who is where instantly. On a 780-person DC site, this difference is critical.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="ptitle">Project-level impact</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    roi_cards = [
        ("185,000+", "Work hours captured",
         "Verified at controlled entry points",
         "Total workforce hours recorded by Kwant badge and sensor data — replacing manual timesheets. 100% verified vs estimated.", r1),
        ("100%", "Digital reporting",
         "Zero paper-based reports",
         "All daily reports, incident logs, and compliance records generated digitally via Kwant.", r2),
        ("75%", "Faster incident response",
         "vs manual · EllisDon benchmark",
         "EllisDon reduced incident response time by 75% using Kwant real-time location data.", r3),
        (f"${ro['cost_savings_low_k']}K–${ro['cost_savings_high_k']}K", "Est. savings / incident avoided",
         "1–4 worker incident reduction",
         f"Direct + indirect savings per avoided incident. DC builds: a 60MW delay costs ${ro['delay_cost_per_month_m']}M/month (iRecruit 2026) — safety incidents cascade into schedule risk.", r4),
    ]
    for val, label, sub, tooltip, col in roi_cards:
        with col:
            st.markdown(f"""
            <div class="roi-block" title="{tooltip}">
              <div class="roi-val">{val}</div>
              <div class="roi-label">{label}</div>
              <div class="roi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r_left, r_right = st.columns(2)
    with r_left:
        st.markdown(f"""<div class="ptitle">
          {tip("Admin time saved", "Hours/week the project team saves by eliminating manual reporting, cert tracking, headcount reconciliation, and compliance docs. Benchmarked from Yates Construction (5–10 hrs/week per team).")} — this project
        </div>""", unsafe_allow_html=True)
        weeks_elapsed = PROJECT["week"]
        total_admin_saved = ro["admin_hrs_saved_weekly"] * weeks_elapsed
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px" title="Hours saved per week vs manual — Yates benchmark: 5–10 hrs/week">
              <div style="font-size:42px;font-weight:700;color:{BLUE}">{ro['admin_hrs_saved_weekly']}</div>
              <div style="font-size:12px;color:#aaa">hrs saved / week</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Yates benchmark: 5–10 hrs/wk</div>
            </div>
            <div style="text-align:center;padding:12px" title="Cumulative admin hours saved — Week 22 × 9 hrs/week">
              <div style="font-size:42px;font-weight:700;color:{GREEN}">{total_admin_saved}</div>
              <div style="font-size:12px;color:#aaa">total hrs saved to date</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Over {weeks_elapsed} weeks on Kwant</div>
            </div>
          </div>
          <div style="background:#f5f3ef;border-radius:8px;padding:10px 14px;margin-top:12px;
                      font-size:12px;color:#666;text-align:center">
            Equivalent to <strong>{round(total_admin_saved/40, 1)} weeks</strong> of full-time PM overhead eliminated
          </div>
        </div>""", unsafe_allow_html=True)

    with r_right:
        st.markdown(f"""<div class="ptitle">
          {tip("Change order protection", "Dollar value of disputed hours Kwant's location data is defending. Without Kwant, GCs typically pay disputed COs due to lack of evidence. EllisDon prevented a false injury claim and verified CO work with location data.")} — value defended
        </div>""", unsafe_allow_html=True)
        disputed_hrs = int(CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum())
        value_k = round(disputed_hrs * 95 / 1000, 1)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px" title="Hours across disputed COs where Kwant shows fewer hours than billed">
              <div style="font-size:42px;font-weight:700;color:{RED}">{disputed_hrs}</div>
              <div style="font-size:12px;color:#aaa">disputed hours</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Flagged by Kwant zone data</div>
            </div>
            <div style="text-align:center;padding:12px" title="Financial value of disputed hours at $95/hr DC blended labor rate">
              <div style="font-size:42px;font-weight:700;color:{GREEN}">${value_k}K</div>
              <div style="font-size:12px;color:#aaa">value protected</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">At $95/hr DC blended rate</div>
            </div>
          </div>
          <div style="background:#EAF3DE;border-radius:8px;padding:10px 14px;margin-top:12px;
                      font-size:12px;color:{GREEN};text-align:center">
             EllisDon: location data prevented a false injury claim + verified change order work
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    st.caption("ROI benchmarks: Suffolk Construction Q1 2026, Yates Construction Q1 2026, EllisDon. DC delay cost: iRecruit 2026. All project figures are simulated for demonstration.")

# ═══════════════════════════════════════════════
# TAB 6 — DATA & METHODS
# ═══════════════════════════════════════════════
with tab6:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{BLUE} 0%,#0f2870 100%);border-radius:12px;
                padding:1.25rem 1.75rem;margin-bottom:1.5rem;color:white">
      <div style="font-size:16px;font-weight:700">Data Generation & Methodology</div>
      <div style="font-size:12px;opacity:.65;margin-top:4px">
        How the numbers in this dashboard are generated, what assumptions are built in, and where the parameters come from.
      </div>
    </div>""", unsafe_allow_html=True)

    d1, d2 = st.columns(2)

    with d1:
        st.markdown("### How data is generated")
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem;margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:{BLUE};margin-bottom:8px">Generation approach</div>
          <div style="font-size:13px;color:#333;line-height:1.7">
            Every metric in this dashboard is generated fresh on each page load using <strong>bounded uniform random variation</strong>
            applied to research-grounded base values. This is intentional — it simulates the natural day-to-day
            fluctuation a PM would see on a live Kwant dashboard.<br><br>
            The random seed is <code>None</code>, meaning it pulls from system entropy. There is no normality assumption.
            Construction data is <strong>not normally distributed</strong>: headcount ramps up non-linearly,
            incidents cluster near zero with rare spikes, and fatigue accumulates monotonically until a rest day.
            Bounded uniform noise is honest about what we know — the plausible range — without fabricating a distribution shape.
          </div>
        </div>
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem;margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:{BLUE};margin-bottom:8px">Why not a normal distribution?</div>
          <div style="font-size:13px;color:#333;line-height:1.7">
            <strong>Headcount</strong> follows a right-skewed ramp — slow start, fast mid-project growth, plateau near peak.
            Adding Gaussian noise to this would imply symmetric uncertainty we don't have evidence for.<br><br>
            <strong>Safety incidents (TRIR)</strong> are Poisson-distributed in reality — rare discrete events.
            Modeling as continuous normal would allow negative incident rates, which is meaningless.<br><br>
            <strong>Fatigue streaks</strong> are path-dependent: a worker at day 9 was at day 8 yesterday.
            They don't fluctuate randomly — they accumulate. We model this by fixing names and applying
            small bounded variation to streak length only (±1 day) to simulate scheduling uncertainty.
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### Live distributions — this session")
        st.markdown('<div class="ptitle">Hourly headcount distribution</div>', unsafe_allow_html=True)
        fig_dist1 = go.Figure()
        fig_dist1.add_bar(x=HOURLY_HEADCOUNT["hour"], y=HOURLY_HEADCOUNT["actual"],
                          name="Actual", marker_color="#378ADD")
        fig_dist1.add_scatter(x=HOURLY_HEADCOUNT["hour"], y=HOURLY_HEADCOUNT["planned"],
                              name="Planned", mode="lines",
                              line=dict(color="#bbb", dash="dash", width=1.5))
        fig_dist1.update_layout(height=200, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=10)),
            yaxis=dict(gridcolor="#f5f3ef", tickfont=dict(size=10)),
            xaxis=dict(tickfont=dict(size=10), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_dist1, use_container_width=True, key="dist_hc")

        st.markdown('<div class="ptitle">Trade utilization % distribution</div>', unsafe_allow_html=True)
        colors_dist = ["#E24B4A" if p < 75 else "#EF9F27" if p < 90 else "#378ADD" for p in TRADES["pct"]]
        fig_dist2 = go.Figure(go.Bar(
            y=TRADES["trade"], x=TRADES["pct"], orientation="h",
            marker_color=colors_dist,
            text=[f"{p}%" for p in TRADES["pct"]],
            textposition="outside", textfont=dict(size=10)
        ))
        fig_dist2.add_vline(x=100, line_dash="dash", line_color="#bbb", line_width=1.5)
        fig_dist2.add_vline(x=90,  line_dash="dot",  line_color="#EF9F27", line_width=1)
        fig_dist2.add_vline(x=75,  line_dash="dot",  line_color="#E24B4A", line_width=1)
        fig_dist2.update_layout(height=280, margin=dict(t=5,b=5,l=5,r=50),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(range=[0,130], showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_dist2, use_container_width=True, key="dist_trades")

    with d2:
        st.markdown("### Parameter sources")
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem;margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:{BLUE};margin-bottom:10px">Project baseline — 100MW Phoenix build</div>
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666;width:55%">Peak headcount range (100MW)</td>
              <td style="padding:6px 0;font-weight:600">800–1,200 workers</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Source</td>
              <td style="padding:6px 0">CBRE North America Data Center Trends 2024</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Build duration</td>
              <td style="padding:6px 0;font-weight:600">18–36 months (72 weeks modeled)</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Source</td>
              <td style="padding:6px 0">Uptime Institute 2024 Global Data Center Survey</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Worker density (construction)</td>
              <td style="padding:6px 0;font-weight:600">0.7–2.0 workers per MW</td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#666">Source</td>
              <td style="padding:6px 0">Data Center Employment Forecast, HAMM Institute, Dec 2025</td>
            </tr>
          </table>
        </div>
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem;margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:{BLUE};margin-bottom:10px">Safety benchmarks</div>
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666;width:55%">Construction TRIR (industry avg)</td>
              <td style="padding:6px 0;font-weight:600">2.2–2.3 per 100 FTE</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Source</td>
              <td style="padding:6px 0">U.S. Bureau of Labor Statistics SOII, 2024</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">GC prequalification threshold</td>
              <td style="padding:6px 0;font-weight:600">TRIR &lt; 1.0 (mission-critical)</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">This project TRIR range</td>
              <td style="padding:6px 0;font-weight:600">0.62–0.74 (modeled)</td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#666">Fatigue accident multiplier</td>
              <td style="padding:6px 0;font-weight:600">70% more likely (NSC)</td>
            </tr>
          </table>
        </div>
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem;margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:{BLUE};margin-bottom:10px">Labor market context</div>
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666;width:55%">DC firms struggling to fill craft positions</td>
              <td style="padding:6px 0;font-weight:600">82% (AGC 2024)</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Electrician employment growth 2024–2034</td>
              <td style="padding:6px 0;font-weight:600">+9.5% (BlackRock 2025)</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">Electrician labor cost increase (YoY)</td>
              <td style="padding:6px 0;font-weight:600">+8–12% (Turner & Townsend 2024)</td>
            </tr>
            <tr style="border-bottom:1px solid {BORDER}">
              <td style="padding:6px 0;color:#666">DC schedule delay cost (60MW)</td>
              <td style="padding:6px 0;font-weight:600">$14.2M / month</td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#666">Source</td>
              <td style="padding:6px 0">iRecruit.co Data Center Labor Report, 2026</td>
            </tr>
          </table>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="ptitle">Fatigue flags — streak distribution (this session)</div>', unsafe_allow_html=True)
        fig_fat = go.Figure()
        colors_fat = ["#E24B4A" if r == "High" else "#EF9F27" for r in FATIGUE_FLAGS["risk"]]
        fig_fat.add_bar(
            x=FATIGUE_FLAGS["worker"], y=FATIGUE_FLAGS["streak"],
            marker_color=colors_fat,
            text=FATIGUE_FLAGS["streak"].astype(str) + "d",
            textposition="outside", textfont=dict(size=11)
        )
        fig_fat.add_hline(y=5, line_dash="dot", line_color="#EF9F27", line_width=1.5,
                          annotation_text="Medium threshold (5d)", annotation_font_size=10)
        fig_fat.add_hline(y=8, line_dash="dot", line_color="#E24B4A", line_width=1.5,
                          annotation_text="High threshold (8d)", annotation_font_size=10)
        fig_fat.update_layout(height=240, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(range=[0,16], gridcolor="#f5f3ef", tickfont=dict(size=10), title="Consec. days"),
            xaxis=dict(tickfont=dict(size=10), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_fat, use_container_width=True, key="dist_fatigue")

        st.markdown('<div class="ptitle">Subcontractor risk score distribution</div>', unsafe_allow_html=True)
        colors_sub_d = ["#E24B4A" if s < 55 else "#EF9F27" if s < 72 else "#639922" for s in SUBCONTRACTORS["score"]]
        fig_sub_d = go.Figure(go.Bar(
            x=SUBCONTRACTORS["name"], y=SUBCONTRACTORS["score"],
            marker_color=colors_sub_d,
            text=SUBCONTRACTORS["score"].astype(str),
            textposition="outside", textfont=dict(size=11)
        ))
        fig_sub_d.add_hline(y=85, line_dash="dash", line_color="#bbb", line_width=1.5,
                             annotation_text="Target (85)", annotation_font_size=10)
        fig_sub_d.update_layout(height=220, margin=dict(t=15,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(range=[0,110], gridcolor="#f5f3ef", tickfont=dict(size=10)),
            xaxis=dict(tickfont=dict(size=10), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_sub_d, use_container_width=True, key="dist_subs")

    st.divider()
    st.caption("""
    Sources: CBRE North America Data Center Trends 2024 · Uptime Institute 2024 Global Data Center Survey ·
    HAMM Institute Data Center Employment Forecast Dec 2025 · U.S. Bureau of Labor Statistics SOII 2024 ·
    AGC/Sage 2026 Outlook · Turner & Townsend Data Center Cost Index 2024 · BlackRock 2025 infrastructure report ·
    iRecruit.co Data Center Construction Labor Report 2026 · National Safety Council ·
    Suffolk Construction ROI Study Q1 2026 · Yates Construction ROI Study Q1 2026 · EllisDon case study.
    All project metrics are simulated for demonstration purposes.
    """)

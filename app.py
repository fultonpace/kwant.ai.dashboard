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
    """Wrap text in a span with a hover tooltip."""
    return f'<span title="{tooltip}" style="cursor:help;border-bottom:1px dotted #aaa">{text}</span>'

PROJECT = {
    "name": "Hudson Yards — Tower C",
    "location": "New York, NY",
    "week": 34,
    "total_weeks": 78,
    "date": "May 15, 2026",
    "planned_headcount": 310,
    "contract_value_m": 480,
    "phase": "MEP (Mechanical, Electrical & Plumbing) Rough-in + Curtain Wall",
}

WORKFORCEOS_SCORES = {
    "Safety":       {"score": ri(72, -5, 5),  "target": 85, "note": "2 near-misses · 1 zone breach · TRIR 0.82"},
    "Productivity": {"score": ri(68, -5, 5),  "target": 85, "note": "Electrical below plan · -3d schedule"},
    "Compliance":   {"score": ri(84, -3, 3),  "target": 85, "note": "11 certs expiring · COI current all subs"},
}

on_site     = ri(284, -8, 12)
near_misses = ri(2, -1, 2)
fatigue_ct  = ri(7, -1, 2)
overtime_ct = ri(19, -3, 4)
inc_free    = ri(19, 0, 1)

KPI = {
    "on_site":                on_site,
    "planned":                310,
    "utilization":            round(on_site / 310 * 100),
    "avg_hrs":                round(r(6.4, -0.4, 0.6), 1),
    "overtime_flags_7d":      overtime_ct,
    "incidents":              0,
    "incident_free_days":     inc_free,
    "trir":                   round(r(0.82, -0.05, 0.05), 2),
    "near_misses_today":      near_misses,
    "zone_breaches":          ri(1, 0, 1),
    "schedule_variance_days": ri(-3, -1, 1),
    "compliance_rate":        ri(96, -2, 2),
    "fatigue_flags":          fatigue_ct,
}

base_actual  = [14, 88, 196, 251, 268, 272, 241, 258, 271, 284]
base_fatigue = [0,   0,   4,   7,   7,   7,   6,   7,   7,   7]
actual_hc  = [max(5, v + rng.randint(-8, 8)) for v in base_actual]
fatigue_hc = [max(0, min(f + rng.randint(-1, 1), actual_hc[i])) for i, f in enumerate(base_fatigue)]

HOURLY_HEADCOUNT = pd.DataFrame({
    "hour":            ["6AM","7AM","8AM","9AM","10AM","11AM","12PM","1PM","2PM","3PM"],
    "actual":          actual_hc,
    "fatigue_flagged": fatigue_hc,
    "planned":         [310]*10,
})

trade_data = [
    ("Concrete / formwork",                 58, 60),
    ("Structural steel",                    44, 48),
    ("Curtain wall",                        41, 45),
    ("MEP — Mechanical (HVAC & piping)",    36, 38),
    ("MEP — Electrical (power & lighting)", 14, 22),
    ("MEP — Plumbing (water & drainage)",   26, 28),
    ("Carpentry / framing",                 38, 40),
    ("Laborers / general",                  27, 29),
]
TRADES = pd.DataFrame([
    {"trade": name, "actual": max(1, ri(base, -4, 4)), "planned": planned}
    for name, base, planned in trade_data
])
TRADES["pct"] = (TRADES["actual"] / TRADES["planned"] * 100).round(0).astype(int)

zone_data = [
    ("Structure (L12–22)",                97, 71, 18,  8),
    ("MEP (Mech/Elec/Plumbing) rough-in", 62, 38, 14, 10),
    ("Curtain wall",                       41, 24, 10,  7),
    ("Staging / grade",                    84, 62, 15,  7),
]
rows = []
for zone, workers, prod, transit, down in zone_data:
    w = max(10, ri(workers, -6, 6))
    p = max(5, min(prod + rng.randint(-5, 5), w - 5))
    t = max(2, min(transit + rng.randint(-3, 3), w - p - 2))
    d = w - p - t
    rows.append({"zone": zone, "workers": w, "production": p, "transit": t, "downtime": max(0, d)})
ZONES = pd.DataFrame(rows)

fatigue_data = [
    ("R. Gutierrez", "Electrical",       9, 10.2, "High"),
    ("M. Okafor",    "Electrical",       9,  9.8, "High"),
    ("D. Reyes",     "Concrete",         6, 10.1, "High"),
    ("T. Callahan",  "Scaffold",         7,  9.4, "Medium"),
    ("J. Morales",   "MEP — Mechanical", 6,  9.1, "Medium"),
    ("B. Osei",      "Laborers",         5,  8.9, "Medium"),
    ("C. Huang",     "Structural steel", 5,  8.5, "Medium"),
]
FATIGUE_FLAGS = pd.DataFrame([
    {"worker": name, "trade": trade,
     "streak": max(4, streak + rng.randint(-1, 1)),
     "avg_hrs": round(r(hrs, -0.3, 0.3), 1), "risk": risk}
    for name, trade, streak, hrs, risk in fatigue_data
])

sub_data = [
    ("Stahl Electric",   41, 14, "High",   2.1, 71),
    ("Pyramid Scaffold", 58, 38, "Medium", 1.4, 83),
    ("CoreSteel LLC",    71, 44, "Medium", 0.9, 91),
    ("Harbor Curtain",   79, 41, "Low",    0.7, 94),
    ("Summit MEP",       82, 62, "Low",    0.6, 97),
    ("Apex Concrete",    76, 58, "Low",    0.8, 95),
]
SUBCONTRACTORS = pd.DataFrame([
    {"name": name,
     "score":      max(20, min(99, ri(score, -4, 4))),
     "workers":    max(1, ri(workers, -3, 3)),
     "risk":       risk,
     "trir":       round(r(trir, -0.1, 0.1), 1),
     "compliance": max(60, min(100, ri(comp, -3, 3)))}
    for name, score, workers, risk, trir, comp in sub_data
]).sort_values("score")

cert_data = [
    ("OSHA 30-hour",               284, 284, 0),
    ("Fall protection",            271, 284, 0),
    ("Scaffold competency",         38,  44, 6),
    ("Confined space entry",        17,  22, 5),
    ("Forklift / telehandler",      29,  29, 0),
]
CERTIFICATIONS = pd.DataFrame([
    {"cert": cert,
     "compliant": max(0, min(total, ri(compliant, -2, 2))),
     "total": total,
     "expiring": max(0, ri(expiring, -1, 1))}
    for cert, compliant, total, expiring in cert_data
])

ROI = {
    "checkin_manual_min": 25, "checkin_kwant_min": 4,
    "onboarding_manual_min": 90, "onboarding_kwant_min": 38,
    "emergency_manual_min": 35, "emergency_kwant_min": 4,
    "admin_hrs_saved_weekly": 7, "hrs_captured_total": 185000,
    "cost_savings_low_k": 40, "cost_savings_high_k": 160,
    "incident_response_reduction_pct": 75, "digital_reporting_pct": 95,
}

MUSTER = {
    "last_drill": "May 12, 2026 · 10:15 AM",
    "total_on_site_at_drill": 271, "accounted_for": 263, "missing": 8,
    "time_to_full_account_min": 3.8, "benchmark_manual_min": 28,
    "zones_cleared": ["L1 Staging", "L9 Structure", "L12 MEP", "Curtain Wall"],
    "zones_pending": [],
}

GATE = {
    "avg_checkin_time_sec": max(8, ri(14, -3, 3)),
    "manual_baseline_sec": 90,
    "peak_flow_per_hr": ri(312, -15, 15),
    "total_today": on_site,
    "first_badge_time": "5:58 AM",
    "peak_hour": "7–8 AM",
}

CHANGE_ORDERS = pd.DataFrame([
    {"co": "CO-114", "trade": "MEP Electrical", "zone": "L14–16 Electrical room",
     "kwant_hrs": ri(186,-5,5), "reported_hrs": 210, "status": "Disputed"},
    {"co": "CO-118", "trade": "Concrete",        "zone": "L9 Pour deck",
     "kwant_hrs": ri(312,-4,4), "reported_hrs": 314, "status": "Approved"},
    {"co": "CO-121", "trade": "Curtain wall",    "zone": "L20–22 East face",
     "kwant_hrs": ri(97,-3,3),  "reported_hrs": 97,  "status": "Approved"},
    {"co": "CO-125", "trade": "Structural steel","zone": "L18 Structural",
     "kwant_hrs": ri(144,-5,5), "reported_hrs": 171, "status": "Disputed"},
    {"co": "CO-129", "trade": "MEP Mechanical",  "zone": "L10–12 HVAC shaft",
     "kwant_hrs": ri(228,-4,4), "reported_hrs": 229, "status": "Approved"},
])
CHANGE_ORDERS["variance"] = CHANGE_ORDERS["kwant_hrs"] - CHANGE_ORDERS["reported_hrs"]

base_actual_wk  = [198, 214, 231, 248, 261, 275, 279, 284]
base_planned_wk = [220, 240, 255, 270, 285, 300, 305, 310]
base_fatigue_wk = [2, 3, 3, 4, 5, 6, 7, 7]
WEEKLY_TREND = pd.DataFrame({
    "week":          ["Wk 27","Wk 28","Wk 29","Wk 30","Wk 31","Wk 32","Wk 33","Wk 34"],
    "actual":        [max(100, v + rng.randint(-5,5)) for v in base_actual_wk],
    "planned":       base_planned_wk,
    "fatigue_flags": [max(0, v + rng.randint(-1,1)) for v in base_fatigue_wk],
})

ALERTS = [
    {"severity": "critical", "icon": "🔴", "title": f"Fatigue threshold — {fatigue_ct} workers flagged including 3 from Stahl Electric at 9th consecutive day.", "time": "08:00 AM", "source": "Fatigue Mgmt"},
    {"severity": "warning",  "icon": "⚠️", "title": "Unauthorized zone entry — L18 mechanical shaft. Badge #A-2291.", "time": "08:47 AM", "source": "ZoneIQ"},
    {"severity": "warning",  "icon": "⚠️", "title": "Near-miss logged — falling object, curtain wall L22. Area cleared.", "time": "09:14 AM", "source": "Safety"},
    {"severity": "warning",  "icon": "⚠️", "title": "CO-114 hour variance flagged — Kwant verified hrs below reported. Data sent to PM.", "time": "09:30 AM", "source": "Change Orders"},
    {"severity": "info",     "icon": "ℹ️", "title": f"MEP Electrical headcount below plan. Root cause: fatigue flags + no-shows.", "time": "08:00 AM", "source": "WorkforceOS"},
    {"severity": "resolved", "icon": "✅", "title": "SOS resolved — Badge #B-0074 confirmed safe. False alarm.", "time": "07:32 AM", "source": "Safety"},
]

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Kwant · PM Dashboard", page_icon="🏗️",
                   layout="wide", initial_sidebar_state="collapsed")

BLUE="#1B3FA0"; GOLD="#F5C518"; GREEN="#3B6D11"; RED="#A32D2D"; LIGHT="#f8f7f4"; BORDER="#e8e6e0"

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"]{{background:{LIGHT}}}
  [data-testid="stHeader"]{{background:transparent}}
  .block-container{{padding:1.25rem 2rem 2rem;max-width:1440px}}
  div[data-testid="stTabs"] button{{font-size:13px;font-weight:500}}
  .kw-header{{background:linear-gradient(135deg,{BLUE} 0%,#0f2870 100%);border-radius:12px;
    padding:1.25rem 1.75rem;margin-bottom:1.25rem;display:flex;
    justify-content:space-between;align-items:center}}
  .kw-header-left{{color:white}}
  .kw-proj-name{{font-size:20px;font-weight:700;margin:0}}
  .kw-proj-sub{{font-size:12px;opacity:.7;margin:4px 0 0}}
  .kw-badges{{display:flex;gap:8px;flex-wrap:wrap}}
  .badge{{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:600;
    padding:4px 10px;border-radius:20px;border:1.5px solid}}
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
    <div class="kw-proj-name">🏗️ {PROJECT['name']}</div>
    <div class="kw-proj-sub">
      {PROJECT['location']} &nbsp;·&nbsp;
      <span title="Current week of construction vs total project duration">{PROJECT['week']} of {PROJECT['total_weeks']} weeks ({pct}% complete)</span>
      &nbsp;·&nbsp; Phase: <span title="MEP = Mechanical, Electrical & Plumbing — the building systems being installed on active floors. Curtain wall = exterior glass facade installation.">{PROJECT['phase']}</span>
      &nbsp;·&nbsp; {PROJECT['date']} &nbsp;·&nbsp; Updated 2 min ago
    </div>
  </div>
  <div class="kw-badges">
    <span class="badge b-white" title="Dashboard is receiving live badge and sensor data from the jobsite"><span class="dot"></span> Live</span>
    <span class="badge b-amber" title="Alerts requiring action from the project team">⚠ 3 open alerts</span>
    <span class="badge b-red" title="Workers who have exceeded consecutive workday or hour thresholds — elevated accident risk">🔴 {fatigue_ct} fatigue flags</span>
    <span class="badge b-amber" title="Change orders where Kwant-verified hours differ from subcontractor-reported hours by more than 5%">📋 2 CO disputes</span>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "👷 Workforce & Fatigue",
    "🛡️ Safety & Zones", "📋 Compliance & Change Orders", "💡 Kwant ROI"
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
        "Compliance":   ("#3B6D11", "#EAF3DE"),
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
         "Workers currently badged in via Kwant access control", "↑ +12 vs yesterday", "up"),
        ("Utilization",        f"{k['utilization']}%",
         "Percentage of planned headcount (310) actually on site. Below 90% = understaffed vs schedule.", f"vs {k['planned']} planned", "nt"),
        ("TRIR",               str(k["trir"]),
         "Total Recordable Incident Rate — number of OSHA-recordable injuries per 100 full-time workers per year. Industry avg ~3.0; target here is below 1.0.", "Target < 1.0 ✓", "up"),
        ("Incident-free days", str(k["incident_free_days"]),
         "Consecutive days without a recordable safety incident on this jobsite", "0 recordable incidents", "up"),
        ("Near-misses today",  str(k["near_misses_today"]),
         "Events that could have caused injury but didn't. Tracked as early warning signals — more near-misses = higher incident risk.", "↑ +1 vs 7-day avg", "dn"),
        ("Fatigue flags",      str(k["fatigue_flags"]),
         "Workers who have exceeded Kwant's configurable fatigue threshold — typically 5+ consecutive days or 10+ hrs/day avg. High-risk for accidents.", f"{k['fatigue_flags']} workers at threshold", "dn"),
        ("Overtime flags (7d)",str(k["overtime_flags_7d"]),
         "Workers who logged overtime in the past 7 days. Tracked to monitor fatigue risk and labor compliance.", "↑ +6 vs prior week", "dn"),
        ("Schedule variance",  f"{k['schedule_variance_days']}d",
         "How many days behind (negative) or ahead (positive) the project is vs the baseline schedule. Driven by headcount gaps, weather, and productivity losses.", "Behind plan", "dn"),
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
          {tip("Hourly headcount", "Number of workers badged in at each hour. Red = fatigue-flagged workers within the total. Dashed line = planned staffing level.")} — today vs planned
        </div>""", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["actual"]-HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Workforce", marker_color="#378ADD")
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Fatigue-flagged", marker_color="#E24B4A")
        fig.add_scatter(x=HOURLY_HEADCOUNT["hour"], y=HOURLY_HEADCOUNT["planned"],
                        name="Planned (310)", mode="lines",
                        line=dict(color="#bbb", dash="dash", width=1.5))
        fig.update_layout(barmode="stack", height=260, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            yaxis=dict(range=[0,350], gridcolor="#f5f3ef", tickfont=dict(size=11)),
            xaxis=dict(tickfont=dict(size=11), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig, use_container_width=True, key="hc_today")

    with ch2:
        st.markdown('<div class="ptitle">Active alerts</div>', unsafe_allow_html=True)
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
      {tip("8-week workforce trend", "Rolling view of actual vs planned headcount over the last 8 weeks. Red bars (right axis) show fatigue flags accumulating — a leading indicator of safety risk.")}
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
        yaxis=dict(range=[0,360], gridcolor="#f5f3ef", tickfont=dict(size=11)),
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
          {tip("Workforce by trade", "Compares actual workers checked in vs the planned staffing level for each trade. Red = critical shortfall (under 75% of plan). Amber = below target (75–90%). Blue = on track.")} — actual vs planned
        </div>""", unsafe_allow_html=True)
        colors = ["#E24B4A" if p < 75 else "#EF9F27" if p < 90 else "#378ADD" for p in TRADES["pct"]]
        fig = go.Figure()
        fig.add_bar(y=TRADES["trade"], x=TRADES["planned"], orientation="h",
                    name="Planned", marker_color="#e8e6e0")
        fig.add_bar(y=TRADES["trade"], x=TRADES["actual"], orientation="h",
                    name="Actual", marker_color=colors,
                    text=[f"{a}/{p}  ({round(a/p*100)}%)" for a,p in zip(TRADES["actual"], TRADES["planned"])],
                    textposition="outside", textfont=dict(size=11))
        fig.update_layout(barmode="overlay", height=320, margin=dict(t=5,b=5,l=5,r=80),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig, use_container_width=True, key="trades")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Gate throughput", "How fast workers are moving through site entry points. Kwant passive badge detection eliminates stop-and-scan bottlenecks — workers walk through without stopping.")} — today
        </div>""", unsafe_allow_html=True)
        g = GATE
        gate_kpis = [
            ("Avg check-in time", f"{g['avg_checkin_time_sec']}s",
             "Time from badge detection to access granted. Kwant passive detection vs manual scanner baseline of 90 seconds.",
             f"Manual baseline: {g['manual_baseline_sec']}s", "up"),
            ("Peak flow",         f"{g['peak_flow_per_hr']}/hr",
             "Maximum workers processed per hour at peak entry time. Yates Construction moved 5,000 workers in 30 min using Kwant.",
             f"Peak hour: {g['peak_hour']}", "nt"),
            ("First badge",       g["first_badge_time"],
             "Time of first worker badge scan today — indicates when site activity began.",
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
          {tip("Fatigue management", "Kwant monitors consecutive workdays and average daily hours per worker. Workers exceeding configurable thresholds are flagged before entering high-risk areas. Fatigued workers are 70% more likely to be involved in accidents (NSC).")} — flagged workers
        </div>""", unsafe_allow_html=True)
        for _, row in FATIGUE_FLAGS.iterrows():
            bg     = "#FCEBEB" if row["risk"] == "High" else "#FAEEDA"
            color  = "#A32D2D" if row["risk"] == "High" else "#854F0B"
            border = "#E24B4A" if row["risk"] == "High" else "#EF9F27"
            icon   = "🔴" if row["risk"] == "High" else "🟡"
            risk_tt = "High risk: worker has exceeded fatigue threshold. Recommend immediate schedule review or rest day." if row["risk"] == "High" else "Medium risk: worker approaching threshold. Monitor closely."
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:9px 12px;border-radius:8px;background:{bg};
                        border:1px solid {border};margin-bottom:7px"
                 title="{risk_tt}">
              <div>
                <div style="font-size:13px;font-weight:600;color:#1a1a1a">{icon} {row['worker']}</div>
                <div style="font-size:11px;color:#888;margin-top:2px">
                  {row['trade']} &nbsp;·&nbsp;
                  <span title="Average hours per day this worker has been on site over their current streak">{row['avg_hrs']}h avg/day</span>
                </div>
              </div>
              <div style="text-align:right" title="Number of consecutive days worked without a rest day">
                <div style="font-size:18px;font-weight:700;color:{color}">{row['streak']}</div>
                <div style="font-size:10px;color:{color}">consec. days</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Subcontractor risk score", "WorkforceOS composite score (0–100) per subcontractor, weighting safety incidents, fatigue flags, compliance rate, and headcount reliability. Lower score = higher risk. Source: Kwant WorkforceOS.")}
        </div>""", unsafe_allow_html=True)
        colors_sub = ["#E24B4A" if s < 55 else "#EF9F27" if s < 72 else "#639922" for s in SUBCONTRACTORS["score"]]
        fig3 = go.Figure(go.Bar(
            x=SUBCONTRACTORS["score"], y=SUBCONTRACTORS["name"],
            orientation="h", marker_color=colors_sub,
            text=[f"{s}  ({w}w · TRIR {t})" for s,w,t in zip(SUBCONTRACTORS["score"], SUBCONTRACTORS["workers"], SUBCONTRACTORS["trir"])],
            textposition="outside", textfont=dict(size=11),
        ))
        fig3.update_layout(height=260, margin=dict(t=5,b=5,l=5,r=100),
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
          {tip("ZoneIQ", "Kwant's real-time indoor location system using badge sensors. Tracks which zone each worker is in and categorizes their time as productive work, moving between zones, or idle.")} — production / transit / downtime per zone
        </div>""", unsafe_allow_html=True)
        zone_tooltips = {
            "production":  "Time workers are actively in the zone performing their trade work",
            "transit":     "Time spent moving between zones, waiting for materials, or traveling to work areas",
            "downtime":    "Idle time — worker present in zone but not actively working. High downtime may indicate scheduling or material delivery issues.",
        }
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
                <span style="font-size:12px;color:#aaa" title="Total workers currently detected in this zone by Kwant location sensors">{total} workers</span>
              </div>
              <div style="display:flex;height:12px;border-radius:6px;overflow:hidden;gap:2px">
                <div style="flex:{p};background:{prod_color};border-radius:6px 0 0 6px"
                     title="{zone_tooltips['production']}"></div>
                <div style="flex:{t};background:#EF9F27"
                     title="{zone_tooltips['transit']}"></div>
                <div style="flex:{d};background:#e0ddd7;border-radius:0 6px 6px 0"
                     title="{zone_tooltips['downtime']}"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:#aaa;margin-top:5px">
                <span style="color:{prod_color};font-weight:600" title="{zone_tooltips['production']}">{p}% production</span>
                <span title="{zone_tooltips['transit']}">{t}% transit</span>
                <span title="{zone_tooltips['downtime']}">{d}% downtime</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Near-miss trend", "A near-miss is an unplanned event that did not result in injury but had the potential to. Tracking trends reveals whether safety conditions are improving or deteriorating. Rising near-misses are a leading indicator of future incidents.")} — last 8 weeks
        </div>""", unsafe_allow_html=True)
        nm_data = [1,0,2,1,3,1,1,2]
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
        accounted_pct = round(m["accounted_for"]/m["total_on_site_at_drill"]*100)
        time_saved = m["benchmark_manual_min"] - m["time_to_full_account_min"]
        st.markdown(f"""<div class="ptitle">
          {tip("Muster point", "Emergency assembly location where all workers report during an evacuation or drill. Kwant tracks who is accounted for in real time vs manual roll call.")} — last drill results
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="font-size:11px;color:#aaa;margin-bottom:12px"
               title="Date and time of the most recent emergency evacuation drill">{m['last_drill']}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
            <div style="text-align:center"
                 title="Workers confirmed at muster point or accounted for via Kwant location data">
              <div style="font-size:38px;font-weight:700;color:{GREEN}">{m['accounted_for']}</div>
              <div style="font-size:11px;color:#aaa">Accounted for</div>
            </div>
            <div style="text-align:center"
                 title="Workers on site at drill time who were not immediately at the muster point — located via badge data">
              <div style="font-size:38px;font-weight:700;color:{RED}">{m['missing']}</div>
              <div style="font-size:11px;color:#aaa">Initially missing</div>
            </div>
            <div style="text-align:center"
                 title="Time from drill start to 100% worker accountability. Kwant benchmark: under 5 min. Manual baseline: 20–45 min.">
              <div style="font-size:38px;font-weight:700;color:{BLUE}">{m['time_to_full_account_min']}m</div>
              <div style="font-size:11px;color:#aaa">Full accountability</div>
            </div>
          </div>
          <div style="background:#EAF3DE;border-radius:8px;padding:10px 14px;margin-bottom:10px"
               title="Time saved vs manual roll call process. Suffolk case study: manual 20–45 min → Kwant under 5 min.">
            <div style="font-size:13px;font-weight:600;color:{GREEN}">
              ✅ {time_saved:.0f} min faster than manual ({m['benchmark_manual_min']} min → {m['time_to_full_account_min']} min)
            </div>
          </div>
          <div style="font-size:11px;color:#aaa;margin-bottom:6px;font-weight:600"
               title="Zones confirmed clear during drill — all workers accounted for or evacuated">ZONES CLEARED</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            {''.join([f"<span style='background:#EAF3DE;color:{GREEN};border:1px solid #97C459;border-radius:5px;padding:3px 9px;font-size:11px'>✓ {z}</span>" for z in m['zones_cleared']])}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Safety KPIs at a glance</div>', unsafe_allow_html=True)
        safety_kpis = [
            ("TRIR", str(KPI["trir"]),
             "Total Recordable Incident Rate. Calculated as (# recordable incidents × 200,000) ÷ total hours worked. OSHA standard metric. Industry avg ~3.0; under 1.0 is excellent.",
             "Target < 1.0", "up"),
            ("Incident-free days", str(KPI["incident_free_days"]),
             "Consecutive calendar days without an OSHA-recordable incident on this jobsite",
             "0 recordable incidents", "up"),
            ("Zone breaches today", str(KPI["zone_breaches"]),
             "Workers detected by ZoneIQ sensors in restricted areas they are not authorized to enter. Each breach triggers an immediate alert to safety managers.",
             "1 unauthorized entry", "dn"),
            ("Near-misses today", str(KPI["near_misses_today"]),
             "Unplanned events with injury potential logged today. Near-misses are leading indicators — 1 serious injury is typically preceded by hundreds of near-misses.",
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
          {tip("Certification compliance", "Tracks active safety certifications for every worker on site. Kwant automatically flags workers with expiring certs and can block site access until renewed.")}
        </div>""", unsafe_allow_html=True)
        cert_tooltips = {
            "OSHA 30-hour":          "30-hour OSHA safety training required for all supervisors and foremen on site",
            "Fall protection":        "Required for anyone working at heights over 6 feet. Covers harness use, anchor points, and rescue procedures.",
            "Scaffold competency":    "Required for workers erecting, modifying, or working on scaffolding. Must be renewed periodically.",
            "Confined space entry":   "Required for entering enclosed spaces like tanks, vaults, or shafts where hazardous atmospheres may be present.",
            "Forklift / telehandler": "Required for operating powered industrial trucks and telescopic material handlers on site.",
        }
        for _, row in CERTIFICATIONS.iterrows():
            pct = round(row["compliant"]/row["total"]*100)
            bar_c = "#E24B4A" if pct < 80 else "#EF9F27" if row["expiring"] > 0 else "#639922"
            badge = (f'<span style="background:#FAEEDA;color:#854F0B;border:1px solid #EF9F27;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px" '
                     f'title="Workers whose certification expires within 30 days — Kwant sends automated renewal reminders">'
                     f'⚠ {row["expiring"]} expiring</span>') if row["expiring"] > 0 else \
                    (f'<span style="background:#EAF3DE;color:{GREEN};border:1px solid #97C459;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px" '
                     f'title="All workers hold valid, current certification">✓ Current</span>')
            cert_tt = cert_tooltips.get(row["cert"], "")
            st.markdown(f"""
            <div style="padding:10px 0;border-bottom:1px solid {BORDER}" title="{cert_tt}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:13px;color:#1a1a1a;font-weight:500">{row['cert']}</span>
                {badge}
              </div>
              <div style="display:flex;align-items:center;gap:10px">
                <div style="flex:1;height:8px;background:#f0ede8;border-radius:4px;overflow:hidden"
                     title="{pct}% of workers hold valid certification">
                  <div style="width:{pct}%;height:100%;background:{bar_c};border-radius:4px"></div>
                </div>
                <span style="font-size:11px;color:#aaa;width:55px;text-align:right"
                      title="Compliant workers / total workers requiring this cert">{row['compliant']}/{row['total']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="ptitle">
          {tip("Overall compliance rate", "Composite percentage of workers with all required certifications current across all cert types. Target: 95%+.")}
        </div>""", unsafe_allow_html=True)
        fig_c = go.Figure(go.Indicator(
            mode="gauge+number", value=KPI["compliance_rate"],
            gauge={"axis":{"range":[0,100],"tickwidth":0},
                   "bar":{"color":"#639922","thickness":0.65},
                   "bgcolor":"#f0ede8","borderwidth":0,
                   "threshold":{"line":{"color":"#1a1a1a","width":2},"thickness":0.75,"value":95}},
            number={"font":{"size":40,"color":"#639922"},"suffix":"%"},
        ))
        fig_c.update_layout(height=160, margin=dict(t=10,b=5,l=20,r=20),
            paper_bgcolor="white", font={"family":"sans-serif"})
        st.plotly_chart(fig_c, use_container_width=True, key="compliance_gauge")

    with c2:
        st.markdown(f"""<div class="ptitle">
          {tip("Change order validation", "Change orders (COs) are contract amendments that adjust scope and payment. Kwant's zone data verifies actual hours worked vs subcontractor-reported hours, protecting the GC from overbilling. A variance over 5% triggers a dispute flag.")} — Kwant hrs vs reported hrs
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#E6F1FB;border-radius:8px;padding:9px 12px;margin-bottom:12px;font-size:12px;color:#0C447C"
             title="Kwant automatically compares hours logged by zone sensor data against what each subcontractor bills on their change orders">
          ℹ️ Kwant location data validates hours worked by zone. Disputes auto-flagged when variance &gt; 5%.
        </div>""", unsafe_allow_html=True)
        for _, row in CHANGE_ORDERS.iterrows():
            is_disputed = row["status"] == "Disputed"
            bg   = "#FCEBEB" if is_disputed else "#EAF3DE"
            bc   = "#E24B4A" if is_disputed else "#97C459"
            icon = "⚠️" if is_disputed else "✅"
            var_c = RED if row["variance"] < -5 else GREEN
            co_tt = "Kwant verified hours are significantly below what the subcontractor reported — flagged for PM review before payment." if is_disputed else "Kwant data and subcontractor report are within acceptable variance — approved for payment."
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
                <div style="text-align:center" title="Hours Kwant's zone sensors recorded workers actively present in this area">
                  <div style="font-size:18px;font-weight:700;color:#1B3FA0">{row['kwant_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Kwant verified</div>
                </div>
                <div style="text-align:center" title="Hours the subcontractor reported on their change order billing">
                  <div style="font-size:18px;font-weight:700;color:#aaa">{row['reported_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Sub reported</div>
                </div>
                <div style="text-align:center" title="Difference between Kwant verified and reported hours. Negative = subcontractor billed more than Kwant recorded.">
                  <div style="font-size:18px;font-weight:700;color:{var_c}">{row['variance']:+d}h</div>
                  <div style="font-size:10px;color:#aaa">Variance</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        total_disputed = CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum()
        st.markdown(f"""
        <div style="background:{BLUE};border-radius:10px;padding:12px 16px;color:white;margin-top:4px"
             title="Total labor hours currently under dispute across all flagged change orders — Kwant data is the evidence the GC uses to negotiate or deny payment">
          <div style="font-size:12px;opacity:.7">Total hours in dispute — protected by Kwant data</div>
          <div style="font-size:28px;font-weight:700;color:{GOLD}">{int(total_disputed)} hrs</div>
          <div style="font-size:11px;opacity:.6;margin-top:2px">
            Equivalent to ~${int(total_disputed * 85 / 1000)}K at blended labor rate
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 5 — KWANT ROI
# ═══════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1B3FA0 0%,#0f2870 100%);border-radius:12px;
                padding:1.25rem 1.75rem;margin-bottom:1.5rem;color:white">
      <div style="font-size:16px;font-weight:700">Kwant ROI — Hudson Yards Tower C</div>
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
        "Manual sign-in: 25 min average per worker including badge scan + verification. Kwant passive detection: worker walks through without stopping. Suffolk saved 27,000 hours over 296 workdays.")
    efficiency_card(pe2, "Worker onboarding",
        ro["onboarding_manual_min"], ro["onboarding_kwant_min"], " min", "Suffolk ROI Study Q1 2026",
        "Manual onboarding: paper forms, in-person cert checks, manual data entry — 90 min avg. Kwant digital onboarding: mobile-first, completed before arriving on site. Suffolk: 1,811 hours saved across 2,415 workers.")
    efficiency_card(pe3, "Emergency accountability",
        ro["emergency_manual_min"], ro["emergency_kwant_min"], " min", "Yates / Suffolk case studies",
        "Manual muster roll call: 20–45 min to account for all workers. Kwant: real-time badge location data shows exactly who is where instantly. Critical in actual emergencies.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="ptitle">Project-level impact</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    roi_cards = [
        ("185,000", "Work hours captured",
         "Verified at controlled entry points",
         "Total workforce hours recorded by Kwant badge and sensor data — replacing manual timesheets. 100% verified vs estimated.", r1),
        ("100%", "Digital reporting",
         "Zero paper-based reports",
         "All daily reports, incident logs, and compliance records generated digitally via Kwant — eliminating paper trails and manual compilation.", r2),
        ("75%", "Faster incident response",
         "vs manual process · EllisDon benchmark",
         "EllisDon reduced incident response time by 75% using Kwant real-time location data — safety teams know exactly where workers are during any event.", r3),
        (f"${ro['cost_savings_low_k']}K–${ro['cost_savings_high_k']}K", "Est. savings / incident avoided",
         "1–4 worker incident reduction · Yates benchmark",
         "Direct + indirect cost savings from preventing 1–4 worker incidents per project. Includes medical costs, lost productivity, legal exposure, and insurance impact. Yates benchmark: $50K–$500K range.", r4),
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
          {tip("Admin time saved", "Hours per week the project team saves by eliminating manual reporting, certification tracking, headcount reconciliation, and compliance documentation. Benchmarked from Yates Construction (5–10 hrs/week per project team).")} — this project
        </div>""", unsafe_allow_html=True)
        weeks_elapsed = PROJECT["week"]
        total_admin_saved = ro["admin_hrs_saved_weekly"] * weeks_elapsed
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px"
                 title="Hours saved per week vs manual processes — Yates benchmark: 5–10 hrs/week">
              <div style="font-size:42px;font-weight:700;color:{BLUE}">{ro['admin_hrs_saved_weekly']}</div>
              <div style="font-size:12px;color:#aaa">hrs saved / week</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Yates benchmark: 5–10 hrs/wk</div>
            </div>
            <div style="text-align:center;padding:12px"
                 title="Cumulative admin hours saved since project started on Kwant — Week 34 × 7 hrs/week">
              <div style="font-size:42px;font-weight:700;color:{GREEN}">{total_admin_saved}</div>
              <div style="font-size:12px;color:#aaa">total hrs saved to date</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Over {weeks_elapsed} weeks on Kwant</div>
            </div>
          </div>
          <div style="background:#f5f3ef;border-radius:8px;padding:10px 14px;margin-top:12px;
                      font-size:12px;color:#666;text-align:center"
               title="Total hours saved expressed as full-time equivalent weeks of PM overhead eliminated">
            Equivalent to <strong>{round(total_admin_saved/40, 1)} weeks</strong> of full-time PM overhead eliminated
          </div>
        </div>""", unsafe_allow_html=True)

    with r_right:
        st.markdown(f"""<div class="ptitle">
          {tip("Change order protection", "Dollar value of hours under dispute that Kwant's location data is defending. Without Kwant, GCs typically pay disputed change orders due to lack of evidence. EllisDon used location data to prevent a false injury claim and verify change order work.")} — value defended
        </div>""", unsafe_allow_html=True)
        disputed_hrs = int(CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum())
        value_k = round(disputed_hrs * 85 / 1000, 1)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px"
                 title="Total hours across all disputed change orders where Kwant data shows fewer hours than subcontractor billed">
              <div style="font-size:42px;font-weight:700;color:{RED}">{disputed_hrs}</div>
              <div style="font-size:12px;color:#aaa">disputed hours</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Flagged by Kwant zone data</div>
            </div>
            <div style="text-align:center;padding:12px"
                 title="Financial value of disputed hours at $85/hr blended labor rate — money the GC is protected from overbilling">
              <div style="font-size:42px;font-weight:700;color:{GREEN}">${value_k}K</div>
              <div style="font-size:12px;color:#aaa">value protected</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">At $85/hr blended rate</div>
            </div>
          </div>
          <div style="background:#EAF3DE;border-radius:8px;padding:10px 14px;margin-top:12px;
                      font-size:12px;color:{GREEN};text-align:center">
            ✓ EllisDon: location data prevented a false injury claim + verified change order work
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    st.caption("ROI benchmarks: Suffolk Construction Q1 2026, Yates Construction Q1 2026, EllisDon. All project figures are simulated for demonstration.")

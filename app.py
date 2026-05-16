import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from mock_data import (
    PROJECT, WORKFORCEOS_SCORES, KPI, ROI,
    HOURLY_HEADCOUNT, WEEKLY_TREND, TRADES, ZONES,
    FATIGUE_FLAGS, SUBCONTRACTORS, CERTIFICATIONS,
    MUSTER, GATE, CHANGE_ORDERS, ALERTS
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kwant · PM Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BLUE   = "#1B3FA0"
GOLD   = "#F5C518"
GREEN  = "#3B6D11"
AMBER  = "#BA7517"
RED    = "#A32D2D"
LIGHT  = "#f8f7f4"
BORDER = "#e8e6e0"

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background: {LIGHT}; }}
  [data-testid="stHeader"] {{ background: transparent; }}
  .block-container {{ padding: 1.25rem 2rem 2rem; max-width: 1440px; }}
  div[data-testid="stTabs"] button {{ font-size: 13px; font-weight: 500; }}

  .kw-header {{
    background: linear-gradient(135deg, {BLUE} 0%, #0f2870 100%);
    border-radius: 12px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .kw-header-left {{ color: white; }}
  .kw-proj-name {{ font-size: 20px; font-weight: 700; margin: 0; }}
  .kw-proj-sub  {{ font-size: 12px; opacity: .7; margin: 4px 0 0; }}
  .kw-badges    {{ display: flex; gap: 8px; flex-wrap: wrap; }}

  .badge {{ display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:600;
            padding:4px 10px;border-radius:20px;border:1.5px solid; }}
  .b-green  {{ background:#EAF3DE;color:{GREEN};border-color:#97C459; }}
  .b-amber  {{ background:#FAEEDA;color:#854F0B;border-color:#EF9F27; }}
  .b-red    {{ background:#FCEBEB;color:{RED};border-color:#E24B4A; }}
  .b-blue   {{ background:#E6F1FB;color:#0C447C;border-color:#85B7EB; }}
  .b-white  {{ background:rgba(255,255,255,.15);color:white;border-color:rgba(255,255,255,.4); }}
  .dot      {{ width:7px;height:7px;border-radius:50%;background:currentColor;
               animation:pulse 1.8s ease-in-out infinite;display:inline-block; }}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}

  .mcard {{
    background: white; border-radius: 10px; padding: 1rem 1.2rem;
    border: 1px solid {BORDER}; height: 100%;
  }}
  .mlabel {{ font-size: 10px; color: #999; text-transform: uppercase;
             letter-spacing: .06em; margin-bottom: 4px; }}
  .mval   {{ font-size: 26px; font-weight: 700; color: #1a1a1a; line-height: 1.1; }}
  .mdelta {{ font-size: 11px; margin-top: 5px; }}
  .up     {{ color: {GREEN}; }} .dn {{ color: {RED}; }} .nt {{ color: #999; }}

  .panel {{
    background: white; border-radius: 10px; border: 1px solid {BORDER};
    padding: 1.25rem; height: 100%;
  }}
  .ptitle {{
    font-size: 10px; font-weight: 700; color: #aaa;
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: .9rem;
  }}

  .alert-item {{
    display: flex; gap: 10px; padding: 8px 10px; border-radius: 8px;
    margin-bottom: 7px; border-left: 3px solid;
  }}
  .alert-title {{ font-size: 12px; color: #1a1a1a; line-height: 1.4; }}
  .alert-meta  {{ font-size: 10px; color: #bbb; margin-top: 2px; }}

  .roi-block {{
    background: {BLUE}; border-radius: 10px; padding: 1rem 1.25rem; text-align: center; color: white;
  }}
  .roi-val  {{ font-size: 32px; font-weight: 700; color: {GOLD}; line-height: 1; }}
  .roi-label{{ font-size: 11px; opacity: .8; margin-top: 5px; }}
  .roi-sub  {{ font-size: 10px; opacity: .55; margin-top: 3px; }}

  .muster-big {{ font-size: 48px; font-weight: 700; line-height: 1; }}
  .muster-ok  {{ color: {GREEN}; }}
  .muster-bad {{ color: {RED}; }}

  .co-disputed {{ color: {RED}; font-weight: 600; }}
  .co-approved {{ color: {GREEN}; font-weight: 600; }}

  div[data-testid="stMetric"] {{ background: white; border-radius: 10px;
    border: 1px solid {BORDER}; padding: .75rem 1rem; }}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
pct_complete = round(PROJECT["week"] / PROJECT["total_weeks"] * 100)
st.markdown(f"""
<div class="kw-header">
  <div class="kw-header-left">
    <div class="kw-proj-name">🏗️ {PROJECT['name']}</div>
    <div class="kw-proj-sub">
      {PROJECT['location']} &nbsp;·&nbsp; Week {PROJECT['week']} of {PROJECT['total_weeks']}
      ({pct_complete}% complete) &nbsp;·&nbsp; Phase: {PROJECT['phase']}
      &nbsp;·&nbsp; {PROJECT['date']} &nbsp;·&nbsp; Updated 2 min ago
    </div>
  </div>
  <div class="kw-badges">
    <span class="badge b-white"><span class="dot"></span> Live</span>
    <span class="badge b-amber">⚠ 3 open alerts</span>
    <span class="badge b-red">🔴 7 fatigue flags</span>
    <span class="badge b-amber">📋 2 CO disputes</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "👷 Workforce & Fatigue",
    "🛡️ Safety & Zones", "📋 Compliance & Change Orders", "💡 Kwant ROI"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════
with tab1:

    # WorkforceOS scores
    st.markdown('<div class="ptitle">WorkforceOS — AI project risk scores</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    score_meta = {
        "Safety":       ("#BA7517", "#FAEEDA"),
        "Productivity": ("#BA7517", "#FAEEDA"),
        "Compliance":   ("#3B6D11", "#EAF3DE"),
    }
    for col, (label, data) in zip([sc1, sc2, sc3], WORKFORCEOS_SCORES.items()):
        bar_c, bg_c = score_meta[label]
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["score"],
                gauge={
                    "axis": {"range": [0,100], "tickwidth":0, "tickcolor":"white"},
                    "bar":  {"color": bar_c, "thickness": 0.65},
                    "bgcolor": "#f0ede8", "borderwidth": 0,
                    "threshold": {"line": {"color":"#1a1a1a","width":2},
                                  "thickness":0.75, "value": data["target"]},
                },
                number={"font":{"size":38,"color":bar_c}},
            ))
            fig.update_layout(height=150, margin=dict(t=20,b=5,l=20,r=20),
                paper_bgcolor="white", plot_bgcolor="white",
                font={"family":"sans-serif"})
            st.plotly_chart(fig, use_container_width=True, key=f"g_{label}")
            st.markdown(f"""
            <div style="background:{bg_c};border-radius:8px;padding:7px 10px;margin-top:-8px;margin-bottom:6px">
              <div style="font-size:12px;font-weight:600;color:#1a1a1a">{label} — {data['score']}/100</div>
              <div style="font-size:11px;color:#666;margin-top:2px">{data['note']}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # KPI row
    st.markdown('<div class="ptitle">Today at a glance</div>', unsafe_allow_html=True)
    k = KPI
    kpis = [
        ("On-site now",        str(k["on_site"]),               f"↑ +12 vs yesterday", "up"),
        ("Utilization",        f"{k['utilization']}%",          f"vs {k['planned']} planned", "nt"),
        ("TRIR",               str(k["trir"]),                  "Target < 1.0 ✓", "up"),
        ("Incident-free days", str(k["incident_free_days"]),    "0 recordable incidents", "up"),
        ("Near-misses today",  str(k["near_misses_today"]),     "↑ +1 vs 7-day avg", "dn"),
        ("Fatigue flags",      str(k["fatigue_flags"]),         "7 workers flagged", "dn"),
        ("Overtime flags (7d)",str(k["overtime_flags_7d"]),     "↑ +6 vs prior week", "dn"),
        ("Schedule variance",  f"{k['schedule_variance_days']}d", "Behind plan", "dn"),
    ]
    cols = st.columns(8)
    for col, (label, val, delta, direction) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="mcard">
              <div class="mlabel">{label}</div>
              <div class="mval">{val}</div>
              <div class="mdelta {direction}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Headcount chart + Alerts
    ch1, ch2 = st.columns([2,1])
    with ch1:
        st.markdown('<div class="ptitle">Hourly headcount — today vs planned</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["actual"]-HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Workforce", marker_color="#378ADD", )
        fig.add_bar(x=HOURLY_HEADCOUNT["hour"],
                    y=HOURLY_HEADCOUNT["fatigue_flagged"],
                    name="Fatigue-flagged", marker_color="#E24B4A", )
        fig.add_scatter(x=HOURLY_HEADCOUNT["hour"], y=HOURLY_HEADCOUNT["planned"],
                        name="Planned (310)", mode="lines",
                        line=dict(color="#bbb", dash="dash", width=1.5))
        fig.update_layout(barmode="stack", height=260,
            margin=dict(t=5,b=5,l=5,r=5),
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
        for a in ALERTS:
            bg, bc = sev_style.get(a["severity"], ("#f5f5f5","#ccc"))
            st.markdown(f"""
            <div class="alert-item" style="background:{bg};border-color:{bc}">
              <div>
                <div class="alert-title">{a['icon']} {a['title']}</div>
                <div class="alert-meta">{a['time']} · {a['source']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Weekly trend
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="ptitle">8-week workforce trend</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_scatter(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["planned"],
                     name="Planned", line=dict(color="#bbb", dash="dash", width=1.5), mode="lines")
    fig2.add_scatter(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["actual"],
                     name="Actual", line=dict(color="#378ADD", width=2.5), mode="lines+markers",
                     marker=dict(size=7))
    fig2.add_bar(x=WEEKLY_TREND["week"], y=WEEKLY_TREND["fatigue_flags"],
                 name="Fatigue flags", marker_color="#E24B4A", opacity=0.7,
                 yaxis="y2")
    fig2.update_layout(
        height=220, margin=dict(t=5,b=5,l=5,r=5),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
        yaxis=dict(range=[0,360], gridcolor="#f5f3ef", tickfont=dict(size=11)),
        yaxis2=dict(range=[0,30], overlaying="y", side="right",
                    showgrid=False, tickfont=dict(size=10), title="Fatigue flags"),
        xaxis=dict(tickfont=dict(size=11), showgrid=False),
        font=dict(family="sans-serif"))
    st.plotly_chart(fig2, use_container_width=True, key="weekly")


# ═══════════════════════════════════════════════════════════════
# TAB 2 — WORKFORCE & FATIGUE
# ═══════════════════════════════════════════════════════════════
with tab2:
    w1, w2 = st.columns(2)

    with w1:
        st.markdown('<div class="ptitle">Workforce by trade — actual vs planned</div>', unsafe_allow_html=True)
        colors = ["#E24B4A" if p < 75 else "#EF9F27" if p < 90 else "#378ADD"
                  for p in TRADES["pct"]]
        fig = go.Figure()
        fig.add_bar(y=TRADES["trade"], x=TRADES["planned"], orientation="h",
                    name="Planned", marker_color="#e8e6e0")
        fig.add_bar(y=TRADES["trade"], x=TRADES["actual"], orientation="h",
                    name="Actual", marker_color=colors,
                    text=[f"{a}/{p}  ({round(a/p*100)}%)"
                          for a,p in zip(TRADES["actual"], TRADES["planned"])],
                    textposition="outside", textfont=dict(size=11))
        fig.update_layout(barmode="overlay", height=320,
            margin=dict(t=5,b=5,l=5,r=80),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig, use_container_width=True, key="trades")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Gate throughput — today</div>', unsafe_allow_html=True)
        g = GATE
        gcols = st.columns(3)
        gate_kpis = [
            ("Avg check-in time", f"{g['avg_checkin_time_sec']}s", f"Manual baseline: {g['manual_baseline_sec']}s", "up"),
            ("Peak flow",         f"{g['peak_flow_per_hr']}/hr",   f"Peak hour: {g['peak_hour']}", "nt"),
            ("First badge",       g["first_badge_time"],           "Continuous gate flow", "nt"),
        ]
        for col, (label, val, delta, direction) in zip(gcols, gate_kpis):
            with col:
                st.markdown(f"""
                <div class="mcard">
                  <div class="mlabel">{label}</div>
                  <div class="mval" style="font-size:20px">{val}</div>
                  <div class="mdelta {direction}">{delta}</div>
                </div>""", unsafe_allow_html=True)

    with w2:
        st.markdown('<div class="ptitle">Fatigue management — all flagged workers</div>', unsafe_allow_html=True)
        for _, row in FATIGUE_FLAGS.iterrows():
            bg     = "#FCEBEB" if row["risk"] == "High" else "#FAEEDA"
            color  = "#A32D2D" if row["risk"] == "High" else "#854F0B"
            border = "#E24B4A" if row["risk"] == "High" else "#EF9F27"
            icon   = "🔴" if row["risk"] == "High" else "🟡"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:9px 12px;border-radius:8px;background:{bg};
                        border:1px solid {border};margin-bottom:7px">
              <div>
                <div style="font-size:13px;font-weight:600;color:#1a1a1a">{icon} {row['worker']}</div>
                <div style="font-size:11px;color:#888;margin-top:2px">
                  {row['trade']} &nbsp;·&nbsp; {row['avg_hrs']}h avg/day
                </div>
              </div>
              <div style="text-align:right">
                <div style="font-size:18px;font-weight:700;color:{color}">{row['streak']}</div>
                <div style="font-size:10px;color:{color}">consec. days</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Subcontractor risk scores (WorkforceOS)</div>', unsafe_allow_html=True)
        colors_sub = ["#E24B4A" if s < 55 else "#EF9F27" if s < 72 else "#639922"
                      for s in SUBCONTRACTORS["score"]]
        fig3 = go.Figure(go.Bar(
            x=SUBCONTRACTORS["score"], y=SUBCONTRACTORS["name"],
            orientation="h", marker_color=colors_sub,
            text=[f"{s}  ({w}w · TRIR {t})"
                  for s,w,t in zip(SUBCONTRACTORS["score"],
                                   SUBCONTRACTORS["workers"],
                                   SUBCONTRACTORS["trir"])],
            textposition="outside", textfont=dict(size=11),
        ))
        fig3.update_layout(height=260, margin=dict(t=5,b=5,l=5,r=100),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(range=[0,130], showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig3, use_container_width=True, key="subs")


# ═══════════════════════════════════════════════════════════════
# TAB 3 — SAFETY & ZONES
# ═══════════════════════════════════════════════════════════════
with tab3:
    s1, s2 = st.columns([1, 1])

    with s1:
        st.markdown('<div class="ptitle">ZoneIQ — production / transit / downtime</div>', unsafe_allow_html=True)
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
                <span style="font-size:12px;color:#aaa">{total} workers</span>
              </div>
              <div style="display:flex;height:12px;border-radius:6px;overflow:hidden;gap:2px">
                <div style="flex:{p};background:{prod_color};border-radius:6px 0 0 6px"></div>
                <div style="flex:{t};background:#EF9F27"></div>
                <div style="flex:{d};background:#e0ddd7;border-radius:0 6px 6px 0"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;
                          color:#aaa;margin-top:5px">
                <span style="color:{prod_color};font-weight:600">{p}% production</span>
                <span>{t}% transit</span>
                <span>{d}% downtime</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # Safety trend (simple sparkline)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Near-miss trend — last 8 weeks</div>', unsafe_allow_html=True)
        nm_data = [1, 0, 2, 1, 3, 1, 1, 2]
        fig_nm = go.Figure(go.Scatter(
            x=WEEKLY_TREND["week"], y=nm_data,
            mode="lines+markers",
            line=dict(color="#E24B4A", width=2),
            marker=dict(size=8, color="#E24B4A"),
            fill="tozeroy", fillcolor="rgba(226,75,74,0.08)"
        ))
        fig_nm.update_layout(height=180, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(gridcolor="#f5f3ef", tickfont=dict(size=11), dtick=1),
            xaxis=dict(tickfont=dict(size=11), showgrid=False),
            font=dict(family="sans-serif"))
        st.plotly_chart(fig_nm, use_container_width=True, key="nm_trend")

    with s2:
        # Muster point
        m = MUSTER
        accounted_pct = round(m["accounted_for"]/m["total_on_site_at_drill"]*100)
        time_saved = m["benchmark_manual_min"] - m["time_to_full_account_min"]

        st.markdown('<div class="ptitle">Muster point — last drill</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="font-size:11px;color:#aaa;margin-bottom:12px">{m['last_drill']}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
            <div style="text-align:center">
              <div style="font-size:38px;font-weight:700;color:{GREEN}">{m['accounted_for']}</div>
              <div style="font-size:11px;color:#aaa">Accounted for</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:38px;font-weight:700;color:{RED}">{m['missing']}</div>
              <div style="font-size:11px;color:#aaa">Initially missing</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:38px;font-weight:700;color:{BLUE}">{m['time_to_full_account_min']}m</div>
              <div style="font-size:11px;color:#aaa">Full accountability</div>
            </div>
          </div>
          <div style="background:#EAF3DE;border-radius:8px;padding:10px 14px;margin-bottom:10px">
            <div style="font-size:13px;font-weight:600;color:{GREEN}">
              ✅ {time_saved:.0f} min faster than manual ({m['benchmark_manual_min']} min → {m['time_to_full_account_min']} min)
            </div>
          </div>
          <div style="font-size:11px;color:#aaa;margin-bottom:6px;font-weight:600">ZONES CLEARED</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            {''.join([f'<span style="background:#EAF3DE;color:{GREEN};border:1px solid #97C459;border-radius:5px;padding:3px 9px;font-size:11px">✓ {z}</span>' for z in m['zones_cleared']])}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Safety KPIs at a glance</div>', unsafe_allow_html=True)
        safety_kpis = [
            ("TRIR", str(KPI["trir"]), "Target < 1.0", "up"),
            ("Incident-free days", str(KPI["incident_free_days"]), "0 recordable incidents", "up"),
            ("Zone breaches today", str(KPI["zone_breaches"]), "1 unauthorized entry", "dn"),
            ("Near-misses today", str(KPI["near_misses_today"]), "+1 vs 7-day avg", "dn"),
        ]
        scols = st.columns(2)
        for i, (label, val, delta, direction) in enumerate(safety_kpis):
            with scols[i % 2]:
                st.markdown(f"""
                <div class="mcard" style="margin-bottom:10px">
                  <div class="mlabel">{label}</div>
                  <div class="mval">{val}</div>
                  <div class="mdelta {direction}">{delta}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 4 — COMPLIANCE & CHANGE ORDERS
# ═══════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="ptitle">Certification compliance</div>', unsafe_allow_html=True)
        for _, row in CERTIFICATIONS.iterrows():
            pct = round(row["compliant"]/row["total"]*100)
            bar_c = "#E24B4A" if pct < 80 else "#EF9F27" if row["expiring"] > 0 else "#639922"
            badge = (f'<span style="background:#FAEEDA;color:#854F0B;border:1px solid #EF9F27;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px">'
                     f'⚠ {row["expiring"]} expiring</span>') if row["expiring"] > 0 else \
                    (f'<span style="background:#EAF3DE;color:{GREEN};border:1px solid #97C459;'
                     f'border-radius:4px;padding:2px 8px;font-size:11px">✓ Current</span>')
            st.markdown(f"""
            <div style="padding:10px 0;border-bottom:1px solid {BORDER}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:13px;color:#1a1a1a;font-weight:500">{row['cert']}</span>
                {badge}
              </div>
              <div style="display:flex;align-items:center;gap:10px">
                <div style="flex:1;height:8px;background:#f0ede8;border-radius:4px;overflow:hidden">
                  <div style="width:{pct}%;height:100%;background:{bar_c};border-radius:4px"></div>
                </div>
                <span style="font-size:11px;color:#aaa;width:55px;text-align:right">
                  {row['compliant']}/{row['total']}
                </span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ptitle">Overall compliance rate</div>', unsafe_allow_html=True)
        fig_c = go.Figure(go.Indicator(
            mode="gauge+number",
            value=KPI["compliance_rate"],
            gauge={"axis": {"range":[0,100],"tickwidth":0},
                   "bar": {"color":"#639922","thickness":0.65},
                   "bgcolor":"#f0ede8","borderwidth":0,
                   "threshold":{"line":{"color":"#1a1a1a","width":2},
                                "thickness":0.75,"value":95}},
            number={"font":{"size":40,"color":"#639922"},"suffix":"%"},
        ))
        fig_c.update_layout(height=160, margin=dict(t=10,b=5,l=20,r=20),
            paper_bgcolor="white", font={"family":"sans-serif"})
        st.plotly_chart(fig_c, use_container_width=True, key="compliance_gauge")

    with c2:
        st.markdown('<div class="ptitle">Change order validation — Kwant hours vs reported hours</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#E6F1FB;border-radius:8px;padding:9px 12px;margin-bottom:12px;font-size:12px;color:#0C447C">
          ℹ️ Kwant location data validates hours worked by zone. Disputes flagged automatically when variance > 5%.
        </div>""", unsafe_allow_html=True)

        for _, row in CHANGE_ORDERS.iterrows():
            is_disputed = row["status"] == "Disputed"
            bg    = "#FCEBEB" if is_disputed else "#EAF3DE"
            bc    = "#E24B4A" if is_disputed else "#97C459"
            icon  = "⚠️" if is_disputed else "✅"
            var_c = RED if row["variance"] < -5 else GREEN
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {bc};border-radius:10px;
                        padding:12px 14px;margin-bottom:10px">
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
                <div style="text-align:center">
                  <div style="font-size:18px;font-weight:700;color:#1B3FA0">{row['kwant_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Kwant verified</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:18px;font-weight:700;color:#aaa">{row['reported_hrs']}h</div>
                  <div style="font-size:10px;color:#aaa">Sub reported</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:18px;font-weight:700;color:{var_c}">{row['variance']:+d}h</div>
                  <div style="font-size:10px;color:#aaa">Variance</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        total_disputed = CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum()
        st.markdown(f"""
        <div style="background:{BLUE};border-radius:10px;padding:12px 16px;color:white;margin-top:4px">
          <div style="font-size:12px;opacity:.7">Total hours in dispute — protected by Kwant data</div>
          <div style="font-size:28px;font-weight:700;color:{GOLD}">{int(total_disputed)} hrs</div>
          <div style="font-size:11px;opacity:.6;margin-top:2px">
            Equivalent to ~${int(total_disputed * 85 / 1000)}K at blended labor rate
          </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 5 — KWANT ROI
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1B3FA0 0%,#0f2870 100%);border-radius:12px;
                padding:1.25rem 1.75rem;margin-bottom:1.5rem;color:white">
      <div style="font-size:16px;font-weight:700">Kwant ROI — Hudson Yards Tower C</div>
      <div style="font-size:12px;opacity:.65;margin-top:4px">
        Benchmarks sourced from Suffolk (Q1 2026), Yates Construction (Q1 2026), and EllisDon case studies.
        Figures are illustrative projections for this project based on published outcomes.
      </div>
    </div>""", unsafe_allow_html=True)

    r = ROI

    # Process efficiency row
    st.markdown('<div class="ptitle">Process efficiency — manual vs Kwant</div>', unsafe_allow_html=True)
    pe1, pe2, pe3 = st.columns(3)

    def efficiency_card(col, title, manual, kwant, unit, source):
        improvement = round((manual - kwant) / manual * 100)
        with col:
            st.markdown(f"""
            <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.1rem">
              <div style="font-size:10px;color:#aaa;text-transform:uppercase;
                          letter-spacing:.06em;margin-bottom:10px">{title}</div>
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
                    r["checkin_manual_min"], r["checkin_kwant_min"], " min", "Suffolk ROI Study Q1 2026")
    efficiency_card(pe2, "Worker onboarding",
                    r["onboarding_manual_min"], r["onboarding_kwant_min"], " min", "Suffolk ROI Study Q1 2026")
    efficiency_card(pe3, "Emergency accountability",
                    r["emergency_manual_min"], r["emergency_kwant_min"], " min", "Yates / Suffolk case studies")

    st.markdown("<br>", unsafe_allow_html=True)

    # Big ROI numbers
    st.markdown('<div class="ptitle">Project-level impact</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    roi_cards = [
        ("185,000", "Work hours captured", "Verified at controlled entry points", r1),
        ("100%", "Digital reporting", "Zero paper-based reports", r2),
        ("75%", "Faster incident response", "vs manual process · EllisDon benchmark", r3),
        (f"${r['cost_savings_low_k']}K–${r['cost_savings_high_k']}K", "Est. savings / incident avoided",
         "1–4 worker incident reduction · Yates benchmark", r4),
    ]
    for val, label, sub, col in roi_cards:
        with col:
            st.markdown(f"""
            <div class="roi-block">
              <div class="roi-val">{val}</div>
              <div class="roi-label">{label}</div>
              <div class="roi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Admin time saved
    r_left, r_right = st.columns(2)
    with r_left:
        st.markdown('<div class="ptitle">Admin time saved — this project</div>', unsafe_allow_html=True)
        weeks_elapsed = PROJECT["week"]
        total_admin_saved = r["admin_hrs_saved_weekly"] * weeks_elapsed
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px">
              <div style="font-size:42px;font-weight:700;color:{BLUE}">{r['admin_hrs_saved_weekly']}</div>
              <div style="font-size:12px;color:#aaa">hrs saved / week</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Yates benchmark: 5–10 hrs/wk</div>
            </div>
            <div style="text-align:center;padding:12px">
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
        st.markdown('<div class="ptitle">Change order protection — total value defended</div>', unsafe_allow_html=True)
        disputed_hrs = int(CHANGE_ORDERS[CHANGE_ORDERS["status"]=="Disputed"]["variance"].abs().sum())
        blended_rate = 85
        value_k = round(disputed_hrs * blended_rate / 1000, 1)
        st.markdown(f"""
        <div style="background:white;border:1px solid {BORDER};border-radius:10px;padding:1.25rem">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="text-align:center;padding:12px">
              <div style="font-size:42px;font-weight:700;color:{RED}">{disputed_hrs}</div>
              <div style="font-size:12px;color:#aaa">disputed hours</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px">Flagged by Kwant zone data</div>
            </div>
            <div style="text-align:center;padding:12px">
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
    st.caption("ROI benchmarks from Kwant case studies: Suffolk Construction Q1 2026, Yates Construction Q1 2026, EllisDon. All project figures are simulated for demonstration.")


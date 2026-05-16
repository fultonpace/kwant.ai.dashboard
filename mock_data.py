import pandas as pd
import numpy as np

PROJECT = {
    "name": "Hudson Yards — Tower C",
    "location": "New York, NY",
    "week": 34,
    "total_weeks": 78,
    "date": "May 15, 2026",
    "planned_headcount": 310,
    "contract_value_m": 480,
    "phase": "MEP Rough-in + Curtain Wall",
}

WORKFORCEOS_SCORES = {
    "Safety":       {"score": 72, "target": 85, "note": "2 near-misses · 1 zone breach · TRIR 0.82"},
    "Productivity": {"score": 68, "target": 85, "note": "Electrical 36% below plan · -3d schedule"},
    "Compliance":   {"score": 84, "target": 85, "note": "11 certs expiring · COI current all subs"},
}

KPI = {
    "on_site": 284,
    "planned": 310,
    "utilization": 92,
    "avg_hrs": 6.4,
    "overtime_flags_7d": 19,
    "incidents": 0,
    "incident_free_days": 19,
    "trir": 0.82,
    "near_misses_today": 2,
    "zone_breaches": 1,
    "schedule_variance_days": -3,
    "compliance_rate": 96,
    "fatigue_flags": 7,
}

ROI = {
    "checkin_manual_min": 25,
    "checkin_kwant_min": 4,
    "onboarding_manual_min": 90,
    "onboarding_kwant_min": 38,
    "emergency_manual_min": 35,
    "emergency_kwant_min": 4,
    "admin_hrs_saved_weekly": 7,
    "hrs_captured_total": 185000,
    "cost_savings_low_k": 40,
    "cost_savings_high_k": 160,
    "incident_response_reduction_pct": 75,
    "digital_reporting_pct": 95,
}

HOURLY_HEADCOUNT = pd.DataFrame({
    "hour":            ["6AM","7AM","8AM","9AM","10AM","11AM","12PM","1PM","2PM","3PM"],
    "actual":          [14,   88,  196,  251,  268,   272,   241,  258,  271,  284],
    "fatigue_flagged": [0,     0,    4,    7,    7,     7,     6,    7,    7,    7],
    "planned":         [310]*10,
})

TRADES = pd.DataFrame([
    {"trade": "Concrete / formwork", "actual": 58, "planned": 60},
    {"trade": "Structural steel",    "actual": 44, "planned": 48},
    {"trade": "Curtain wall",        "actual": 41, "planned": 45},
    {"trade": "MEP — mechanical",    "actual": 36, "planned": 38},
    {"trade": "MEP — electrical",    "actual": 14, "planned": 22},
    {"trade": "MEP — plumbing",      "actual": 26, "planned": 28},
    {"trade": "Carpentry / framing", "actual": 38, "planned": 40},
    {"trade": "Laborers / general",  "actual": 27, "planned": 29},
])
TRADES["pct"] = (TRADES["actual"] / TRADES["planned"] * 100).round(0).astype(int)

ZONES = pd.DataFrame([
    {"zone": "Structure (L12-22)", "workers": 97, "production": 71, "transit": 18, "downtime": 8},
    {"zone": "MEP rough-in",       "workers": 62, "production": 38, "transit": 14, "downtime": 10},
    {"zone": "Curtain wall",       "workers": 41, "production": 24, "transit": 10, "downtime": 7},
    {"zone": "Staging / grade",    "workers": 84, "production": 62, "transit": 15, "downtime": 7},
])

FATIGUE_FLAGS = pd.DataFrame([
    {"worker": "R. Gutierrez", "trade": "Electrical", "streak": 9, "avg_hrs": 10.2, "risk": "High"},
    {"worker": "M. Okafor",    "trade": "Electrical", "streak": 9, "avg_hrs": 9.8,  "risk": "High"},
    {"worker": "D. Reyes",     "trade": "Concrete",   "streak": 6, "avg_hrs": 10.1, "risk": "High"},
    {"worker": "T. Callahan",  "trade": "Scaffold",   "streak": 7, "avg_hrs": 9.4,  "risk": "Medium"},
    {"worker": "J. Morales",   "trade": "MEP Mech",   "streak": 6, "avg_hrs": 9.1,  "risk": "Medium"},
    {"worker": "B. Osei",      "trade": "Laborers",   "streak": 5, "avg_hrs": 8.9,  "risk": "Medium"},
    {"worker": "C. Huang",     "trade": "Steel",      "streak": 5, "avg_hrs": 8.5,  "risk": "Medium"},
])

SUBCONTRACTORS = pd.DataFrame([
    {"name": "Stahl Electric",   "score": 41, "workers": 14, "risk": "High",   "trir": 2.1, "compliance": 71},
    {"name": "Pyramid Scaffold", "score": 58, "workers": 38, "risk": "Medium", "trir": 1.4, "compliance": 83},
    {"name": "CoreSteel LLC",    "score": 71, "workers": 44, "risk": "Medium", "trir": 0.9, "compliance": 91},
    {"name": "Harbor Curtain",   "score": 79, "workers": 41, "risk": "Low",    "trir": 0.7, "compliance": 94},
    {"name": "Summit MEP",       "score": 82, "workers": 62, "risk": "Low",    "trir": 0.6, "compliance": 97},
    {"name": "Apex Concrete",    "score": 76, "workers": 58, "risk": "Low",    "trir": 0.8, "compliance": 95},
]).sort_values("score")

CERTIFICATIONS = pd.DataFrame([
    {"cert": "OSHA 30-hour",          "compliant": 284, "total": 284, "expiring": 0},
    {"cert": "Fall protection",       "compliant": 271, "total": 284, "expiring": 0},
    {"cert": "Scaffold competency",   "compliant": 38,  "total": 44,  "expiring": 6},
    {"cert": "Confined space entry",  "compliant": 17,  "total": 22,  "expiring": 5},
    {"cert": "Forklift / telehandler","compliant": 29,  "total": 29,  "expiring": 0},
])

MUSTER = {
    "last_drill": "May 12, 2026 · 10:15 AM",
    "total_on_site_at_drill": 271,
    "accounted_for": 263,
    "missing": 8,
    "time_to_full_account_min": 3.8,
    "benchmark_manual_min": 28,
    "zones_cleared": ["L1 Staging", "L9 Structure", "L12 MEP", "Curtain Wall"],
    "zones_pending": [],
}

GATE = {
    "avg_checkin_time_sec": 14,
    "manual_baseline_sec": 90,
    "peak_flow_per_hr": 312,
    "total_today": 284,
    "first_badge_time": "5:58 AM",
    "peak_hour": "7-8 AM",
}

CHANGE_ORDERS = pd.DataFrame([
    {"co": "CO-114", "trade": "MEP Electrical", "zone": "L14-16 Elec room",  "kwant_hrs": 186, "reported_hrs": 210, "variance": -24, "status": "Disputed"},
    {"co": "CO-118", "trade": "Concrete",       "zone": "L9 Pour deck",      "kwant_hrs": 312, "reported_hrs": 314, "variance":  -2, "status": "Approved"},
    {"co": "CO-121", "trade": "Curtain wall",   "zone": "L20-22 East face",  "kwant_hrs": 97,  "reported_hrs": 97,  "variance":   0, "status": "Approved"},
    {"co": "CO-125", "trade": "Steel",          "zone": "L18 Structural",    "kwant_hrs": 144, "reported_hrs": 171, "variance": -27, "status": "Disputed"},
    {"co": "CO-129", "trade": "MEP Mechanical", "zone": "L10-12 HVAC shaft", "kwant_hrs": 228, "reported_hrs": 229, "variance":  -1, "status": "Approved"},
])

WEEKLY_TREND = pd.DataFrame({
    "week":          ["Wk 27","Wk 28","Wk 29","Wk 30","Wk 31","Wk 32","Wk 33","Wk 34"],
    "actual":        [198, 214, 231, 248, 261, 275, 279, 284],
    "planned":       [220, 240, 255, 270, 285, 300, 305, 310],
    "fatigue_flags": [2,   3,   3,   4,   5,   6,   7,   7],
})

ALERTS = [
    {"severity": "critical", "icon": "🔴", "title": "Fatigue threshold — 3 workers from Stahl Electric at 9th consecutive day.", "time": "08:00 AM", "source": "Fatigue Mgmt"},
    {"severity": "warning",  "icon": "⚠️", "title": "Unauthorized zone entry — L18 mechanical shaft. Badge #A-2291.",           "time": "08:47 AM", "source": "ZoneIQ"},
    {"severity": "warning",  "icon": "⚠️", "title": "Near-miss logged — falling object, curtain wall L22. Area cleared.",       "time": "09:14 AM", "source": "Safety"},
    {"severity": "warning",  "icon": "⚠️", "title": "CO-114 hour variance flagged — 24hrs below reported. Kwant data sent to PM.", "time": "09:30 AM", "source": "Change Orders"},
    {"severity": "info",     "icon": "ℹ️", "title": "Electrical headcount 14 of 22. Root cause: fatigue flags + 2 no-shows.",   "time": "08:00 AM", "source": "WorkforceOS"},
    {"severity": "resolved", "icon": "✅", "title": "SOS resolved — Badge #B-0074 confirmed safe. False alarm.",                 "time": "07:32 AM", "source": "Safety"},
]

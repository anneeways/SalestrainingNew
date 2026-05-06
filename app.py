import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import json
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Joey's Business Case | HR loves Finance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Font Awesome ─────────────────────────────────────────────────────────────
# ─── Font Awesome — single lightweight CDN ───────────────────────────────────
st.markdown("""
<link rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
  crossorigin="anonymous"/>
""", unsafe_allow_html=True)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Segoe UI — system font */

/* ══ GLOBAL BUTTON OVERRIDE — only main content area ══ */
section[data-testid="stMain"] button,
section.main button,
div[data-testid="stVerticalBlock"] button,
div[data-testid="stHorizontalBlock"] button,
.stButton > button {
    background-color: #1E2A5E !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(30,42,94,0.2) !important;
}
section[data-testid="stMain"] button:hover { 
    opacity: 0.88 !important; 
    background-color: #253472 !important; 
}

html, body, [class*="css"] { font-family: 'Segoe UI', system-ui, sans-serif; }
.stApp { background-color: #E8E3D8; }

/* ── Mobile ── */
@media (max-width: 768px) {
    /* Hide progress stepper dots on mobile — nav buttons are enough */
    .progress-mobile-hide { display: none !important; }

    /* Compact nav buttons */
    .stButton > button {
        font-size: 0.72rem !important;
        padding: 0.35rem 0.3rem !important;
    }
    /* Smaller hero header */
    .main-hero { padding: 0.9rem 1rem !important; }
    .main-hero .hero-title { font-size: 1.3rem !important; }
    .main-hero .hero-creds { display: none !important; }

    /* Full-width dialogue boxes */
    .dialogue-box { padding: 0.8rem 0.9rem !important; }

    /* Stack columns on mobile */
    .scene-header { font-size: 1.4rem !important; }
}

/* ── Content Boxes ── */
.content-box {
    background: white;
    border-radius: 12px;
    border: 1.5px solid #D1CCBF;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 6px rgba(30,42,94,0.06);
}
.navy-box {
    background: #1E2A5E;
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1rem;
    color: #F5F0E6;
}
.navy-box h3 {
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #B8BCDE; font-size: 0.8rem;
    font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 0.6rem;
}
.navy-box p { font-size: 0.93rem; line-height: 1.75; opacity: 0.92; }

/* ── Progress ── */
.progress-label {
    font-size: 0.72rem; color: #9CA3AF;
    letter-spacing: 0.07em; text-transform: uppercase;
    font-weight: 600; margin-bottom: 0.8rem;
}
.progress-steps {
    display: flex; gap: 0.6rem; margin-bottom: 2.2rem; align-items: center;
}
.prog-item {
    display: flex; align-items: center; gap: 0.45rem; flex: 1;
}
.prog-dot {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; flex-shrink: 0; transition: all 0.2s;
}
.prog-dot-done    { background: #B8BCDE; color: #1E2A5E; }
.prog-dot-active  { background: #1E2A5E; color: #F5F0E6;
                    box-shadow: 0 0 0 3px rgba(30,42,94,0.15); }
.prog-dot-pending { background: #E5E1D8; color: #C4C0B8; }
.prog-line {
    flex: 1; height: 2px; border-radius: 1px;
}
.prog-line-done    { background: #B8BCDE; }
.prog-line-active  { background: linear-gradient(90deg, #B8BCDE 50%, #E5E1D8 50%); }
.prog-line-pending { background: #E5E1D8; }

/* ── Typography ── */
.scene-header {
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #1E2A5E; font-size: 1.9rem; margin-bottom: 0.25rem;
}
.scene-sub {
    color: #9CA3AF; font-size: 0.82rem; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 1.6rem;
    display: flex; align-items: center; gap: 0.4rem;
}

/* ── Dialogue ── */
.dialogue-box {
    background: white; border-radius: 12px;
    border: 1px solid #EAE7DF;
    padding: 1.2rem 1.5rem; margin-bottom: 0.9rem;
    box-shadow: 0 1px 4px rgba(30,42,94,0.05);
}
.speaker-row {
    display: flex; align-items: center; gap: 0.5rem;
    margin-bottom: 0.55rem;
}
.speaker-avatar {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; flex-shrink: 0;
}
.av-joey    { background: #1E2A5E; color: #F5F0E6; }
.av-vl      { background: #E5E1D8; color: #6B7280; }
.av-thought { background: #F3F4F6; color: #9CA3AF; }
.speaker-name {
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase;
}
.sn-joey    { color: #1E2A5E; }
.sn-vl      { color: #6B7280; }
.sn-thought { color: #9CA3AF; }
.dialogue-text   { color: #1E2A5E; font-size: 0.94rem; line-height: 1.75; }
.dialogue-thought { color: #6B7280; font-size: 0.9rem; line-height: 1.7; font-style: italic; }

/* ── Choice Cards ── */
.choice-title {
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #1E2A5E; font-size: 1.25rem; margin: 1.2rem 0 1.1rem;
}
.choice-card-navy {
    background: #1E2A5E; border-radius: 14px; padding: 1.7rem;
    color: #F5F0E6; margin-bottom: 0.8rem;
}
.choice-card-light {
    background: white; border: 1.5px solid #1E2A5E;
    border-radius: 14px; padding: 1.7rem; margin-bottom: 0.8rem;
}
.choice-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 1rem;
}
.ci-navy  { background: rgba(184,188,222,0.25); color: #B8BCDE; }
.ci-light { background: #F5F0E6; color: #1E2A5E; }
.choice-card-navy h3  {
    font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.15rem;
    color: #F5F0E6; margin-bottom: 0.5rem;
}
.choice-card-light h3 {
    font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.15rem;
    color: #1E2A5E; margin-bottom: 0.5rem;
}
.choice-card-navy p  { font-size: 0.87rem; color: #B8BCDE; line-height: 1.7; }
.choice-card-light p { font-size: 0.87rem; color: #6B7280; line-height: 1.7; }

/* ── Swifty Chat ── */
.swifty-header {
    display: flex; align-items: center; gap: 0.7rem; margin-bottom: 1.2rem;
}
.swifty-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: #D1FAE5; display: flex; align-items: center;
    justify-content: center; font-size: 1.1rem; color: #059669;
    flex-shrink: 0;
}
.swifty-label { font-size: 0.72rem; font-weight: 700; color: #059669;
                letter-spacing: 0.07em; text-transform: uppercase; }
.swifty-bubble {
    background: #1E2A5E; color: #F5F0E6;
    border-radius: 14px 14px 14px 4px;
    padding: 1rem 1.3rem; margin: 0.4rem 0;
    font-size: 0.93rem; line-height: 1.75; max-width: 82%;
}
.user-bubble {
    background: #B8BCDE; color: #1E2A5E;
    border-radius: 14px 14px 4px 14px;
    padding: 0.9rem 1.2rem; margin: 0.4rem 0 0.4rem auto;
    font-size: 0.93rem; line-height: 1.7;
    max-width: 82%; text-align: right;
}

/* ── Checklist ── */
.check-item {
    background: white; border-radius: 10px;
    border: 1px solid #EAE7DF;
    padding: 0.85rem 1.1rem; margin-bottom: 0.55rem;
    display: flex; gap: 0.75rem; align-items: flex-start;
}
.check-icon-wrap {
    width: 24px; height: 24px; border-radius: 50%;
    background: #D1FAE5; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0; margin-top: 0.1rem;
}
.check-icon-wrap i { font-size: 0.65rem; color: #059669; }

/* ── KPI Cards ── */
.kpi-grid { display: flex; gap: 0.9rem; margin: 1.3rem 0; flex-wrap: wrap; }
.kpi-card {
    background: #1E2A5E; border-radius: 12px;
    padding: 1.1rem 1.2rem; color: #F5F0E6;
    flex: 1; min-width: 120px;
}
.kpi-icon { font-size: 1rem; color: #B8BCDE; margin-bottom: 0.5rem; }
.kpi-label {
    font-size: 0.68rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: #B8BCDE; margin-bottom: 0.25rem;
}
.kpi-value {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 1.55rem; color: #F5F0E6; line-height: 1;
}
.kpi-sub { font-size: 0.68rem; color: #B8BCDE; margin-top: 0.2rem; }

/* ── Recommendation ── */
.rec-success {
    background: #D1FAE5; border-left: 4px solid #059669;
    border-radius: 10px; padding: 1.1rem 1.4rem;
    color: #065F46; margin: 1rem 0;
    display: flex; gap: 0.8rem; align-items: flex-start;
}
.rec-success i { font-size: 1.1rem; margin-top: 0.1rem; color: #059669; }
.rec-warn {
    background: #FEF3C7; border-left: 4px solid #D97706;
    border-radius: 10px; padding: 1.1rem 1.4rem;
    color: #92400E; margin: 1rem 0;
    display: flex; gap: 0.8rem; align-items: flex-start;
}
.rec-warn i { font-size: 1.1rem; margin-top: 0.1rem; color: #D97706; }

/* ── Argument Items ── */
.arg-item {
    background: white; border-radius: 10px;
    border: 1px solid #EAE7DF;
    padding: 0.9rem 1.1rem; margin-bottom: 0.55rem;
    display: flex; gap: 0.75rem; align-items: flex-start;
}
.arg-icon-wrap {
    width: 26px; height: 26px; border-radius: 50%;
    background: #EEF0F8; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0; margin-top: 0.1rem;
}
.arg-icon-wrap i { font-size: 0.65rem; color: #1E2A5E; }

/* ── Scenario Tile ── */
.scenario-tile {
    background: white; border-radius: 10px;
    border: 1px solid #EAE7DF;
    padding: 0.9rem 1.1rem; margin-bottom: 0.55rem;
}
.scenario-tile .s-badge {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 0.3rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.badge-cons   { color: #3B82F6; }
.badge-real   { color: #059669; }
.badge-opt    { color: #D97706; }

/* ── Calc Box ── */
.calc-detail {
    background: #F5F0E6; border-radius: 10px;
    padding: 1rem 1.3rem; font-size: 0.86rem;
    color: #1E2A5E; line-height: 2.1;
    border: 1px solid #E5E1D8;
}

/* ── Buttons ── */
.stButton > button,
button[data-testid="baseButton-secondary"],
button[data-testid="baseButton-primary"] {
    background: #1E2A5E !important; color: #F5F0E6 !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 0.9rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.82 !important; }

hr { border: none; border-top: 1px solid #EAE7DF; margin: 1.6rem 0; }
label { color: #1E2A5E !important; font-weight: 500; }

.footer {
    margin-top: 3rem; padding-top: 1rem;
    border-top: 1px solid #E5E1D8;
    text-align: center; color: #B0ABA0; font-size: 0.77rem;
    display: flex; align-items: center; justify-content: center; gap: 0.6rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
def init():
    for k, v in {
        "step": 1, "path": None, "max_steps": 7,
        "swifty_messages": [], "params": None, "results": None,
        "prep_notes": {}, "status_quo": {}, "recommendation": "Volltraining", "ai_summary": ""
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ─── Data ─────────────────────────────────────────────────────────────────────
@dataclass
class Params:
    participants: int = 10
    cost_per_person: float = 2500
    monthly_leads: int = 200
    current_rate: float = 15.0
    target_rate: float = 25.0
    deal_value: float = 15000
    margin_rate: float = 25.0
    training_days: int = 3
    daily_rate: float = 400.0
    pilot_mode: bool = False  # Train-the-Trainer: cost for N, revenue for full team

def calculate(p: Params):
    tc = p.participants * p.cost_per_person
    oc = p.participants * p.training_days * p.daily_rate
    total = tc + oc
    cd = p.monthly_leads * (p.current_rate / 100)
    td_full = p.monthly_leads * (p.target_rate / 100)

    if p.pilot_mode:
        # Phase 1 (Months 1-6): only pilot participants at target rate
        pilot_share = p.participants / 10  # fraction of team trained
        td_phase1 = (p.monthly_leads * pilot_share * (p.target_rate / 100) +
                     p.monthly_leads * (1 - pilot_share) * (p.current_rate / 100))
        ad_phase1 = td_phase1 - cd
        mm_phase1 = ad_phase1 * p.deal_value * (p.margin_rate / 100)

        # Phase 2 (Months 7-12): full team at target rate
        ad_phase2 = td_full - cd
        mm_phase2 = ad_phase2 * p.deal_value * (p.margin_rate / 100)

        am = mm_phase1 * 6 + mm_phase2 * 6  # blended annual margin
        ad = (ad_phase1 + ad_phase2) / 2     # avg for display
        mm = am / 12                          # avg monthly for payback
        td = td_phase1                        # display phase 1 target
    else:
        td = td_full
        ad = td - cd
        mr = ad * p.deal_value
        mm = mr * (p.margin_rate / 100)
        am = mm * 12

    mr = ad * p.deal_value
    net = am - total
    roi = (net / total) * 100 if total > 0 else 0
    pb = (total / mm) if mm > 0 else 0
    return dict(total=total, tc=tc, oc=oc, cd=cd, td=td, ad=ad,
                mr=mr, mm=mm, am=am, net=net, roi=roi, pb=pb,
                pilot_mode=p.pilot_mode,
                mm_phase1=mm_phase1 if p.pilot_mode else mm,
                mm_phase2=mm_phase2 if p.pilot_mode else mm)

def fmt(v): return f"{v:,.0f} €".replace(",", ".")


# ─── Swifty Agent ─────────────────────────────────────────────────────────────
SWIFTY_SYSTEM = """Du bist Swifty — ein motivierender, warmherziger Business-Case-Coach für HR-Professionals.

Deine Persönlichkeit:
- Enthusiastisch und ermutigend ("Genau der richtige Gedanke!", "Das ist eine starke Frage!")
- Du stellst immer nur EINE Frage pro Nachricht
- Du bist direkt aber nie belehrend
- Maximal 120 Wörter pro Antwort
- Sprich auf Deutsch, du-Form

Das Szenario: Joey (HR Business Partnerin) hat erfahren, dass das Sales-Team ein neues Training möchte (25.000 €, Budget überschritten). Sie muss CFO und CEO überzeugen.

Führe sie durch:
1. Warum jetzt? Welches konkrete Problem lösen wir?
2. Was passiert wenn wir NICHT investieren?
3. Welche Infos braucht Joey noch um rechnen zu können?
4. Welche Einwände könnte der CFO haben?
5. Wie kommuniziert sie Gewinn statt Umsatz?

Nach ca. 5-6 Austauschen: Fasse zusammen und beende mit: "Du bist bereit! Klick auf 'Weiter zum Follow-up' 🚀"
"""

def swifty_call(messages):
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return "⚠️ Kein API-Key konfiguriert. Bitte `ANTHROPIC_API_KEY` in den Streamlit Secrets hinterlegen."
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-opus-4-5", "max_tokens": 300,
                  "system": SWIFTY_SYSTEM, "messages": messages},
            timeout=30
        )
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"Verbindungsfehler: {e}"


# ─── Progress Bar ─────────────────────────────────────────────────────────────
STEP_META = [
    ("fa-comment-dots",       "Das Gespräch"),
    ("fa-arrow-right-arrow-left",    "Dein Weg"),
    ("fa-list-check",        "Vorbereitung"),
    ("fa-people-arrows",      "Follow-up"),
    ("fa-magnifying-glass-chart",    "Datensynthese"),
    ("fa-calculator",     "Kalkulator"),
    ("fa-award",     "Ergebnis"),
]


# ─── Logo (base64 embedded) ─────────────────────────────────────────────────
LOGO_B64 = "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"
# ─── Inline SVG Icons (no CDN needed) ────────────────────────────────────────
def svg_icon(name, size=18, color="currentColor"):
    """Return inline SVG for given icon name"""
    paths = {
        "chat":       "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
        "fork":       "M7 3a2 2 0 100 4 2 2 0 000-4zm10 0a2 2 0 100 4 2 2 0 000-4zM12 17a2 2 0 100 4 2 2 0 000-4zM7 7v2a2 2 0 002 2h6a2 2 0 002-2V7M12 11v6",
        "compass":    "M16.24 7.76l-1.804 5.411-5.41 1.804 1.804-5.411 5.41-1.804zM12 2a10 10 0 100 20A10 10 0 0012 2z",
        "handshake":  "M9 12l-4-4m0 0l4-4M5 8h7a4 4 0 014 4v1M15 17l4 4m0 0l-4 4m4-4H8a4 4 0 01-4-4v-1",
        "calculator": "M9 7H7v2h2V7zm0 4H7v2h2v-2zm0 4H7v2h2v-2zm4-8h-2v2h2V7zm0 4h-2v2h2v-2zm0 4h-2v6h2v-6zm4-8h-2v8h2V7zM5 3a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2H5z",
        "chart":      "M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z",
        "user":       "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z",
        "briefcase":  "M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zM16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2",
        "thought":    "M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
        "clock":      "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
        "location":   "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z",
        "robot":      "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h3M15 3h3a2 2 0 012 2v10a2 2 0 01-2 2h-2M12 12h.01M8 8h.01M16 8h.01",
        "pen":        "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
        "check":      "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
        "trending":   "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
        "money":      "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
        "fire":       "M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z",
        "shield":     "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
        "star":       "M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z",
        "hourglass":  "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
        "download":   "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4",
        "refresh":    "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
    }
    path = paths.get(name, paths["chat"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" 
         viewBox="0 0 24 24" fill="none" stroke="{color}" 
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="{path}"/>
    </svg>'''

STEP_ICONS = ["fa-comment-dots","fa-arrow-right-arrow-left","fa-list-check","fa-people-arrows","fa-magnifying-glass-chart","fa-calculator","fa-award"]



def render_progress(current):
    n = len(STEP_META)
    st.progress(current / n)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


def render_nav():
    """Simple text navigation — current step highlighted navy"""
    current = st.session_state.get("step", 1)
    labels = [s[1] for s in STEP_META]

    # CSS to style nav buttons
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        color: #9CA3AF !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        padding: 0.3rem 0.2rem !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid #1E2A5E !important;
        border-radius: 0 !important;
        color: #1E2A5E !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        padding: 0.3rem 0.2rem !important;
    }
    </style>""", unsafe_allow_html=True)

    cols = st.columns(len(labels))
    for i, (col, label) in enumerate(zip(cols, labels), 1):
        with col:
            is_cur = (i == current)
            if st.button(label, key=f"nav_{i}",
                         use_container_width=True,
                         type="primary" if is_cur else "secondary"):
                st.session_state.step = i
                st.rerun()
    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)


# ─── Dialogue Helper ──────────────────────────────────────────────────────────
def dialogue(speaker, text, kind="joey"):
    """kind: joey | vl | thought"""
    fa_map  = {"joey": "fa-user", "vl": "fa-briefcase", "thought": "fa-ellipsis"}
    av_cls  = {"joey": "av-joey", "vl": "av-vl",        "thought": "av-thought"}
    sn_cls  = {"joey": "sn-joey", "vl": "sn-vl",        "thought": "sn-thought"}
    fg_col  = {"joey": "#F5F0E6", "vl": "#6B7280",       "thought": "#9CA3AF"}
    txt_cls = "dialogue-thought" if kind == "thought" else "dialogue-text"
    fa  = fa_map.get(kind, "fa-user")
    av  = av_cls.get(kind, "av-joey")
    sn  = sn_cls.get(kind, "sn-joey")
    fg  = fg_col.get(kind, "#F5F0E6")
    return f"""
    <div class="dialogue-box">
        <div class="speaker-row">
            <div class="speaker-avatar {av}" style="font-size:0.75rem;">
                <i class="fa-solid {fa}" style="color:{fg};"></i>
            </div>
            <div class="speaker-name {sn}">{speaker}</div>
        </div>
        <div class="{txt_cls}">„{text}"</div>
    </div>"""


def step1():
    render_progress(1)
    render_nav()
    st.markdown('<div class="scene-header">Das Gespräch</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        🕐 Montagmorgen &nbsp;·&nbsp;
        📍 Flur vor dem Sales-Büro
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="dialogue-box" style="border-left: 3px solid #E5E1D8;">
        <div style="font-size:0.85rem; color:#9CA3AF; font-style:italic; line-height:1.7;">
            🎬
            Joey ist auf dem Weg zum Drucker, als sie Thomas, den Vertriebsleiter,
            mit dem Telefon am Ohr vorbeirennen sieht. Er winkt sie heran.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(dialogue("Thomas — Vertriebsleiter",
        "Joey, kurz — ich hab gerade eine Anfrage von Consilium Training. "
        "Die haben ein neues Sales-Programm, das ist wirklich stark. "
        "Drei Tage, die ganze Truppe durch. Der Anbieter sagt, andere Unternehmen "
        "haben ihre Abschlussquote damit von 15 auf 25 Prozent gesteigert.", "vl"),
        unsafe_allow_html=True)

    st.markdown(dialogue("Joey", "Klingt interessant. Was kostet das?", "joey"),
        unsafe_allow_html=True)

    st.markdown(dialogue("Thomas",
        "2.500 € pro Person. Wir wären zehn Leute — also 25.000 €. "
        "Ich weiß, das übersteigt unser genehmigtes Trainingsbudget. "
        "Aber ich glaube wirklich daran. Kannst du das irgendwie durchkriegen?", "vl"),
        unsafe_allow_html=True)

    st.markdown(dialogue("Joey — innerlich",
        "Okay. Thomas glaubt daran — das ist ein gutes Zeichen. Aber der CFO wird Zahlen sehen wollen. "
        "Echte Zahlen. Nicht Versprechen vom Anbieter. Ich muss das durchdenken, "
        "bevor ich irgendwo anklopfe.", "thought"),
        unsafe_allow_html=True)

    st.markdown(dialogue("Joey",
        "Ich schaue mir das an, Thomas. Gib mir bis Mittwoch.", "joey"),
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Weiter  →  Was macht Joey jetzt?"):
        st.session_state.step = 2
        st.rerun()


def step2():
    render_progress(2)
    render_nav()
    st.markdown('<div class="scene-header">Joeys nächster Schritt</div>', unsafe_allow_html=True)

    st.markdown(dialogue("Joey — innerlich",
        "Ich muss einen Business Case bauen. Aber wo fange ich an? "
        "Welche Fragen muss ich mir überhaupt stellen — bevor ich auch nur "
        "eine Zahl in den Rechner eingebe?", "thought"),
        unsafe_allow_html=True)

    st.markdown('<div class="choice-title">Wie willst du vorgehen?</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="choice-card-navy">
            <div class="choice-icon ci-navy">
                🤖
            </div>
            <h3>Ich brauche Swifty's Hilfe</h3>
            <p>Swifty führt dich durch die wichtigen Fragen,
            die du dir stellen musst — bevor du zum Kalkulator gehst.
            Schritt für Schritt, mit Coaching.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mit Swifty starten", key="btn_swifty"):
            st.session_state.path = "swifty"
            st.session_state.step = 3
            opening = (
                "Hey Joey — super, dass du dir die Zeit nimmst, das wirklich durchzudenken! 🎉\n\n"
                "Bevor wir zu den Zahlen kommen, lass uns bei der wichtigsten Frage beginnen — "
                "die viele überspringen:\n\n"
                "**Welches konkrete Problem hat das Sales-Team gerade?** "
                "Was steckt hinter der stagnierenden Abschlussquote?"
            )
            st.session_state.swifty_messages = [{"role": "assistant", "content": opening}]
            st.rerun()

    with col2:
        st.markdown("""
        <div class="choice-card-light">
            <div class="choice-icon ci-light">
                ✏️
            </div>
            <h3>Ich weiß schon was ich fragen will</h3>
            <p>Du kennst dein Handwerk. Überprüfe deine
            Vorbereitungs-Checkliste und geh direkt zum
            Follow-up-Gespräch mit Thomas.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Direkt zur Checkliste", key="btn_fast"):
            st.session_state.path = "fast"
            st.session_state.step = 3
            st.rerun()


def step3():
    render_progress(3)
    render_nav()

    if st.session_state.path == "swifty":
        st.markdown('<div class="scene-header">Vorbereitung mit Swifty</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="swifty-header">
            <div class="swifty-avatar">🤖</div>
            <div>
                <div class="swifty-label">Swifty · Business-Case-Coach</div>
                <div style="font-size:0.8rem; color:#6B7280;">Motivierender Coach · immer eine Frage</div>
            </div>
        </div>""", unsafe_allow_html=True)

        for msg in st.session_state.swifty_messages:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="swifty-bubble">{msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-bubble">{msg["content"]}</div>',
                            unsafe_allow_html=True)

        last = st.session_state.swifty_messages[-1]["content"] if st.session_state.swifty_messages else ""
        if "Du bist bereit" in last or "bereit!" in last:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Weiter zum Follow-up-Gespräch  →"):
                st.session_state.step = 4
                st.rerun()
        else:
            user_input = st.chat_input("Deine Antwort an Swifty …")
            if user_input:
                st.session_state.swifty_messages.append({"role": "user", "content": user_input})
                with st.spinner("Swifty denkt …"):
                    resp = swifty_call(st.session_state.swifty_messages)
                st.session_state.swifty_messages.append({"role": "assistant", "content": resp})
                st.rerun()

        col_skip, _ = st.columns([1, 5])
        with col_skip:
            if st.button("Zur Checkliste →"):
                st.session_state.path = "fast"
                st.rerun()

    else:
        st.markdown('<div class="scene-header">Deine Vorbereitungs-Checkliste</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.78rem;color:#059669;font-weight:700;letter-spacing:0.07em;
                    text-transform:uppercase;margin-bottom:0.8rem;">
            ✅ &nbsp;Was Joey klären muss — bevor sie rechnet
        </div>""", unsafe_allow_html=True)

        # Status Quo research hints
        st.markdown(
            "<div style='background:#F3F2EE;border-radius:10px;border-left:3px solid #B8BCDE;"
            "padding:0.9rem 1.1rem;margin-bottom:0.8rem;'>"
            "<div style='font-weight:700;color:#1E2A5E;font-size:0.88rem;margin-bottom:0.5rem;'>"
            "🔍 Status Quo recherchieren — bevor du Zahlen sammelst</div>"
            "<div style='font-size:0.83rem;color:#6B7280;line-height:1.8;'>"
            "📋 <strong>HR-Daten prüfen:</strong> Fluktuation im Sales-Team (12 Monate), "
            "Engagement Survey Ergebnisse, Abwesenheitsquote<br>"
            "🎯 <strong>Performance-Daten:</strong> Wer trifft Ziele — wer nicht? "
            "Seit wann stagniert die Quote? Gab es früher bessere Werte?<br>"
            "🏆 <strong>Wettbewerb:</strong> Was weiß Thomas über Konkurrenz-Quoten? "
            "Gibt es Branchenbenchmarks (z.B. 20-25% ist Branchendurchschnitt)?<br>"
            "👥 <strong>Teamdynamik:</strong> Letzte Mitarbeitergespräche, "
            "Feedbackrunden, bekannte Motivationsthemen"
            "</div></div>",
            unsafe_allow_html=True
        )

        # Finance tip
        st.markdown(
            "<div style='background:#EEF0F8;border-radius:10px;border-left:3px solid #1E2A5E;"
            "padding:0.9rem 1.1rem;margin-bottom:1.2rem;'>"
            "<div style='font-weight:700;color:#1E2A5E;font-size:0.88rem;margin-bottom:0.5rem;'>"
            "💼 Mit Finance abstimmen — vor dem Follow-up</div>"
            "<div style='font-size:0.83rem;color:#6B7280;line-height:1.8;'>"
            "📊 <strong>Marge & Deal-Wert verifizieren:</strong> Finance kann die tatsächliche "
            "Deckungsbeitragsmarge aus dem Controlling bestätigen — nicht nur eine Schätzung von Thomas.<br>"
            "📈 <strong>Pipeline-Daten:</strong> CRM-Auswertung mit Abschlussquoten pro Quartal — "
            "Finance oder Sales-Controlling hat diese Zahlen oft vorliegen.<br>"
            "💰 <strong>Trainingsbudget klären:</strong> Wie groß ist das genehmigte Budget, "
            "was fehlt, welche Genehmigungsstufe ist nötig?<br>"
            "🔒 <strong>Vorabgespräch CFO:</strong> Vor dem formalen Business Case lohnt ein kurzer "
            "informeller Check — 'Was braucht ihr, um das zu genehmigen?'"
            "</div></div>",
            unsafe_allow_html=True
        )

        # Part A: Can answer now
        items_now = [
            ("fa-circle-question", "Ist Training wirklich die richtige Antwort?",
             "Haben wir Führungsprobleme? Unklare Prozesse? Fehlt Motivation — oder echtes Skill-Gap? Training löst nur das letzte."),
            ("fa-users-gear", "Führung & Teamdynamik",
             "Wie führt Thomas sein Team? Gibt es Fluktuation, Demotivation, fehlende Erwartungsklarheit?"),
            ("fa-magnifying-glass-chart", "Was ist das eigentliche Problem?",
             "Fähigkeitslücke, Prozess, Markt — oder alles zusammen? Eigene Einschätzung vor dem Gespräch."),
            ("fa-award", "Marktdruck & Wettbewerb",
             "Was macht die Konkurrenz anders? Hat der Wettbewerb bessere Abschlussquoten?"),
            ("fa-circle-question", "Warum jetzt?",
             "Was verschärft die Dringlichkeit? Wettbewerbsdruck, Quartalsziele, Personalwechsel?"),
            ("fa-coins", "Gewinn statt Umsatz — meine Argumentation",
             "Nicht Mehrumsatz, sondern zusätzlicher Deckungsbeitrag ist das CFO-Argument."),
        ]

        # Part B: Need to find out from Thomas
        items_thomas = [
            ("fa-table-cells-large", "Zahlen die ich brauche",
             "Leads/Monat, Deal-Wert, Marge, Teilnehmerzahl, Ausfallkosten — alles für den Kalkulator."),
            ("fa-shield-check", "Warum wirkt das Training?",
             "Referenzkunden, vergleichbare Unternehmen — kein Anbieter-Versprechen, sondern Daten."),
            ("fa-user-group", "Pilot möglich? Top-Performer zuerst?",
             "Könnten wir mit 2-3 Top-Performern starten und ein Train-the-Trainer Konzept entwickeln?"),
            ("fa-comments", "CFO-Einwände antizipieren",
             "Welche Gegenargumente kommen? Antworten vorbereiten bevor das Meeting stattfindet."),
            ("fa-circle-exclamation", "Was passiert wenn wir nichts tun?",
             "Entgangener Gewinn pro Monat — den konkreten Preis des Abwartens benennen."),
        ]

        def render_checklist_section(section_items, section_key_prefix):
            col_h1, col_h2 = st.columns(2, gap="medium")
            with col_h1:
                st.markdown(
                    "<div style='background:#1E2A5E;color:#B8BCDE;border-radius:8px;"
                    "padding:0.5rem 1rem;font-size:0.75rem;font-weight:700;"
                    "letter-spacing:0.06em;text-transform:uppercase;'>Frage / Überlegung</div>",
                    unsafe_allow_html=True
                )
            with col_h2:
                st.markdown(
                    "<div style='background:#1E2A5E;color:#B8BCDE;border-radius:8px;"
                    "padding:0.5rem 1rem;font-size:0.75rem;font-weight:700;"
                    "letter-spacing:0.06em;text-transform:uppercase;'>✏️ Deine Erkenntnis</div>",
                    unsafe_allow_html=True
                )
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            for item_icon, title, detail in section_items:
                note_key = f"{section_key_prefix}_{title[:20].replace(' ','_')}"
                col_q, col_a = st.columns(2, gap="medium")
                with col_q:
                    st.markdown(
                        f"<div style='background:white;border-radius:10px;"
                        f"border:1.5px solid #D1CCBF;padding:0.85rem 1rem;"
                        f"box-shadow:0 1px 4px rgba(0,0,0,0.05);'>"
                        f"<div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;'>"
                        f"<div style='width:26px;height:26px;min-width:26px;border-radius:50%;"
                        f"background:#D1FAE5;display:flex;align-items:center;justify-content:center;'>"
                        f"<i class='fa-solid {item_icon}' style='font-size:0.65rem;color:#059669;'></i>"
                        f"</div>"
                        f"<span style='font-size:0.9rem;font-weight:700;color:#1E2A5E;'>{title}</span>"
                        f"</div>"
                        f"<div style='font-size:0.81rem;color:#9CA3AF;line-height:1.5;"
                        f"padding-left:32px;'>{detail}</div></div>",
                        unsafe_allow_html=True
                    )
                with col_a:
                    val = st.text_area(
                        label=title, key=note_key,
                        placeholder="Was ist deine Einschätzung?",
                        height=95, label_visibility="collapsed"
                    )
                    st.session_state.prep_notes[title] = val
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Section A
        st.markdown(
            "<div style='background:#1E2A5E;border-radius:10px;padding:0.6rem 1rem;"
            "margin-bottom:0.7rem;'><span style='color:#F5F0E6;font-weight:700;"
            "font-size:0.88rem;'>💡 Das kann ich jetzt schon beantworten</span>"
            "<span style='color:#B8BCDE;font-size:0.8rem;'> — vor dem Gespräch mit Thomas</span></div>",
            unsafe_allow_html=True
        )
        render_checklist_section(items_now, "now")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Section B
        st.markdown(
            "<div style='background:#B8BCDE;border-radius:10px;padding:0.6rem 1rem;"
            "margin-bottom:0.7rem;'><span style='color:#1E2A5E;font-weight:700;"
            "font-size:0.88rem;'>🤝 Das muss ich noch herausfinden</span>"
            "<span style='color:#1E2A5E;font-size:0.8rem;opacity:0.7;'> — im Follow-up mit Thomas</span></div>",
            unsafe_allow_html=True
        )
        render_checklist_section(items_thomas, "thomas")

        for item_icon, title, detail in []:  # dummy to keep indent
            pass  # handled by render_checklist_section

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🤝  Weiter zum Follow-up-Gespräch →"):
            st.session_state.step = 4
            st.rerun()


def step4():
    render_progress(4)
    render_nav()
    st.markdown('<div class="scene-header">Das Follow-up</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        🕐 Mittwoch · 10:15 Uhr &nbsp;·&nbsp;
        📍 Joeys Büro
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F3F2EE;border-radius:10px;border-left:3px solid #B8BCDE;
                padding:1rem 1.3rem;margin-bottom:0.5rem;">
        <span style="font-size:0.85rem;color:#9CA3AF;font-style:italic;line-height:1.7;">
            🎬 &nbsp;Joey hat Thomas zu sich gebeten. Vor ihr liegt ihre ausgefüllte Checkliste —
            die gesammelten Informationen aus der Vorbereitung und die offenen Fragen,
            die sie noch klären muss. Sie startet nicht mit Zahlen, sondern mit den Menschen.
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#EEF0F8;border-radius:8px;padding:0.6rem 1rem;
                margin-bottom:1rem;font-size:0.8rem;color:#6B7280;
                border:1px dashed #B8BCDE;">
        💡 <em>Dieses Gespräch ist <strong>beispielhaft</strong> und zeigt eine mögliche Gesprächsführung.
        In der Praxis wird jedes Follow-up anders verlaufen — je nach Unternehmen, Team und Kontext.
        Erweiterbar mit eigenen Fragen aus der Checkliste.</em>
    </div>""", unsafe_allow_html=True)

    exchanges = [
        # 1. Einstieg
        ("joey", "Joey",
         "Thomas, ich freue mich dass wir uns Zeit nehmen. Bevor wir über das Training reden — "
         "ich möchte zuerst ein paar grundlegendere Fragen stellen. Nicht als Kritik, "
         "aber ich muss sicher sein dass wir das richtige Problem lösen."),
        ("vl", "Thomas", "Klar — frag alles was du brauchst."),

        # 2. People first
        ("joey", "Joey",
         "Wie lange stagniert die Abschlussquote schon bei 15%? War das mal besser — und wenn ja, was hat sich verändert?"),
        ("vl", "Thomas",
         "Vor zwei Jahren lagen wir noch bei 20%. Seitdem drei Neuzugänge im Team, "
         "der Markt ist wettbewerbsintensiver geworden."),
        ("joey", "Joey",
         "Wie hoch war eure Fluktuation im Sales-Team in den letzten 12 Monaten?"),
        ("vl", "Thomas",
         "Zwei Leute haben uns verlassen — einer davon war ein Top-Performer. Das hat uns zurückgeworfen."),
        ("joey", "Joey",
         "Habt ihr zuletzt eine Mitarbeiterbefragung oder Feedback-Gespräche geführt? "
         "Wie ist die Stimmung — und weiß das Team klar was von ihnen erwartet wird?"),
        ("vl", "Thomas",
         "Letztes Jahr gab es eine kurze Umfrage. Engagement war okay, aber Erwartungsklarheit "
         "wurde als Verbesserungsfeld genannt. Ich bin ehrlich gesagt oft selbst im Kundenkontakt."),
        ("joey", "Joey",
         "Gibt es Leute im Team die konstant ihre Ziele verfehlen — unabhängig von Methodik oder Markt?"),
        ("vl", "Thomas",
         "Ja, zwei machen mir wirklich Sorgen. Aber drei andere haben echtes Potenzial — "
         "die könnten noch viel mehr."),
        ("thought", "Joey — innerlich",
         "Führungsdefizite, ein verlorener Top-Performer, Erwartungsunklarheit — "
         "das ist kein reines Training-Problem. Ich muss das im Business Case benennen."),

        # 3. Jetzt die Zahlen
        ("joey", "Joey",
         "Danke Thomas — das hilft mir sehr. Jetzt brauche ich die Zahlen für den Business Case. "
         "Wie viele Leads habt ihr aktuell pro Monat?"),
        ("vl", "Thomas", "Ungefähr 200. Manchmal mehr, selten weniger."),
        ("joey", "Joey", "Durchschnittlicher Deal-Wert?"),
        ("vl", "Thomas", "15.000 €. Das ist realistisch."),
        ("joey", "Joey", "Marge pro Deal — nach Kosten?"),
        ("vl", "Thomas", "Etwa 25%."),
        ("joey", "Joey",
         "Woher weiß ich, dass 25% Abschlussquote erreichbar ist — und nicht nur ein Anbieterversprechen?"),
        ("vl", "Thomas",
         "Zwei Referenzkunden — beide haben nach dem Training zwischen 22 und 28% erreicht. "
         "Ich kann dir die Kontakte geben."),

        # 4. Pilot-Idee
        ("joey", "Joey",
         "Letzte Überlegung: Was wäre wenn wir zunächst nur 2-3 Top-Performer schicken — als Pilot? "
         "Geringeres Risiko, und wenn es wirkt bauen wir ein Train-the-Trainer Konzept."),
        ("vl", "Thomas",
         "Das gefällt mir. Kostet weniger und die drei sind hoch motiviert. "
         "Wenn es läuft, ziehen wir alle nach."),
        ("thought", "Joey — innerlich",
         "Gut. Ich habe jetzt das vollständige Bild: Führungsthemen parallel adressieren, "
         "zwei Szenarien für den Business Case — Volltraining oder Pilot. Beides rechne ich durch."),
    ]

    for kind, speaker, text in exchanges:
        st.markdown(dialogue(speaker, text, kind), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Weiter zum Kalkulator  →"):
        st.session_state.step = 5
        st.rerun()


# ─── AI Summary Generator ─────────────────────────────────────────────────────
def generate_ai_summary(notes: dict, status_quo: dict, results: dict) -> str:
    """Generate board summary suggestions from checklist notes"""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return "⚠️ Kein API-Key konfiguriert."

        notes_text = "\n".join([f"- {k}: {v}" for k, v in notes.items() if v])
        sq_text = "\n".join([f"- {k}: {v}" for k, v in status_quo.items() if v])
        res_text = f"""
- Gesamtinvestition: {results.get("total", 0):,.0f} €
- Jahresgewinn: {results.get("am", 0):,.0f} €
- ROI: {results.get("roi", 0):.0f}%
- Payback: {results.get("pb", 0):.1f} Monate
""" if results else ""

        prompt = f"""Du bist ein erfahrener CFO-Berater und hilfst einer HR Business Partnerin dabei,
einen Business Case für den Vorstand vorzubereiten.

Basierend auf den folgenden gesammelten Informationen, erstelle eine strukturierte Zusammenfassung
mit konkreten Vorschlägen für die Vorstandspräsentation.

STATUS QUO:
{sq_text}

ERKENNTNISSE AUS DER ANALYSE:
{notes_text}

FINANZKENNZAHLEN:
{res_text}

Erstelle eine Zusammenfassung mit folgender Struktur:
1. KERNAUSSAGE (1-2 Sätze — das wichtigste Argument)
2. AUSGANGSLAGE (3-4 Punkte — was steht auf dem Spiel)
3. EMPFEHLUNG (klar und entscheidungsreif)
4. FINANZIELLE BEGRÜNDUNG (die wichtigsten Zahlen)
5. RISIKEN & MASSNAHMEN (was noch zu klären ist)
6. NÄCHSTE SCHRITTE (konkret, mit Zeitrahmen)

Schreibe präzise, direkt und auf CFO-Niveau. Deutsch. Maximal 350 Wörter."""

        import requests
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-opus-4-5", "max_tokens": 600,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"Fehler: {e}"


# ─── Charts ───────────────────────────────────────────────────────────────────
def make_charts(r):
    navy, lav, cream = "#1E2A5E", "#B8BCDE", "#F5F0E6"
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Investition vs. Jahresgewinn", "Break-even Verlauf"),
        horizontal_spacing=0.12
    )
    fig.add_trace(go.Bar(
        x=["💸 Investition", "📈 Jahresgewinn"],
        y=[r["total"], r["am"]],
        marker_color=[lav, navy],
        text=[fmt(r["total"]), fmt(r["am"])],
        textposition="auto",
        textfont=dict(color=[navy, cream]),
    ), row=1, col=1)

    months = list(range(13))
    cum = [-r["total"]]
    for _ in range(12):
        cum.append(cum[-1] + r["mm"])

    fig.add_trace(go.Scatter(
        x=months, y=cum, mode="lines+markers",
        line=dict(color=navy, width=3),
        marker=dict(color=navy, size=7),
        fill="tozeroy", fillcolor="rgba(30,42,94,0.08)",
    ), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="#DC2626",
                  annotation_text=f"  Break-even: Monat {r['pb']:.1f}",
                  annotation_font_color="#DC2626", row=1, col=2)

    fig.update_layout(
        height=300, showlegend=False,
        plot_bgcolor=cream, paper_bgcolor=cream,
        font=dict(family="Segoe UI, system-ui, sans-serif", color=navy),
        margin=dict(t=40, b=10, l=10, r=10)
    )
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", linecolor="#E5E7EB")
    return fig


def step5():
    render_progress(5)
    render_nav()
    st.markdown('<div class="scene-header">Datensynthese</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        🧩 Alle gesammelten Erkenntnisse — Grundlage für den Business Case
    </div>""", unsafe_allow_html=True)

    notes = {k: v for k, v in st.session_state.get("prep_notes", {}).items() if v and v.strip()}

    # ── Status Quo Zusammenfassung (editierbar) ──────────────────────────────
    st.markdown(
        "<div style='background:#1E2A5E;border-radius:10px;padding:0.7rem 1.1rem;"
        "margin-bottom:0.8rem;'><span style='color:#F5F0E6;font-weight:700;"
        "font-size:0.9rem;'>📊 Status Quo — Deine Zahlen eintragen</span>"
        "<span style='color:#B8BCDE;font-size:0.78rem;'> &nbsp;·&nbsp; anpassbar für euer Unternehmen</span></div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        sq_quote = st.text_input("⚠️ Aktuelle Abschlussquote", 
            value=st.session_state.status_quo.get("quote", "15% — stagnierend seit Q3"),
            key="sq_quote")
        sq_leads = st.text_input("📥 Leads pro Monat",
            value=st.session_state.status_quo.get("leads", "~200"),
            key="sq_leads")
        sq_marge = st.text_input("📊 Marge pro Deal",
            value=st.session_state.status_quo.get("marge", "25%"),
            key="sq_marge")
    with col2:
        sq_team = st.text_input("👥 Teamgröße",
            value=st.session_state.status_quo.get("team", "10 Personen im Sales-Team"),
            key="sq_team")
        sq_deal = st.text_input("💰 Ø Deal-Wert",
            value=st.session_state.status_quo.get("deal", "15.000 €"),
            key="sq_deal")
        sq_wettb = st.text_input("🏆 Wettbewerb / Benchmark",
            value=st.session_state.status_quo.get("wettb", "Hat Training bereits durchgeführt — 22-28% Quote erreicht"),
            key="sq_wettb")

    # Zusätzliches Freitextfeld
    sq_kontext = st.text_area("📝 Weiterer Kontext (Fluktuation, Teamdynamik, Marktlage ...)",
        value=st.session_state.status_quo.get("kontext", ""),
        placeholder="z.B. Fluktuation 18% letztes Jahr, zwei Underperformer im Team, Marktdruck durch neuen Wettbewerber...",
        height=80, key="sq_kontext")

    # Save to session state
    st.session_state.status_quo = {
        "quote": sq_quote, "leads": sq_leads, "marge": sq_marge,
        "team": sq_team, "deal": sq_deal, "wettb": sq_wettb, "kontext": sq_kontext
    }

    # ── Offene Fragen / Risiken ───────────────────────────────────────────────
    st.markdown(
        "<div style='background:#FEF3C7;border-left:4px solid #D97706;border-radius:10px;"
        "padding:0.9rem 1.1rem;margin:0.8rem 0;'>"
        "<div style='font-weight:700;color:#92400E;margin-bottom:0.4rem;'>⚠️ Offene Fragen — noch zu klären</div>"
        "<div style='font-size:0.87rem;color:#92400E;line-height:1.8;'>"
        "• Zwei Teammitglieder verfehlen Ziele dauerhaft — Führungsgespräch nötig<br>"
        "• Feedbackroutinen und Erwartungsklarheit könnten gestärkt werden<br>"
        "• Pilot (Top-Performer) vs. Volltraining — Entscheidung steht noch aus<br>"
        "• Train-the-Trainer Konzept als Phase 2 zu definieren"
        "</div></div>",
        unsafe_allow_html=True
    )

    # ── Erkenntnisse aus Vorbereitung ─────────────────────────────────────────
    st.markdown(
        "<div style='background:#1E2A5E;border-radius:10px;padding:0.7rem 1.1rem;"
        "margin:0.8rem 0;'><span style='color:#F5F0E6;font-weight:700;"
        "font-size:0.9rem;'>✏️ Deine Erkenntnisse aus der Vorbereitung</span></div>",
        unsafe_allow_html=True
    )
    if notes:
        for q, a in notes.items():
            col_q, col_a = st.columns([1, 1], gap="medium")
            with col_q:
                st.markdown(
                    f"<div style='background:#EEF0F8;border-radius:8px;"
                    f"padding:0.6rem 0.85rem;font-size:0.84rem;"
                    f"font-weight:600;color:#1E2A5E;'>{q}</div>",
                    unsafe_allow_html=True
                )
            with col_a:
                st.markdown(
                    f"<div style='background:white;border-radius:8px;"
                    f"border:1.5px solid #D1CCBF;padding:0.6rem 0.85rem;"
                    f"font-size:0.84rem;color:#374151;'>{a}</div>",
                    unsafe_allow_html=True
                )
            st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)
    else:
        st.info("💡 Keine Notizen aus Schritt 3 — fülle die Checkliste aus für eine vollständigere Analyse.")

    # ── Empfehlungs-Vorschlag (wählbar) ──────────────────────────────────────
    st.markdown(
        "<div style='background:#1E2A5E;border-radius:10px;padding:0.7rem 1.1rem;"
        "margin:0.8rem 0;'><span style='color:#F5F0E6;font-weight:700;"
        "font-size:0.9rem;'>🎯 Empfehlungs-Richtung wählen</span>"
        "<span style='color:#B8BCDE;font-size:0.78rem;'>"
        " &nbsp;·&nbsp; Deine Einschätzung vor der Berechnung</span></div>",
        unsafe_allow_html=True
    )

    options = {
        "🎓 Volltraining": {
            "sub": "10 Personen, 25.000 €  ·  Maximaler Impact sofort",
            "border": "#059669", "bg": "#F0FDF4"
        },
        "🚀 Pilot + Train-the-Trainer": {
            "sub": "3 Top-Performer, ~7.500 €  ·  Geringeres Risiko, nachhaltig",
            "border": "#3B82F6", "bg": "#EFF6FF"
        },
        "⏸️ Nicht jetzt": {
            "sub": "Führungsthemen zuerst adressieren",
            "border": "#9CA3AF", "bg": "#F9FAFB"
        },
    }

    cols = st.columns(3, gap="medium")
    for i, (opt_label, opt_data) in enumerate(options.items()):
        with cols[i]:
            is_sel = (st.session_state.recommendation == opt_label)
            bg = opt_data["bg"] if is_sel else "white"
            border_w = "3px" if is_sel else "1.5px"
            st.markdown(
                f"<div style='background:{bg};border-radius:10px;"
                f"border:{border_w} solid {opt_data['border']};"
                f"padding:1.1rem;text-align:center;min-height:110px;'>"
                f"<div style='font-weight:700;color:#1E2A5E;font-size:0.9rem;"
                f"margin-bottom:0.4rem;'>{opt_label}</div>"
                f"<div style='font-size:0.78rem;color:#6B7280;line-height:1.5;'>"
                f"{opt_data['sub']}</div>"
                f"{'<div style="margin-top:0.5rem;font-size:0.7rem;font-weight:700;color:' + opt_data['border'] + '">✓ Ausgewählt</div>' if is_sel else ''}"
                f"</div>",
                unsafe_allow_html=True
            )
            if st.button(f"Wählen", key=f"rec_{i}", use_container_width=True):
                st.session_state.recommendation = opt_label
                st.rerun()

    # Show selected recommendation
    sel = st.session_state.recommendation
    if sel:
        st.markdown(
            f"<div style='background:#EEF0F8;border-radius:8px;padding:0.6rem 1rem;"
            f"margin-top:0.5rem;font-size:0.85rem;color:#1E2A5E;'>"
            f"<strong>Deine Wahl:</strong> {sel} — "
            f"wird in den Kalkulator und das Executive Summary übernommen.</div>",
            unsafe_allow_html=True
        )

    # ── AI Zusammenfassung ────────────────────────────────────────────────────
    st.markdown(
        "<div style='background:#1E2A5E;border-radius:10px;padding:0.7rem 1.1rem;"
        "margin:1rem 0 0.6rem;'><span style='color:#F5F0E6;font-weight:700;"
        "font-size:0.9rem;'>🤖 Vorstandszusammenfassung generieren</span>"
        "<span style='color:#B8BCDE;font-size:0.78rem;'>"
        " &nbsp;·&nbsp; KI erstellt Vorschläge aus deinen Erkenntnissen</span></div>",
        unsafe_allow_html=True
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        generate = st.button("✨ Zusammenfassung erstellen", use_container_width=True)
    with col_info:
        st.markdown(
            "<div style='font-size:0.82rem;color:#6B7280;padding-top:0.5rem;'>"
            "Nutzt deine Checklisten-Notizen, Status Quo Daten und Finanzkennzahlen "
            "um Vorschläge für die Vorstandspräsentation zu generieren.</div>",
            unsafe_allow_html=True
        )

    if generate or st.session_state.get("ai_summary"):
        if generate:
            notes = {k: v for k, v in st.session_state.get("prep_notes", {}).items() if v and v.strip()}
            sq = st.session_state.get("status_quo", {})
            res = st.session_state.get("results", {})
            with st.spinner("Swifty denkt …"):
                summary = generate_ai_summary(notes, sq, res)
            st.session_state.ai_summary = summary

        if st.session_state.get("ai_summary"):
            st.markdown("**📋 Vorschlag — editierbar:**")
            edited = st.text_area(
                label="Vorstandszusammenfassung",
                value=st.session_state.ai_summary,
                height=320,
                label_visibility="collapsed",
                key="ai_summary_edit"
            )
            st.session_state.ai_summary = edited

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧮  Weiter zum Kalkulator →"):
        st.session_state.step = 6
        st.rerun()


def step6():
    render_progress(6)
    render_nav()
    st.markdown('<div class="scene-header">Der Kalkulator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        🧮 Joey rechnet — mit den Zahlen aus dem Gespräch
    </div>""", unsafe_allow_html=True)

    # Data summary before calculator
    notes = {k: v for k, v in st.session_state.get("prep_notes", {}).items() if v and v.strip()}
    if notes:
        with st.expander("📋 Gesammelte Erkenntnisse — alle Daten auf einen Blick", expanded=False):
            st.markdown(
                "<div style='background:#1E2A5E;border-radius:8px;padding:0.6rem 1rem;"
                "margin-bottom:0.8rem;color:#B8BCDE;font-size:0.78rem;font-weight:700;"
                "letter-spacing:0.06em;text-transform:uppercase;'>"
                "Aus Checkliste + Follow-up-Gespräch</div>",
                unsafe_allow_html=True
            )
            for q, a in notes.items():
                col_q, col_a = st.columns([1, 1], gap="medium")
                with col_q:
                    st.markdown(
                        f"<div style='background:#EEF0F8;border-radius:8px;"
                        f"padding:0.5rem 0.8rem;font-size:0.84rem;"
                        f"font-weight:600;color:#1E2A5E;'>{q}</div>",
                        unsafe_allow_html=True
                    )
                with col_a:
                    st.markdown(
                        f"<div style='background:white;border-radius:8px;"
                        f"border:1px solid #E5E1D8;padding:0.5rem 0.8rem;"
                        f"font-size:0.84rem;color:#374151;'>{a}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)

            # Pilot scenario notice
            st.markdown(
                "<div style='background:#D1FAE5;border-radius:8px;border-left:3px solid #059669;"
                "padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.85rem;color:#065F46;'>"
                "<strong>💡 Zwei Szenarien verfügbar:</strong> Volltraining (10 Personen) "
                "oder Pilot mit Top-Performern (2-3 Personen) als Train-the-Trainer Ansatz. "
                "Beide Optionen unten im Kalkulator vergleichen.</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("💡 Tipp: Fülle die Checkliste in Schritt 3 aus — dann siehst du hier alle gesammelten Erkenntnisse.")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F3F2EE;border-radius:10px;border-left:3px solid #B8BCDE;
                padding:1rem 1.3rem;margin-bottom:1rem;">
        <span style="font-size:0.88rem;color:#6B7280;font-style:italic;line-height:1.7;">
            💭 &nbsp;<strong>Joey — innerlich:</strong>
            „Die Zahlen sind da. Jetzt muss ich aus Umsatz Gewinn machen —
            das ist was den CFO interessiert. Nicht was wir verkaufen könnten,
            sondern was wirklich in der Kasse landet."
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Connect recommendation from step 5
    rec = st.session_state.get("recommendation", "🎓 Volltraining")
    is_pilot = "Pilot" in rec
    is_skip  = "jetzt" in rec

    if is_skip:
        st.warning("⏸️ Du hast in der Datensynthese 'Nicht jetzt' gewählt. "
                   "Du kannst trotzdem rechnen — z.B. um zu zeigen was das Abwarten kostet.")

    # Scenario indicator
    st.markdown(
        f"<div style='background:{'#EFF6FF' if is_pilot else '#F0FDF4'};"
        f"border-radius:8px;border-left:4px solid {'#3B82F6' if is_pilot else '#059669'};"
        f"padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.87rem;color:#1E2A5E;'>"
        f"<strong>Szenario aus Datensynthese:</strong> {rec} — "
        f"{'Teilnehmerzahl auf 3 voreingestellt' if is_pilot else 'Teilnehmerzahl auf 10 voreingestellt'}"
        f"</div>",
        unsafe_allow_html=True
    )

    default_p = 3 if is_pilot else 10
    lp = st.session_state.get("loaded_params", {})

    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        st.markdown("**🎓&nbsp; Das Training**", unsafe_allow_html=True)
        participants  = st.number_input("Teilnehmer", 1, 50, lp.get("participants", default_p))
        cost_pp       = st.number_input("Kosten pro Person (€)", 500, 20000, lp.get("cost_per_person", 2500), 100)
        t_days        = st.number_input("Trainingstage", 1, 10, lp.get("training_days", 3))
        daily_rate    = st.number_input("Tagessatz Ausfall/MA (€)", 100, 2000, lp.get("daily_rate", 400), 50)

    with col_r:
        st.markdown("**📊&nbsp; Sales-Metriken — aus dem Gespräch**",
                    unsafe_allow_html=True)
        leads         = st.number_input("Leads pro Monat", 10, 1000, lp.get("monthly_leads", 200), 10)
        curr_rate     = st.slider("Abschlussquote aktuell (%)", 1.0, 50.0, float(lp.get("current_rate", 15.0)), 0.5)
        tgt_rate      = st.slider("Abschlussquote Ziel (%)", 1.0, 50.0, float(lp.get("target_rate", 25.0)), 0.5)
        deal_val      = st.number_input("Ø Deal-Wert (€)", 1000, 500000, lp.get("deal_value", 15000), 500)
        margin        = st.slider("Marge pro Deal (%)", 5.0, 80.0, float(lp.get("margin_rate", 25.0)), 1.0)

    is_pilot_mode = "Pilot" in st.session_state.get("recommendation", "")
    p = Params(participants, cost_pp, leads, curr_rate, tgt_rate, deal_val, margin,
               t_days, daily_rate, pilot_mode=is_pilot_mode)
    r = calculate(p)
    st.session_state.params = p
    st.session_state.results = r

    st.markdown("<hr>", unsafe_allow_html=True)

    kpis = [
        ("fa-sack-dollar",  "Gesamtinvestition", fmt(r["total"]),     "Training + Ausfallzeit"),
        ("fa-chart-simple",   "Zusatzgewinn/Mo.",  fmt(r["mm"]),         f"+{r['ad']:.1f} Deals × {margin}%"),
        ("fa-sack-dollar",      "Jahresgewinn",      fmt(r["am"]),         "nach 12 Monaten"),
        ("fa-percent",          "ROI",               f"{r['roi']:.0f}%",   fmt(r["net"]) + " Nettogewinn"),
        ("fa-rotate-left",   "Payback",           f"{r['pb']:.1f} Mon.", "bis Break-even"),
    ]

    # Pilot mode explanation
    if p.pilot_mode:
        mm1 = r.get("mm_phase1", r["mm"])
        mm2 = r.get("mm_phase2", r["mm"])
        st.markdown(
            "<div style='background:#EFF6FF;border-left:4px solid #3B82F6;border-radius:8px;"
            "padding:0.9rem 1.1rem;margin-bottom:0.8rem;font-size:0.87rem;color:#1E2A5E;'>"
            "<strong>🚀 Train-the-Trainer — Phasenmodell:</strong><br>"
            f"<strong>Phase 1 (Monat 1–6):</strong> Nur {participants} Top-Performer trainiert "
            f"→ Zusatzgewinn <strong>{fmt(mm1)}/Monat</strong><br>"
            f"<strong>Phase 2 (Monat 7–12):</strong> Internes Training, gesamtes Team auf {tgt_rate}% "
            f"→ Zusatzgewinn <strong>{fmt(mm2)}/Monat</strong><br>"
            f"<strong>Jahresgewinn gesamt (gewichtet): {fmt(r['am'])}</strong>"
            "</div>",
            unsafe_allow_html=True
        )

    kpi_html = '<div class="kpi-grid">'
    for kpi_icon, label, value, sub in kpis:
        kpi_html += f"""
        <div class="kpi-card">
            <div class="kpi-icon"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>"""
    kpi_html += "</div>"
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.plotly_chart(make_charts(r), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Weiter zur Argumentation  →"):
        st.session_state.step = 7
        st.rerun()


# ─── PDF Generator ────────────────────────────────────────────────────────────
def generate_pdf(r, p):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm)

    NAVY   = colors.HexColor("#1E2A5E")
    LAV    = colors.HexColor("#B8BCDE")
    CREAM  = colors.HexColor("#F5F0E6")
    GRAY   = colors.HexColor("#6B7280")
    GREEN  = colors.HexColor("#059669")
    WHITE  = colors.white

    def sty(name, **kw):
        base = ParagraphStyle(name, **kw)
        return base

    s_header   = sty("header",   fontSize=22, textColor=NAVY,  leading=28, fontName="Helvetica-Bold")
    s_sub      = sty("sub",      fontSize=8,  textColor=GRAY,  leading=12, fontName="Helvetica", spaceAfter=6)
    s_section  = sty("section",  fontSize=11, textColor=NAVY,  leading=16, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    s_body     = sty("body",     fontSize=9,  textColor=NAVY,  leading=14, fontName="Helvetica")
    s_bodygray = sty("bodygray", fontSize=8,  textColor=GRAY,  leading=12, fontName="Helvetica")
    s_kpi_val  = sty("kpival",   fontSize=18, textColor=WHITE, leading=22, fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_kpi_lbl  = sty("kpilbl",   fontSize=7,  textColor=LAV,   leading=10, fontName="Helvetica",      alignment=TA_CENTER)
    s_footer   = sty("footer",   fontSize=7,  textColor=GRAY,  leading=10, fontName="Helvetica",      alignment=TA_CENTER)
    s_arg_ttl  = sty("argttl",   fontSize=9,  textColor=NAVY,  leading=13, fontName="Helvetica-Bold")
    s_arg_body = sty("argbody",  fontSize=8,  textColor=GRAY,  leading=12, fontName="Helvetica")

    story = []

    # ── Header ──
    story.append(Paragraph("HR loves Finance", s_header))
    story.append(Paragraph(
        f"Joey's Business Case &nbsp;·&nbsp; Sales Training ROI &nbsp;·&nbsp; {datetime.now().strftime('%d.%m.%Y')}",
        s_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=10))

    # ── KPI Table ──
    story.append(Paragraph("Kern-Ergebnisse", s_section))

    kpi_data = [
        [Paragraph("GESAMTINVESTITION", s_kpi_lbl),
         Paragraph("ZUSATZGEWINN/MONAT", s_kpi_lbl),
         Paragraph("JAHRESGEWINN", s_kpi_lbl),
         Paragraph("ROI", s_kpi_lbl),
         Paragraph("PAYBACK", s_kpi_lbl)],
        [Paragraph(fmt(r["total"]),  s_kpi_val),
         Paragraph(fmt(r["mm"]),     s_kpi_val),
         Paragraph(fmt(r["am"]),     s_kpi_val),
         Paragraph(f"{r['roi']:.0f}%", s_kpi_val),
         Paragraph(f"{r['pb']:.1f} Mon.", s_kpi_val)],
    ]
    kpi_table = Table(kpi_data, colWidths=[34*mm]*5)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), NAVY),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [NAVY, NAVY]),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING",(0,0), (-1,-1), 3),
        ("INNERGRID",   (0,0), (-1,-1), 0.5, colors.HexColor("#2E3D6E")),
        ("BOX",         (0,0), (-1,-1), 0,   NAVY),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 8))

    # ── Calculation ──
    story.append(Paragraph("Kalkulation im Detail", s_section))
    calc_data = [
        ["Parameter", "Berechnung", "Ergebnis"],
        ["Trainingskosten",
         f"{p.participants} Teilnehmer x {fmt(p.cost_per_person)}",
         fmt(r["tc"])],
        ["Ausfallkosten",
         f"{p.participants} x {p.training_days} Tage x {p.daily_rate:.0f} EUR",
         fmt(r["oc"])],
        ["Gesamtinvestition", "", fmt(r["total"])],
        ["Zusaetzliche Deals/Monat",
         f"{p.monthly_leads} Leads x ({p.target_rate}% - {p.current_rate}%)",
         f"{r['ad']:.1f} Deals"],
        ["Mehrumsatz/Monat",
         f"{r['ad']:.1f} Deals x {fmt(p.deal_value)}",
         fmt(r["mr"])],
        ["Zusatzgewinn/Monat",
         f"{fmt(r['mr'])} x {p.margin_rate}%",
         fmt(r["mm"])],
        ["Jahresgewinn", "x 12 Monate", fmt(r["am"])],
        ["ROI",
         f"({fmt(r['net'])} / {fmt(r['total'])}) x 100",
         f"{r['roi']:.0f}%"],
        ["Payback",
         f"{fmt(r['total'])} / {fmt(r['mm'])}",
         f"{r['pb']:.1f} Monate"],
    ]
    styled_calc = []
    for row in calc_data:
        styled_calc.append([
            Paragraph(str(row[0]), s_body),
            Paragraph(str(row[1]), s_bodygray),
            Paragraph(str(row[2]), s_body),
        ])

    calc_table = Table(styled_calc, colWidths=[50*mm, 80*mm, 40*mm])
    calc_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  LAV),
        ("TEXTCOLOR",    (0,0), (-1,0),  NAVY),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, colors.HexColor("#F9F8F5")]),
        ("BACKGROUND",   (0,3), (-1,3),  colors.HexColor("#EEF0F8")),
        ("BACKGROUND",   (0,7), (-1,7),  colors.HexColor("#EEF0F8")),
        ("FONTNAME",     (2,3), (2,3),   "Helvetica-Bold"),
        ("FONTNAME",     (2,7), (2,7),   "Helvetica-Bold"),
        ("FONTNAME",     (2,8), (2,8),   "Helvetica-Bold"),
        ("FONTNAME",     (2,9), (2,9),   "Helvetica-Bold"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#E5E1D8")),
        ("BOX",          (0,0), (-1,-1), 1,   LAV),
    ]))
    story.append(calc_table)
    story.append(Spacer(1, 8))

    # ── Arguments ──
    story.append(Paragraph("Top-Argumente fuer CFO und CEO", s_section))
    args = [
        ("Gewinn, nicht Umsatz",
         f"Das Training generiert {fmt(r['am'])} zusaetzlichen Jahresgewinn — echter Deckungsbeitrag."),
        ("Schnelle Amortisation",
         f"Payback in {r['pb']:.1f} Monaten — schneller als jede Software-Einfuehrung."),
        ("Opportunitaetskosten des Abwartens",
         f"Jeder Monat ohne Training kostet {fmt(r['mm'])} entgangenen Gewinn."),
        ("Begrenzter Downside",
         f"Selbst bei nur 20% Abschlussquote bleibt der ROI positiv."),
        ("Referenzen statt Versprechen",
         "Zwei Kunden des Anbieters haben 22-28% erreicht — Marktdaten, kein Pitch."),
    ]
    arg_data = []
    for title, text in args:
        arg_data.append([
            Paragraph(title, s_arg_ttl),
            Paragraph(text, s_arg_body)
        ])
    arg_table = Table(arg_data, colWidths=[50*mm, 120*mm])
    arg_table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, colors.HexColor("#F9F8F5")]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#E5E1D8")),
        ("BOX",           (0,0), (-1,-1), 1,   LAV),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(arg_table)
    story.append(Spacer(1, 8))

    # ── Scenarios ──
    story.append(Paragraph("Szenarien im Vergleich", s_section))
    cons_ad = p.monthly_leads * 0.20 - (p.monthly_leads * p.current_rate / 100)
    cons_am = cons_ad * p.deal_value * (p.margin_rate / 100) * 12
    cons_roi = ((cons_am - r["total"]) / r["total"]) * 100

    sc_data = [
        [Paragraph("Szenario", s_body), Paragraph("Abschlussquote", s_body),
         Paragraph("Jahresgewinn", s_body), Paragraph("ROI", s_body)],
        [Paragraph("Konservativ", s_body), Paragraph("20%", s_bodygray),
         Paragraph(fmt(cons_am), s_body), Paragraph(f"{cons_roi:.0f}%", s_body)],
        [Paragraph("Realistisch", s_body), Paragraph(f"{p.target_rate}%", s_bodygray),
         Paragraph(fmt(r["am"]), s_body), Paragraph(f"{r['roi']:.0f}%", s_body)],
        [Paragraph("Optimistisch", s_body), Paragraph("+25% ueber Ziel", s_bodygray),
         Paragraph(fmt(r["am"]*1.25), s_body),
         Paragraph(f"{((r['am']*1.25 - r['total'])/r['total']*100):.0f}%", s_body)],
    ]
    sc_table = Table(sc_data, colWidths=[40*mm, 40*mm, 55*mm, 35*mm])
    sc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  LAV),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, colors.HexColor("#F9F8F5")]),
        ("BACKGROUND",    (0,2), (-1,2),  colors.HexColor("#D1FAE5")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#E5E1D8")),
        ("BOX",           (0,0), (-1,-1), 1,   LAV),
    ]))
    story.append(sc_table)

    # ── Footer ──
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LAV, spaceAfter=6))
    story.append(Paragraph(
        "HR loves Finance  ·  Anne Schuster Consulting  ·  anneschuster.com  ·  CIMA Fellow (FCMA, CGMA)",
        s_footer))

    doc.build(story)
    buf.seek(0)
    return buf.read()



def step7():
    render_progress(7)
    render_nav()
    r = st.session_state.results
    p = st.session_state.params

    if not r or not p:
        st.warning("Bitte zuerst den Kalkulator ausfüllen.")
        if st.button("← Zurück"):
            st.session_state.step = 6
            st.rerun()
        return

    st.markdown('<div class="scene-header">Joeys Business Case</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        📊 Bereit für CFO &amp; CEO
    </div>""", unsafe_allow_html=True)

    if r["roi"] > 80 and r["pb"] < 6:
        st.markdown(f"""
        <div class="rec-success">
            ✅
            <div>
                <strong>Starker Business Case — Investition klar empfehlenswert.</strong><br>
                ROI von <strong>{r['roi']:.0f}%</strong> &nbsp;·&nbsp;
                Payback in <strong>{r['pb']:.1f} Monaten</strong> &nbsp;·&nbsp;
                Jahresgewinn <strong>{fmt(r['am'])}</strong>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="rec-warn">
            ⚠️
            <div>
                <strong>Positiver Business Case — Argumentation schärfen.</strong><br>
                ROI von <strong>{r['roi']:.0f}%</strong> &nbsp;·&nbsp;
                Prüfe Annahmen zur Marge und Conversion.
            </div>
        </div>""", unsafe_allow_html=True)

    # Show checklist reflections
    notes = {k: v for k, v in st.session_state.get("prep_notes", {}).items() if v and v.strip()}
    if notes:
        with st.expander("📋 Deine Erkenntnisse — Grundlage des Business Case", expanded=True):
            for q, a in notes.items():
                col_q, col_a = st.columns([1, 1], gap="medium")
                with col_q:
                    st.markdown(
                        f"<div style='background:#EEF0F8;border-radius:8px;"
                        f"padding:0.6rem 0.85rem;font-size:0.85rem;"
                        f"font-weight:600;color:#1E2A5E;'>{q}</div>",
                        unsafe_allow_html=True
                    )
                with col_a:
                    st.markdown(
                        f"<div style='background:white;border-radius:8px;"
                        f"border:1.5px solid #D1CCBF;padding:0.6rem 0.85rem;"
                        f"font-size:0.85rem;color:#374151;'>{a}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)
    else:
        st.info("💡 Fülle die Checkliste in Schritt 3 aus — deine Erkenntnisse erscheinen dann hier im Business Case.")

    st.markdown("""
    <div style='background:#FEF3C7;border-left:4px solid #D97706;border-radius:10px;
                padding:1rem 1.4rem;margin:0.8rem 0;'>
        <div style='font-weight:700;color:#92400E;margin-bottom:0.4rem;'>
            ⚠️ Noch offen — parallel klären
        </div>
        <div style='font-size:0.88rem;color:#92400E;line-height:1.7;'>
            Thomas hat zwei Teammitglieder die ihre Ziele dauerhaft verfehlen.
            Führungsstrukturen und Feedback-Routinen könnten gestärkt werden.
            <strong>Empfehlung:</strong> Training genehmigen — aber gleichzeitig
            ein Führungsgespräch mit Thomas ansetzen und Teamzusammensetzung prüfen.
            Das Training ist notwendig, aber nicht hinreichend.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("**👩‍🏫&nbsp; Schlagkräftige Argumente**",
                    unsafe_allow_html=True)
        args = [
            ("fa-sack-dollar",      "Gewinn, nicht Umsatz",
             f"Das Training generiert {fmt(r['am'])} zusätzlichen Jahresgewinn — "
             "kein Umsatzversprechen, sondern echter Deckungsbeitrag."),
            ("fa-rotate-left","Schnelle Amortisation",
             f"Die Investition zahlt sich in {r['pb']:.1f} Monaten zurück — "
             "schneller als jede Software-Einführung."),
            ("fa-bolt",             "Opportunitätskosten des Abwartens",
             f"Jeder Monat ohne Training kostet {fmt(r['mm'])} entgangenen Gewinn. "
             "Nichts-Tun ist nicht kostenlos."),
            ("fa-umbrella",           "Begrenzter Downside",
             f"Selbst bei nur 20% Abschlussquote bleibt der ROI positiv. "
             "Das Risiko ist asymmetrisch."),
            ("fa-certificate",             "Referenzen statt Versprechen",
             "Zwei Kunden des Anbieters haben 22–28% erreicht. "
             "Das sind Marktdaten, kein Anbieter-Pitch."),
        ]
        for arg_icon, title, text in args:
            col_i, col_t = st.columns([0.06, 0.94])
            with col_i:
                st.markdown(
                    f"<div style='width:28px;height:28px;border-radius:50%;"
                    f"background:#EEF0F8;display:flex;align-items:center;"
                    f"justify-content:center;margin-top:3px;'>"
                    f"<i class='fa-solid {arg_icon}' style='font-size:0.69rem;color:#1E2A5E;'></i>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col_t:
                st.markdown(f"**{title}**")
                st.caption(text)

    with col2:
        st.markdown("**⚙️&nbsp; Szenarien im Vergleich**",
                    unsafe_allow_html=True)

        cons_ad = p.monthly_leads * 0.20 - (p.monthly_leads * p.current_rate / 100)
        cons_am = cons_ad * p.deal_value * (p.margin_rate / 100) * 12
        cons_roi = ((cons_am - r["total"]) / r["total"]) * 100

        scenarios = [
            ("fa-circle", "badge-cons", "KONSERVATIV", "20% Abschlussquote",
             fmt(cons_am), f"{cons_roi:.0f}%"),
            ("fa-circle", "badge-real", "REALISTISCH", f"{p.target_rate}% Abschlussquote",
             fmt(r["am"]), f"{r['roi']:.0f}%"),
            ("fa-circle", "badge-opt",  "OPTIMISTISCH", "+25% über Ziel",
             fmt(r["am"] * 1.25), f"{((r['am']*1.25 - r['total'])/r['total']*100):.0f}%"),
        ]
        badge_colors = {"badge-cons": "#3B82F6", "badge-real": "#059669", "badge-opt": "#D97706"}
        for sc_icon, badge, label, sublabel, jahresgewinn, roi_v in scenarios:
            color = badge_colors.get(badge, "#1E2A5E")
            st.markdown(
                f"<div style='background:white;border-radius:10px;border:1px solid #EAE7DF;"
                f"padding:0.9rem 1.1rem;margin-bottom:0.5rem;'>"
                f"<div style='font-size:0.7rem;font-weight:700;letter-spacing:0.06em;"
                f"color:{color};text-transform:uppercase;margin-bottom:0.3rem;'>"
                f"{label} <span style='color:#9CA3AF;font-weight:400;text-transform:none;'>— {sublabel}</span></div>"
                f"<div style='font-size:0.87rem;color:#6B7280;'>"
                f"Jahresgewinn: <strong style='color:#1E2A5E;'>{jahresgewinn}</strong>"
                f" &nbsp;·&nbsp; ROI: <strong style='color:#1E2A5E;'>{roi_v}</strong></div>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔍&nbsp; Die Kalkulation**",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="calc-detail">
            ·
            Trainingskosten: {p.participants} × {fmt(p.cost_per_person)} = <strong>{fmt(r['tc'])}</strong><br>
            ·
            Ausfallkosten: {p.participants} × {p.training_days}d × {p.daily_rate}€ = <strong>{fmt(r['oc'])}</strong><br>
            ·
            <strong>Gesamtinvestition: {fmt(r['total'])}</strong><br><br>
            ·
            Zusätzliche Deals: {r['ad']:.1f}/Mo. × {fmt(p.deal_value)} × {p.margin_rate}%<br>
            ·
            <strong>= {fmt(r['mm'])}/Monat → {fmt(r['am'])}/Jahr</strong>
        </div>""", unsafe_allow_html=True)

    # Export + Restart
    st.markdown("<hr>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        pdf_bytes = generate_pdf(r, p)
        st.download_button(
            "⬇ PDF herunterladen",
            data=pdf_bytes,
            file_name=f"joey_business_case_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    with c2:
        if st.button("Von vorne starten"):
            for k in ["step","path","swifty_messages","params","results"]:
                st.session_state.pop(k, None)
            st.rerun()


# ─── Save / Load ──────────────────────────────────────────────────────────────
def build_save_data():
    """Collect all session data into one dict"""
    r = st.session_state.get("results")
    p = st.session_state.get("params")
    return {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "tool": "HR loves Finance — Joey Business Case",
        "status_quo": st.session_state.get("status_quo", {}),
        "prep_notes": st.session_state.get("prep_notes", {}),
        "params": {
            "participants":    getattr(p, "participants",    10)  if p else 10,
            "cost_per_person": getattr(p, "cost_per_person", 2500) if p else 2500,
            "monthly_leads":   getattr(p, "monthly_leads",  200)  if p else 200,
            "current_rate":    getattr(p, "current_rate",   15.0) if p else 15.0,
            "target_rate":     getattr(p, "target_rate",    25.0) if p else 25.0,
            "deal_value":      getattr(p, "deal_value",     15000) if p else 15000,
            "margin_rate":     getattr(p, "margin_rate",    25.0) if p else 25.0,
            "training_days":   getattr(p, "training_days",  3)    if p else 3,
            "daily_rate":      getattr(p, "daily_rate",     400)  if p else 400,
        } if p else {},
        "results": r if not r else {k: round(v, 2) if isinstance(v, float) else v
                                     for k, v in r.items()},
    }

def load_save_data(data: dict):
    """Restore session state from saved dict"""
    if "status_quo" in data:
        st.session_state.status_quo = data["status_quo"]
    if "prep_notes" in data:
        st.session_state.prep_notes = data["prep_notes"]
    if "params" in data and data["params"]:
        p_data = data["params"]
        st.session_state.loaded_params = p_data  # Store for kalkulator pre-fill
    st.success("✅ Daten erfolgreich geladen! Gehe zum Kalkulator um die Werte zu sehen.")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div style="display:flex; align-items:baseline; gap:0.9rem; margin-bottom:0.2rem;">
        <div class="scene-header" style="margin:0; font-size:2rem;">HR loves Finance</div>
        <div style="color:#B8BCDE; font-size:0.75rem; letter-spacing:0.1em;
                    text-transform:uppercase; font-weight:600;">
            Workshop Tool
        </div>
    </div>
    <div style="color:#B0ABA0; font-size:0.8rem; margin-bottom:2.2rem;
                display:flex; align-items:center; gap:0.5rem;">
        🏢
        Anne Schuster Consulting &nbsp;·&nbsp;
        🌐
        anneschuster.com
    </div>
    """, unsafe_allow_html=True)

    step = st.session_state.step
    if   step == 1: step1()
    elif step == 2: step2()
    elif step == 3: step3()
    elif step == 4: step4()
    elif step == 5: step5()
    elif step == 6: step6()
    elif step == 7: step7()

    st.markdown("""
    <div class="footer">
        ♥
        HR loves Finance &nbsp;·&nbsp; Anne Schuster Consulting &nbsp;·&nbsp; anneschuster.com
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

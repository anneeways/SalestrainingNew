import streamlit as st
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
# ─── Load Font Awesome via multiple fallback methods ─────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/css/all.min.css');
</style>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
""", unsafe_allow_html=True)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Segoe UI — system font */

html, body, [class*="css"] { font-family: 'Segoe UI', system-ui, sans-serif; }
.stApp { background-color: #F5F0E6; }

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
        "step": 1, "path": None,
        "swifty_messages": [], "params": None, "results": None
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

def calculate(p: Params):
    tc = p.participants * p.cost_per_person
    oc = p.participants * p.training_days * p.daily_rate
    total = tc + oc
    cd = p.monthly_leads * (p.current_rate / 100)
    td = p.monthly_leads * (p.target_rate / 100)
    ad = td - cd
    mr = ad * p.deal_value
    mm = mr * (p.margin_rate / 100)
    am = mm * 12
    net = am - total
    roi = (net / total) * 100 if total > 0 else 0
    pb = (total / mm) if mm > 0 else 0
    return dict(total=total, tc=tc, oc=oc, cd=cd, td=td, ad=ad,
                mr=mr, mm=mm, am=am, net=net, roi=roi, pb=pb)

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
    ("fa-comments",    "Das Gespräch"),
    ("fa-code-branch", "Dein Weg"),
    ("fa-compass",     "Vorbereitung"),
    ("fa-handshake",   "Follow-up"),
    ("fa-calculator",  "Kalkulator"),
    ("fa-chart-line",  "Ergebnis"),
]

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

STEP_ICONS = ["fa-comments","fa-code-branch","fa-compass","fa-handshake","fa-calculator","fa-chart-line"]



def render_progress(current):
    n = len(STEP_META)
    names = [s[1] for s in STEP_META]

    # Step label
    st.markdown(
        f"<p style='font-size:0.72rem;color:#9CA3AF;letter-spacing:0.07em;text-transform:uppercase;font-weight:600;margin-bottom:0.5rem;'><i class='fa-solid fa-location-dot'></i>&nbsp;Schritt {current} von {n} — {names[current-1]}</p>",
        unsafe_allow_html=True
    )

    # Progress bar
    st.progress(current / n)

    # Step dots — one column per step
    cols = st.columns(n)
    for i, (_, name) in enumerate(STEP_META, 1):
        step_icon_name = STEP_ICONS[i-1]
        if i < current:
            bg, fg, opacity, lcolor = "#B8BCDE", "#1E2A5E", "1", "#9CA3AF"
        elif i == current:
            bg, fg, opacity, lcolor = "#1E2A5E", "#F5F0E6", "1", "#1E2A5E"
        else:
            bg, fg, opacity, lcolor = "#E5E1D8", "#C4C0B8", "0.5", "#C4C0B8"

        shadow = "box-shadow:0 0 0 3px rgba(30,42,94,0.15);" if i == current else ""
        fw = "700" if i == current else "400"

        with cols[i-1]:
            fa_icon = STEP_META[i-1][0]
            st.markdown(
                f"<div style='text-align:center;opacity:{opacity};'>"
                f"<div style='width:34px;height:34px;border-radius:50%;"
                f"background:{bg};{shadow}display:flex;align-items:center;"
                f"justify-content:center;margin:0 auto 4px;font-size:0.85rem;color:{fg};'>"
                f"<i class='fa-solid {fa_icon}'></i>"
                f"</div>"
                f"<div style='font-size:0.6rem;color:{lcolor};font-weight:{fw};"
                f"white-space:nowrap;'>{name}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)
# ─── Speaker Helper ───────────────────────────────────────────────────────────
def dialogue(speaker, text, kind="joey"):
    """kind: joey | vl | thought"""
    fa_map = {"joey": "fa-user", "vl": "fa-briefcase", "thought": "fa-ellipsis"}
    av_cls = {"joey": "av-joey", "vl": "av-vl", "thought": "av-thought"}
    sn_cls = {"joey": "sn-joey", "vl": "sn-vl", "thought": "sn-thought"}
    txt_cls = "dialogue-thought" if kind == "thought" else "dialogue-text"
    icon = icons.get(kind, "fa-user")
    av   = av_cls.get(kind, "av-joey")
    sn   = sn_cls.get(kind, "sn-joey")
    return f"""
    <div class="dialogue-box">
        <div class="speaker-row">
            <div class="speaker-avatar {av}"></div>
            <div class="speaker-name {sn}">{speaker}</div>
        </div>
        <div class="{txt_cls}">„{text}"</div>
    </div>"""


# ─── Charts ───────────────────────────────────────────────────────────────────
def make_charts(r):
    navy, lav, cream = "#1E2A5E", "#B8BCDE", "#F5F0E6"
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Investition vs. Jahresgewinn", "Break-even Verlauf"),
        horizontal_spacing=0.12
    )
    fig.add_trace(go.Bar(
        x=["Investition", "Jahresgewinn"],
        y=[r["total"], r["am"]],
        marker_color=[lav, navy],
        text=[fmt(r["total"]), fmt(r["am"])],
        textposition="auto",
        textfont=dict(color=[navy, cream]),
    ), row=1, col=1)

    months = list(range(13))
    cum = [-r["total"]]
    for _ in range(12): cum.append(cum[-1] + r["mm"])

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
        height=310, showlegend=False,
        plot_bgcolor=cream, paper_bgcolor=cream,
        font=dict(family="Segoe UI, system-ui, sans-serif", color=navy),
        margin=dict(t=45, b=10, l=10, r=10)
    )
    fig.update_xaxes(showgrid=False, linecolor="#EAE7DF")
    fig.update_yaxes(showgrid=True, gridcolor="#EAE7DF", linecolor="#EAE7DF")
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# STEPS
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Navigation ───────────────────────────────────────────────────────────────
def render_nav():
    """Jump-to navigation between steps"""
    current = st.session_state.get("step", 1)
    nav_meta = [
        ("fa-comments",    "Gespräch"),
        ("fa-code-branch", "Dein Weg"),
        ("fa-compass",     "Vorbereitung"),
        ("fa-handshake",   "Follow-up"),
        ("fa-calculator",  "Kalkulator"),
        ("fa-chart-line",  "Ergebnis"),
    ]
    # Render nav as HTML with FA icons
    nav_html = "<div style='display:flex;gap:0.4rem;margin-bottom:1rem;'>"
    for i, (fa, label) in enumerate(nav_meta, 1):
        is_cur = (i == st.session_state.get("step", 1))
        bg  = "#1E2A5E" if is_cur else "white"
        col = "white"  if is_cur else "#1E2A5E"
        bdr = "none"   if is_cur else "1.5px solid #1E2A5E"
        nav_html += (
            f"<div style='flex:1;background:{bg};color:{col};border:{bdr};"
            f"border-radius:8px;padding:0.4rem 0.3rem;text-align:center;"
            f"font-size:0.75rem;font-weight:600;cursor:pointer;'>"
            f"<i class='fa-solid {fa}'></i><br>"
            f"<span style='font-size:0.6rem;'>{label}</span></div>"
        )
    nav_html += "</div>"
    st.markdown(nav_html, unsafe_allow_html=True)

    # Hidden Streamlit buttons for actual click handling
    cols = st.columns(6)
    for i, (col, (fa, label)) in enumerate(zip(cols, nav_meta), 1):
        with col:
            if st.button(label, key=f"nav_jump_{i}", use_container_width=True,
                         help=f"Zu: {label}"):
                st.session_state.step = i
                st.rerun()


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
            if st.button("Überspringen →"):
                st.session_state.step = 4
                st.rerun()

    else:
        st.markdown('<div class="scene-header">Deine Vorbereitungs-Checkliste</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="scene-sub">
            ✅
            Was Joey klären muss — bevor sie rechnet
        </div>""", unsafe_allow_html=True)

        items = [
            ("fa-circle-question", "Warum jetzt?",
             "Das Sales-Team stagniert seit Q3 bei 15%. Thomas hat konkrete Marktdaten."),
            ("fa-triangle-exclamation", "Was passiert bei Nicht-Investition?",
             "Entgangener Gewinn jeden Monat — der Status quo ist nicht kostenlos."),
            ("fa-table-list", "Welche Zahlen brauche ich?",
             "Leads/Monat, Deal-Wert, Marge pro Abschluss, Teilnehmerzahl, Ausfallkosten."),
            ("fa-shield-halved", "Warum glaube ich, dass das Training wirkt?",
             "Anbieter-Referenzen, vergleichbare Unternehmen — kein Versprechen, Daten."),
            ("fa-comments-dollar", "Welche Einwände wird der CFO haben?",
             "'Woher wissen wir, dass die Quote wirklich steigt?' — Antwort vorbereiten."),
            ("fa-coins", "Gewinn statt Umsatz kommunizieren",
             "Nicht Mehrumsatz, sondern zusätzlicher Deckungsbeitrag ist das Argument."),
            ("fa-down-left-and-up-right-to-center", "Konservatives Szenario vorbereiten",
             "Was wenn's nur 20% statt 25% werden? Ist der Business Case noch positiv?"),
        ]

        for icon, title, detail in items:
            st.markdown(f"""
            <div class="check-item">
                <div class="check-icon-wrap">
                    
                </div>
                <div>
                    <strong style="color:#1E2A5E;">{title}</strong><br>
                    <span style="color:#6B7280; font-size:0.87rem;">{detail}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Weiter zum Follow-up-Gespräch  →"):
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
    <div class="dialogue-box" style="border-left: 3px solid #E5E1D8;">
        <div style="font-size:0.85rem; color:#9CA3AF; font-style:italic; line-height:1.7;">
            🎬
            Joey hat Thomas zu sich gebeten. Sie hat einen Notizblock vor sich —
            keine Zahlen, nur Fragen. Genau so, wie es sein sollte.
        </div>
    </div>""", unsafe_allow_html=True)

    exchanges = [
        ("joey", "Joey",
         "Thomas, bevor ich das intern weitertrage, brauche ich ein paar Zahlen von dir. "
         "Ich will sichergehen, dass wir das wirklich durchgerechnet haben — "
         "nicht nur das Versprechen des Anbieters."),
        ("vl", "Thomas", "Klar, frag mich alles."),
        ("joey", "Joey", "Wie viele Leads habt ihr aktuell pro Monat?"),
        ("vl", "Thomas", "Ungefähr 200. Manchmal mehr, selten weniger."),
        ("joey", "Joey", "Und der durchschnittliche Deal-Wert — wenn ein Lead abschließt?"),
        ("vl", "Thomas", "15.000 €. Kann variieren, aber das ist ein realistischer Durchschnitt."),
        ("joey", "Joey", "Was ist eure Marge auf so einen Deal?"),
        ("vl", "Thomas", "Etwa 25%. Nach Kosten, versteht sich."),
        ("joey", "Joey", "Und ihr seid aktuell wirklich bei 15% Abschlussquote?"),
        ("vl", "Thomas", "Leider ja. War mal besser. Deshalb brauchen wir das Training."),
        ("joey", "Joey",
         "Letzte Frage: Woher weiß ich, dass 25% realistisch ist — und kein Anbieterversprechen?"),
        ("vl", "Thomas",
         "Wir haben zwei Referenzkunden bekommen. Beide haben nach dem Training zwischen 22 und 28% "
         "erreicht. Ich kann dir die Kontakte geben."),
        ("thought", "Joey — innerlich",
         "Gut. Ich hab alles was ich brauche. Jetzt rechne ich."),
    ]

    for kind, speaker, text in exchanges:
        st.markdown(dialogue(speaker, text, kind), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Weiter zum Kalkulator  →"):
        st.session_state.step = 5
        st.rerun()


def step5():
    render_progress(5)
    render_nav()
    st.markdown('<div class="scene-header">Der Kalkulator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="scene-sub">
        🧮
        Joey rechnet — mit den Zahlen aus dem Gespräch
    </div>""", unsafe_allow_html=True)

    st.markdown(dialogue("Joey — innerlich",
        "Die Zahlen sind da. Jetzt muss ich aus Umsatz Gewinn machen — "
        "das ist was den CFO interessiert. Nicht was wir verkaufen könnten, "
        "sondern was wirklich in der Kasse landet.", "thought"),
        unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        st.markdown("**🎓&nbsp; Das Training**",
                    unsafe_allow_html=True)
        participants  = st.number_input("Teilnehmer", 1, 50, 10)
        cost_pp       = st.number_input("Kosten pro Person (€)", 500, 20000, 2500, 100)
        t_days        = st.number_input("Trainingstage", 1, 10, 3)
        daily_rate    = st.number_input("Tagessatz Ausfall/MA (€)", 100, 2000, 400, 50)

    with col_r:
        st.markdown("**📊&nbsp; Sales-Metriken — aus dem Gespräch**",
                    unsafe_allow_html=True)
        leads         = st.number_input("Leads pro Monat", 10, 1000, 200, 10)
        curr_rate     = st.slider("Abschlussquote aktuell (%)", 1.0, 50.0, 15.0, 0.5)
        tgt_rate      = st.slider("Abschlussquote Ziel (%)", 1.0, 50.0, 25.0, 0.5)
        deal_val      = st.number_input("Ø Deal-Wert (€)", 1000, 500000, 15000, 500)
        margin        = st.slider("Marge pro Deal (%)", 5.0, 80.0, 25.0, 1.0)

    p = Params(participants, cost_pp, leads, curr_rate, tgt_rate, deal_val, margin, t_days, daily_rate)
    r = calculate(p)
    st.session_state.params = p
    st.session_state.results = r

    st.markdown("<hr>", unsafe_allow_html=True)

    kpis = [
        ("fa-money-bill-wave",  "Gesamtinvestition", fmt(r["total"]),     "Training + Ausfallzeit"),
        ("fa-arrow-trend-up",   "Zusatzgewinn/Mo.",  fmt(r["mm"]),         f"+{r['ad']:.1f} Deals × {margin}%"),
        ("fa-sack-dollar",      "Jahresgewinn",      fmt(r["am"]),         "nach 12 Monaten"),
        ("fa-percent",          "ROI",               f"{r['roi']:.0f}%",   fmt(r["net"]) + " Nettogewinn"),
        ("fa-hourglass-half",   "Payback",           f"{r['pb']:.1f} Mon.", "bis Break-even"),
    ]

    kpi_html = '<div class="kpi-grid">'
    for icon, label, value, sub in kpis:
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
        st.session_state.step = 6
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
        ("ROUNDEDCORNERS", [4], None, None),
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



def step6():
    render_progress(6)
    render_nav()
    r = st.session_state.results
    p = st.session_state.params

    if not r or not p:
        st.warning("Bitte zuerst den Kalkulator ausfüllen.")
        if st.button("← Zurück"):
            st.session_state.step = 5
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

    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("**👩‍🏫&nbsp; Schlagkräftige Argumente**",
                    unsafe_allow_html=True)
        args = [
            ("fa-sack-dollar",      "Gewinn, nicht Umsatz",
             f"Das Training generiert {fmt(r['am'])} zusätzlichen Jahresgewinn — "
             "kein Umsatzversprechen, sondern echter Deckungsbeitrag."),
            ("fa-clock-rotate-left","Schnelle Amortisation",
             f"Die Investition zahlt sich in {r['pb']:.1f} Monaten zurück — "
             "schneller als jede Software-Einführung."),
            ("fa-fire",             "Opportunitätskosten des Abwartens",
             f"Jeder Monat ohne Training kostet {fmt(r['mm'])} entgangenen Gewinn. "
             "Nichts-Tun ist nicht kostenlos."),
            ("fa-shield",           "Begrenzter Downside",
             f"Selbst bei nur 20% Abschlussquote bleibt der ROI positiv. "
             "Das Risiko ist asymmetrisch."),
            ("fa-star",             "Referenzen statt Versprechen",
             "Zwei Kunden des Anbieters haben 22–28% erreicht. "
             "Das sind Marktdaten, kein Anbieter-Pitch."),
        ]
        for icon, title, text in args:
            st.markdown(f"""
            <div class="arg-item">
                <div class="arg-icon-wrap">
                    
                </div>
                <div>
                    <strong style="color:#1E2A5E;">{title}</strong><br>
                    <span style="color:#6B7280; font-size:0.87rem;">{text}</span>
                </div>
            </div>""", unsafe_allow_html=True)

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
        for icon, badge, label, sublabel, jahresgewinn, roi_v in scenarios:
            st.markdown(f"""
            <div class="scenario-tile">
                <div class="s-badge {badge}">
                     {label}
                    <span style="color:#9CA3AF; font-weight:400;">&nbsp;— {sublabel}</span>
                </div>
                <div style="font-size:0.87rem; color:#6B7280;">
                    Jahresgewinn: <strong style="color:#1E2A5E;">{jahresgewinn}</strong>
                    &nbsp;·&nbsp; ROI: <strong style="color:#1E2A5E;">{roi_v}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

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

    st.markdown("""
    <div class="footer">
        ♥
        HR loves Finance &nbsp;·&nbsp; Anne Schuster Consulting &nbsp;·&nbsp; anneschuster.com
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from io import BytesIO
import json
import requests

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Joey's Business Case | HR loves Finance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS (old proven base + enhancements) ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background-color: #F5F0E6; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #1E2A5E !important; overflow-y: auto !important; }
[data-testid="stSidebar"] > div:first-child { overflow-y: auto !important; padding-bottom: 2rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #F5F0E6 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #B8BCDE !important;
    font-family: 'DM Serif Display', serif !important;
}

/* ── Header ── */
.main-title {
    font-family: 'DM Serif Display', serif;
    color: #1E2A5E; font-size: 2.4rem; line-height: 1.15; margin-bottom: 0.2rem;
}
.main-subtitle {
    color: #6B7280; font-size: 0.85rem; font-weight: 400;
    letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 1.8rem;
}

/* ── Navy Boxes ── */
.scenario-box {
    background: #1E2A5E; border-radius: 14px;
    padding: 1.8rem 2.2rem; color: #F5F0E6; margin-bottom: 1.2rem;
}
.scenario-box h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem; color: #B8BCDE; margin-bottom: 0.8rem;
}
.scenario-box p { font-size: 0.93rem; line-height: 1.75; opacity: 0.92; }

.mission-box {
    background: #B8BCDE; border-radius: 12px;
    padding: 1.3rem 1.7rem; margin-bottom: 1rem;
    border-left: 4px solid #1E2A5E;
}
.mission-box h3 {
    font-family: 'DM Serif Display', serif;
    color: #1E2A5E; font-size: 1.05rem; margin-bottom: 0.5rem;
}
.mission-box ul { margin:0; padding-left:1.2rem; color:#1E2A5E; font-size:0.9rem; line-height:1.8; }

/* ── KPI Cards ── */
.kpi-card {
    background: #1E2A5E; border-radius: 12px;
    padding: 1.2rem 1.3rem; text-align: center; color: #F5F0E6;
}
.kpi-card .kpi-label {
    font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: #B8BCDE; margin-bottom: 0.35rem;
}
.kpi-card .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem; color: #F5F0E6; line-height: 1;
}
.kpi-card .kpi-sub { font-size: 0.7rem; color: #B8BCDE; margin-top: 0.25rem; }

/* ── Dialogue ── */
.dialogue-box {
    background: white; border-radius: 12px;
    border: 1.5px solid #D1CCBF;
    padding: 1.1rem 1.4rem; margin-bottom: 0.8rem;
    box-shadow: 0 2px 6px rgba(30,42,94,0.08);
}
.speaker-row { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.45rem; }
.speaker-avatar {
    width:26px; height:26px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:0.78rem; font-weight:700; flex-shrink:0;
}
.av-joey { background:#1E2A5E; color:#F5F0E6; }
.av-vl   { background:#E5E1D8; color:#6B7280; }
.av-th   { background:#F3F4F6; color:#9CA3AF; }
.speaker-name { font-size:0.7rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; }
.sn-joey { color:#1E2A5E; } .sn-vl { color:#6B7280; } .sn-th { color:#9CA3AF; }
.dialogue-text  { color:#1E2A5E; font-size:0.93rem; line-height:1.75; }
.dialogue-thought { color:#6B7280; font-size:0.88rem; line-height:1.7; font-style:italic; }

/* ── Swifty ── */
.swifty-header { display:flex; align-items:center; gap:0.8rem; margin-bottom:1.2rem; }
.swifty-avatar {
    width:42px; height:42px; border-radius:50%;
    background:#D1FAE5; display:flex; align-items:center;
    justify-content:center; font-size:1.2rem; flex-shrink:0;
}
.swifty-label { font-size:0.7rem; font-weight:700; color:#059669; letter-spacing:0.07em; text-transform:uppercase; }
.swifty-bubble {
    background:#1E2A5E; color:#F5F0E6;
    border-radius:14px 14px 14px 4px;
    padding:0.9rem 1.2rem; margin:0.4rem 0;
    font-size:0.92rem; line-height:1.75; max-width:80%;
}
.user-bubble {
    background:#B8BCDE; color:#1E2A5E;
    border-radius:14px 14px 4px 14px;
    padding:0.85rem 1.1rem; margin:0.4rem 0 0.4rem auto;
    font-size:0.92rem; line-height:1.7; max-width:80%; text-align:right;
}

/* ── Checklist ── */
.check-item {
    background:white; border-radius:10px; border:1.5px solid #D1CCBF;
    padding:0.8rem 1.1rem; margin-bottom:0.5rem;
    display:flex; gap:0.7rem; align-items:flex-start;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:transparent; gap:0.4rem; }
.stTabs [data-baseweb="tab"] {
    background:transparent; border:1.5px solid #1E2A5E;
    border-radius:8px; color:#1E2A5E; font-weight:500; padding:0.4rem 1rem;
}
.stTabs [aria-selected="true"] { background:#1E2A5E !important; color:#F5F0E6 !important; }

/* ── Recommendation ── */
.rec-success {
    background:#D1FAE5; border-left:4px solid #059669;
    border-radius:8px; padding:1rem 1.4rem; color:#065F46; margin:1rem 0;
}
.rec-warning {
    background:#FEF3C7; border-left:4px solid #D97706;
    border-radius:8px; padding:1rem 1.4rem; color:#92400E; margin:1rem 0;
}

/* ── Leitfragen ── */
.leitfrage {
    background:#F5F0E6; border:1.5px solid #1E2A5E;
    border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:0.5rem;
    color:#1E2A5E; font-size:0.9rem; line-height:1.5;
}

/* ── Divider ── */
.navy-divider { border:none; border-top:2px solid #1E2A5E; margin:1.5rem 0; opacity:0.12; }

/* ── Buttons ── */
.stButton > button {
    background:#1E2A5E !important; color:#F5F0E6 !important;
    border:none !important; border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important;
    font-weight:500 !important; transition:opacity 0.2s !important;
}
.stButton > button:hover { opacity:0.82 !important; }

.footer {
    margin-top:3rem; padding-top:1rem; border-top:1px solid #D1D5DB;
    text-align:center; color:#9CA3AF; font-size:0.78rem;
}
</style>
""", unsafe_allow_html=True)


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


# ─── Swifty ───────────────────────────────────────────────────────────────────
SWIFTY_SYSTEM = """Du bist Swifty — ein motivierender, warmherziger Business-Case-Coach für HR-Professionals.

Deine Persönlichkeit:
- Enthusiastisch und ermutigend ("Genau der richtige Gedanke!", "Das ist eine starke Frage!")
- Du stellst immer nur EINE Frage pro Nachricht
- Direkt aber nie belehrend · Maximal 120 Wörter · Deutsch · Du-Form

Das Szenario: Joey (HR Business Partnerin) — Sales-Training 25.000 €, Budget überschritten, CFO und CEO müssen überzeugt werden.

Führe sie durch:
1. Warum jetzt? Welches konkrete Problem lösen wir?
2. Was passiert wenn wir NICHT investieren?
3. Welche Infos braucht Joey noch?
4. Welche Einwände könnte der CFO haben?
5. Wie kommuniziert sie Gewinn statt Umsatz?

Nach 5-6 Austauschen: Zusammenfassen und beenden mit: "Du bist bereit! Klick auf 'Weiter zum Kalkulator' 🚀"
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


# ─── Charts ───────────────────────────────────────────────────────────────────
def make_charts(r):
    navy, lav, cream = "#1E2A5E", "#B8BCDE", "#F5F0E6"
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Investition vs. Jahresgewinn", "Break-even Verlauf"),
        horizontal_spacing=0.12)

    fig.add_trace(go.Bar(
        x=["💸 Investition", "📈 Jahresgewinn"],
        y=[r["total"], r["am"]],
        marker_color=[lav, navy],
        text=[fmt(r["total"]), fmt(r["am"])],
        textposition="auto", textfont=dict(color=[navy, cream]),
    ), row=1, col=1)

    months = list(range(13))
    cum = [-r["total"]]
    for _ in range(12): cum.append(cum[-1] + r["mm"])

    fig.add_trace(go.Scatter(
        x=months, y=cum, mode="lines+markers",
        line=dict(color=navy, width=3), marker=dict(color=navy, size=7),
        fill="tozeroy", fillcolor="rgba(30,42,94,0.08)",
    ), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="#DC2626",
                  annotation_text=f"  Break-even: Monat {r['pb']:.1f}",
                  annotation_font_color="#DC2626", row=1, col=2)

    fig.update_layout(height=300, showlegend=False,
                      plot_bgcolor=cream, paper_bgcolor=cream,
                      font=dict(family="DM Sans, sans-serif", color=navy),
                      margin=dict(t=40, b=10, l=10, r=10))
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", linecolor="#E5E7EB")
    return fig


# ─── PDF ──────────────────────────────────────────────────────────────────────
def generate_pdf(r, p):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=14*mm, bottomMargin=14*mm)

    NAVY = colors.HexColor("#1E2A5E")
    LAV  = colors.HexColor("#B8BCDE")
    WHITE = colors.white
    GRAY  = colors.HexColor("#6B7280")
    LGRAY = colors.HexColor("#F3F2EE")
    GREEN = colors.HexColor("#D1FAE5")

    def s(name, **kw): return ParagraphStyle(name, **kw)
    sh   = s("h",   fontSize=20, textColor=WHITE, leading=26, fontName="Helvetica-Bold")
    shs  = s("hs",  fontSize=8,  textColor=LAV,   leading=12, fontName="Helvetica")
    sv   = s("v",   fontSize=18, textColor=WHITE, leading=24, fontName="Helvetica-Bold", alignment=TA_CENTER)
    sl   = s("l",   fontSize=7,  textColor=LAV,   leading=10, fontName="Helvetica",      alignment=TA_CENTER)
    sec  = s("sec", fontSize=10, textColor=WHITE, leading=14, fontName="Helvetica-Bold")
    sb   = s("sb",  fontSize=8,  textColor=colors.HexColor("#1E2A5E"), leading=13, fontName="Helvetica")
    sbg  = s("sbg", fontSize=8,  textColor=GRAY,  leading=12, fontName="Helvetica")
    sbw  = s("sbw", fontSize=8,  textColor=WHITE, leading=13, fontName="Helvetica")
    sbwb = s("sbwb",fontSize=8,  textColor=WHITE, leading=13, fontName="Helvetica-Bold")
    sat  = s("sat", fontSize=8,  textColor=colors.HexColor("#1E2A5E"), leading=12, fontName="Helvetica-Bold")
    sft  = s("ft",  fontSize=7,  textColor=GRAY,  leading=10, fontName="Helvetica", alignment=TA_CENTER)

    W = 174*mm
    story = []

    # Header
    hdr = Table([[Paragraph("HR loves Finance", sh)],
                 [Paragraph(f"Joey's Business Case  ·  Sales Training ROI  ·  {datetime.now().strftime('%d.%m.%Y')}", shs)]],
                colWidths=[W])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 10), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12), ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 6))

    # KPIs
    kpi_w = W / 5
    kpis = [
        ("GESAMTINVESTITION", fmt(r["total"]),      "Training + Ausfall"),
        ("ZUSATZGEWINN/MON.", fmt(r["mm"]),          f"+{r['ad']:.1f} Deals"),
        ("JAHRESGEWINN",      fmt(r["am"]),          "nach 12 Monaten"),
        ("ROI",               f"{r['roi']:.0f}%",   "Return on Investment"),
        ("PAYBACK",           f"{r['pb']:.1f} Mon.","bis Break-even"),
    ]
    kpi_tbl = Table(
        [[Paragraph(k[0], sl) for k in kpis],
         [Paragraph(k[1], sv) for k in kpis],
         [Paragraph(k[2], sl) for k in kpis]],
        colWidths=[kpi_w]*5)
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 2), ("RIGHTPADDING",  (0,0), (-1,-1), 2),
        ("LINEAFTER",     (0,0), (3,-1),  0.5, colors.HexColor("#2E3D6E")),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 7))

    def navy_hdr(text):
        t = Table([[Paragraph(text, sec)]], colWidths=[W])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),10)]))
        return t

    # Kalkulation
    story.append(navy_hdr("Kalkulation im Detail"))
    story.append(Spacer(1,1))
    calc_rows = [
        ("Trainingskosten", f"{p.participants} x {fmt(p.cost_per_person)}", fmt(r["tc"]), False),
        ("Ausfallkosten", f"{p.participants} x {p.training_days}d x {p.daily_rate:.0f}EUR", fmt(r["oc"]), False),
        ("Gesamtinvestition", "Summe", fmt(r["total"]), True),
        ("Zusaetzl. Deals/Mo.", f"{p.monthly_leads} x ({p.target_rate}% - {p.current_rate}%)", f"{r['ad']:.1f} Deals", False),
        ("Mehrumsatz/Monat", f"{r['ad']:.1f} x {fmt(p.deal_value)}", fmt(r["mr"]), False),
        ("Zusatzgewinn/Monat", f"{fmt(r['mr'])} x {p.margin_rate}%", fmt(r["mm"]), False),
        ("Jahresgewinn", "x 12 Monate", fmt(r["am"]), True),
        ("ROI", f"({fmt(r['net'])} / {fmt(r['total'])}) x 100", f"{r['roi']:.0f}%", True),
        ("Payback", f"{fmt(r['total'])} / {fmt(r['mm'])}", f"{r['pb']:.1f} Monate", True),
    ]
    navy_rows = [i for i, row in enumerate(calc_rows) if row[3]]
    tdata = [[Paragraph(l, sbwb if b else sb),
              Paragraph(f, sbw if b else sbg),
              Paragraph(res, sbwb if b else sb)]
             for l, f, res, b in calc_rows]
    ctbl = Table(tdata, colWidths=[45*mm, 90*mm, 39*mm])
    ts = [("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LGRAY]),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
          ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
          ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDD9D0")),
          ("BOX",(0,0),(-1,-1),1,LAV),("VALIGN",(0,0),(-1,-1),"MIDDLE")]
    for ri in navy_rows: ts.append(("BACKGROUND",(0,ri),(-1,ri),NAVY))
    ctbl.setStyle(TableStyle(ts))
    story.append(ctbl)
    story.append(Spacer(1, 7))

    # Args + Scenarios side by side
    arg_hdr = Table([[Paragraph("Top-Argumente fuer CFO + CEO", sec)]], colWidths=[90*mm])
    arg_hdr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    args = [
        ("Gewinn, nicht Umsatz", f"{fmt(r['am'])} Jahresgewinn — kein Umsatzversprechen."),
        ("Schnelle Amortisation", f"Payback in {r['pb']:.1f} Monaten."),
        ("Opportunitaetskosten", f"Jeder Monat kostet {fmt(r['mm'])} entgangenen Gewinn."),
        ("Begrenzter Downside", "Selbst bei 20% bleibt ROI positiv."),
        ("Referenzen", "Kunden erreichten 22-28% — Marktdaten."),
    ]
    atbl = Table([[Paragraph(f"<b>{t}</b><br/>{d}", sb)] for t, d in args], colWidths=[90*mm])
    atbl.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LGRAY]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDD9D0")),
        ("BOX",(0,0),(-1,-1),1,LAV),("VALIGN",(0,0),(-1,-1),"TOP")]))

    sc_hdr = Table([[Paragraph("Szenarien", sec)]], colWidths=[80*mm])
    sc_hdr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    cons_ad = p.monthly_leads*0.20 - (p.monthly_leads*p.current_rate/100)
    cons_am = cons_ad * p.deal_value * (p.margin_rate/100) * 12
    cons_roi = ((cons_am - r["total"]) / r["total"]) * 100
    sc_data = [
        [Paragraph("<b>Szenario</b>",sbw), Paragraph("<b>Jahresgewinn</b>",sbw), Paragraph("<b>ROI</b>",sbw)],
        [Paragraph("Konservativ (20%)",sb), Paragraph(fmt(cons_am),sb), Paragraph(f"{cons_roi:.0f}%",sb)],
        [Paragraph("<b>Realistisch (25%)</b>",sat), Paragraph(f"<b>{fmt(r['am'])}</b>",sat), Paragraph(f"<b>{r['roi']:.0f}%</b>",sat)],
        [Paragraph("Optimistisch (+25%)",sb), Paragraph(fmt(r["am"]*1.25),sb), Paragraph(f"{((r['am']*1.25-r['total'])/r['total']*100):.0f}%",sb)],
    ]
    stbl = Table(sc_data, colWidths=[32*mm,28*mm,20*mm])
    stbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,GREEN,LGRAY]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDD9D0")),
        ("BOX",(0,0),(-1,-1),1,LAV),("FONTNAME",(0,2),(-1,2),"Helvetica-Bold"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))

    combo = Table([[arg_hdr,Spacer(4,1),sc_hdr],[atbl,Spacer(4,1),stbl]],
                  colWidths=[90*mm,4*mm,80*mm])
    combo.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(combo)

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LAV, spaceAfter=5))
    story.append(Paragraph(
        "HR loves Finance  ·  Anne Schuster Consulting  ·  anneschuster.com  ·  CIMA Fellow (FCMA, CGMA)", sft))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ─── Dialogue Helper ──────────────────────────────────────────────────────────
def dlg(speaker, text, kind="joey"):
    icons = {"joey": ("J", "av-joey", "sn-joey"), "vl": ("T", "av-vl", "sn-vl"), "thought": ("···", "av-th", "sn-th")}
    icon, av, sn = icons.get(kind, icons["joey"])
    txt_cls = "dialogue-thought" if kind == "thought" else "dialogue-text"
    return f"""
    <div class="dialogue-box">
        <div class="speaker-row">
            <div class="speaker-avatar {av}">{icon}</div>
            <div class="speaker-name {sn}">{speaker}</div>
        </div>
        <div class="{txt_cls}">„{text}"</div>
    </div>"""


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    st.sidebar.markdown("## ⚙️ Parameter")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Das Training**")
    participants  = st.sidebar.number_input("Teilnehmer", 1, 50, 10)
    cost_pp       = st.sidebar.number_input("Kosten pro Person (€)", 500, 20000, 2500, 100)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sales-Metriken**")
    leads         = st.sidebar.number_input("Leads pro Monat", 10, 1000, 200, 10)
    curr_rate     = st.sidebar.slider("Abschlussquote aktuell (%)", 1.0, 50.0, 15.0, 0.5)
    tgt_rate      = st.sidebar.slider("Abschlussquote Ziel (%)", 1.0, 50.0, 25.0, 0.5)
    deal_val      = st.sidebar.number_input("Ø Deal-Wert (€)", 1000, 500000, 15000, 500)
    margin        = st.sidebar.slider("Marge pro Deal (%)", 5.0, 80.0, 25.0, 1.0)

    with st.sidebar.expander("Erweiterte Parameter"):
        t_days    = st.number_input("Trainingstage", 1, 10, 3)
        daily_r   = st.number_input("Tagessatz Ausfall/MA (€)", 100, 2000, 400, 50)

    return Params(participants, cost_pp, leads, curr_rate, tgt_rate, deal_val, margin, t_days, daily_r)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Session state
    if "swifty_messages" not in st.session_state:
        st.session_state.swifty_messages = []

    # Sidebar
    params = render_sidebar()
    r = calculate(params)

    # Header
    st.markdown('<div class="main-title">Joey\'s Business Case</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">HR loves Finance &nbsp;·&nbsp; Workshop Tool &nbsp;·&nbsp; Anne Schuster Consulting</div>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋  Das Szenario",
        "🤖  Business Case Begleiter",
        "🔢  ROI Kalkulator"
    ])

    # ── Tab 1: Szenario ───────────────────────────────────────────────────────
    with tab1:
        col_l, col_r = st.columns([3, 2], gap="large")

        with col_l:
            st.markdown("""
            <div class="scenario-box">
                <h2>Die Protagonistin</h2>
                <p>Joey ist eine <strong>proaktive HR Business Partnerin</strong>. Sie hört zu, erkennt Muster und ergreift die Initiative, um das Business voranzubringen. Anstatt nur Budgets zu verwalten, will sie <strong>Wert schaffen</strong>.</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div class="scenario-box">
                <h2>Die Herausforderung</h2>
                <p>Das Sales-Team stagniert bei einer <strong>Abschlussquote von 15%</strong>. Eine neue Trainingsmethode könnte die Quote auf <strong>25%</strong> heben – aber die Investition von <strong>25.000 €</strong> übersteigt das genehmigte Budget.</p>
                <p style="margin-top:0.7rem;">CFO und CEO müssen überzeugt werden – schnell, denn <strong>der Wettbewerb schläft nicht.</strong></p>
                <p style="margin-top:0.7rem; font-style:italic; color:#B8BCDE;">Joey nimmt sich der Sache an.</p>
            </div>""", unsafe_allow_html=True)

            # The conversation
            st.markdown("**🎬 Das Gespräch** — Montagmorgen, Flur vor dem Sales-Büro")
            st.markdown("""
            <div class="dialogue-box" style="border-left:3px solid #E5E1D8;">
                <div style="font-size:0.85rem;color:#9CA3AF;font-style:italic;line-height:1.7;">
                    Joey ist auf dem Weg zum Drucker, als sie Thomas, den Vertriebsleiter, mit dem Telefon am Ohr vorbeirennen sieht. Er winkt sie heran.
                </div>
            </div>""", unsafe_allow_html=True)

            for kind, speaker, text in [
                ("vl",      "Thomas — Vertriebsleiter",
                 "Joey, kurz — ich hab gerade eine Anfrage von Consilium Training. Die haben ein neues Sales-Programm, das ist wirklich stark. Drei Tage, die ganze Truppe durch. Der Anbieter sagt, andere Unternehmen haben ihre Abschlussquote damit von 15 auf 25 Prozent gesteigert."),
                ("joey",    "Joey", "Klingt interessant. Was kostet das?"),
                ("vl",      "Thomas",
                 "2.500 € pro Person. Wir wären zehn Leute — also 25.000 €. Ich weiß, das übersteigt unser genehmigtes Trainingsbudget. Aber ich glaube wirklich daran. Kannst du das irgendwie durchkriegen?"),
                ("thought", "Joey — innerlich",
                 "Okay. Thomas glaubt daran — das ist ein gutes Zeichen. Aber der CFO wird Zahlen sehen wollen. Echte Zahlen. Nicht Versprechen vom Anbieter. Ich muss das durchdenken, bevor ich irgendwo anklopfe."),
                ("joey",    "Joey", "Ich schaue mir das an, Thomas. Gib mir bis Mittwoch."),
            ]:
                st.markdown(dlg(speaker, text, kind), unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div class="mission-box">
                <h3>🎯 Deine Mission</h3>
                <p style="color:#1E2A5E;font-size:0.88rem;margin-bottom:0.6rem;">Versetze dich in die Rolle von Joey. Entwickle eine überzeugende, datengestützte Argumentation für die Geschäftsführung.</p>
                <ul>
                    <li>Nutze den ROI-Rechner mit den genannten Werten</li>
                    <li>Ermittle den zusätzlichen <strong>Gewinn</strong> (nicht nur Umsatz!) nach 12 Monaten</li>
                    <li><em>Bonus:</em> Was ändert sich bei nur 20% Abschlussquote?</li>
                </ul>
            </div>""", unsafe_allow_html=True)

            st.markdown("**Leitfragen für deine Argumentation**")
            for q in [
                "Wie hoch ist der ROI nach einem Jahr?",
                "Nach wie vielen Monaten amortisiert sich die Investition?",
                "Was ist das finanzielle Risiko beim Status quo?",
                "Bonus: Business Case bei nur 20% Abschlussquote?",
            ]:
                st.markdown(f'<div class="leitfrage">❓ {q}</div>', unsafe_allow_html=True)

            # Quick KPIs preview
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📊 Quick Preview** *(Parameter links anpassen)*")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="kpi-card">
                    <div class="kpi-label">Jahresgewinn</div>
                    <div class="kpi-value">{fmt(r["am"])}</div>
                    <div class="kpi-sub">nach 12 Monaten</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="kpi-card">
                    <div class="kpi-label">ROI</div>
                    <div class="kpi-value">{r["roi"]:.0f}%</div>
                    <div class="kpi-sub">Payback: {r["pb"]:.1f} Mon.</div>
                </div>""", unsafe_allow_html=True)

    # ── Tab 2: Swifty ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div class="scenario-box" style="margin-bottom:1.2rem;">
            <h2>🤖 Business Case Begleiter</h2>
            <p>Swifty führt dich durch den Denkprozess — bevor du zum Kalkulator gehst. Immer eine Frage. Motivierend. Auf den Punkt.</p>
        </div>""", unsafe_allow_html=True)

        # Init Swifty
        if not st.session_state.swifty_messages:
            opening = (
                "Hey Joey — super, dass du dir die Zeit nimmst! 🎉\n\n"
                "Bevor wir zu den Zahlen kommen, lass uns bei der wichtigsten Frage beginnen — die viele überspringen:\n\n"
                "**Welches konkrete Problem hat das Sales-Team gerade?** Was steckt hinter der stagnierenden Abschlussquote?"
            )
            st.session_state.swifty_messages = [{"role": "assistant", "content": opening}]

        # Choice: Swifty or Checklist
        col_choice1, col_choice2 = st.columns(2, gap="large")

        with col_choice1:
            st.markdown("**Mit Swifty arbeiten**")
            st.markdown('<div class="swifty-header"><div class="swifty-avatar">🤖</div><div><div class="swifty-label">Swifty · Coach</div><div style="font-size:0.78rem;color:#6B7280;">motivierend · eine Frage at a time</div></div></div>', unsafe_allow_html=True)

            for msg in st.session_state.swifty_messages:
                if msg["role"] == "assistant":
                    st.markdown(f'<div class="swifty-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

            last = st.session_state.swifty_messages[-1]["content"]
            if "Du bist bereit" in last or "bereit!" in last:
                if st.button("🔢  Weiter zum Kalkulator →"):
                    st.info("Gehe zu Tab 3 — ROI Kalkulator")
            else:
                user_input = st.chat_input("Deine Antwort an Swifty …")
                if user_input:
                    st.session_state.swifty_messages.append({"role": "user", "content": user_input})
                    with st.spinner("Swifty denkt …"):
                        resp = swifty_call(st.session_state.swifty_messages)
                    st.session_state.swifty_messages.append({"role": "assistant", "content": resp})
                    st.rerun()

            if st.button("🔄 Neu starten", key="reset_swifty"):
                st.session_state.swifty_messages = []
                st.rerun()

        with col_choice2:
            st.markdown("**Oder: Direkte Checkliste**")
            st.markdown("*Für alle die schon wissen was sie fragen wollen.*")
            items = [
                ("❓", "Warum jetzt?", "Sales-Team stagniert seit Q3 bei 15%."),
                ("⚠️", "Kosten des Nicht-Handelns?", "Entgangener Gewinn jeden Monat."),
                ("📋", "Welche Zahlen brauche ich?", "Leads, Deal-Wert, Marge, Teilnehmer."),
                ("🛡️", "Warum wirkt das Training?", "Referenzkunden mit 22-28% Ergebnis."),
                ("💰", "Gewinn statt Umsatz?", "Deckungsbeitrag ist das CFO-Argument."),
                ("↙️", "Konservatives Szenario?", "Bei 20% ist der ROI noch immer positiv."),
            ]
            for icon, title, detail in items:
                st.markdown(f"""
                <div class="check-item">
                    <span style="font-size:1rem;">{icon}</span>
                    <div>
                        <strong style="color:#1E2A5E;">{title}</strong><br>
                        <span style="color:#6B7280;font-size:0.86rem;">{detail}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Tab 3: ROI Kalkulator ─────────────────────────────────────────────────
    with tab3:
        # KPI Row
        c1, c2, c3, c4, c5 = st.columns(5)
        kpis = [
            ("💸 Investition",     fmt(r["total"]), "Training + Ausfall"),
            ("📈 Zusatzgewinn/Mo.", fmt(r["mm"]),    f"+{r['ad']:.1f} Deals"),
            ("💰 Jahresgewinn",    fmt(r["am"]),     "nach 12 Monaten"),
            ("📊 ROI",             f"{r['roi']:.0f}%", fmt(r["net"]) + " Netto"),
            ("⏳ Payback",         f"{r['pb']:.1f} Mon.", "bis Break-even"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4, c5], kpis):
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)

        # Recommendation
        if r["roi"] > 80 and r["pb"] < 6:
            st.markdown(f"""<div class="rec-success">
                <strong>✅ Starker Business Case — Investition klar empfehlenswert.</strong><br>
                ROI von <strong>{r['roi']:.0f}%</strong> · Payback in <strong>{r['pb']:.1f} Monaten</strong> ·
                Jeder Euro bringt <strong>{r['roi']/100+1:.1f}x zurück</strong>.
            </div>""", unsafe_allow_html=True)
        elif r["roi"] > 30:
            st.markdown(f"""<div class="rec-warning">
                <strong>👍 Training lohnt sich — Argumentation schärfen.</strong><br>
                ROI von <strong>{r['roi']:.0f}%</strong> · Payback: <strong>{r['pb']:.1f} Monate</strong>.
            </div>""", unsafe_allow_html=True)

        st.plotly_chart(make_charts(r), use_container_width=True)
        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)

        # Sub-tabs
        s1, s2, s3 = st.tabs(["📐 Kalkulation", "🔍 Szenarien", "💼 CFO Argumente"])

        with s1:
            ca, cb = st.columns(2)
            with ca:
                st.markdown(f"""
**Investment-Aufbau**
- Trainingskosten: {params.participants} × {fmt(params.cost_per_person)} = **{fmt(r["tc"])}**
- Ausfallkosten: {params.participants} × {params.training_days}d × {params.daily_rate}€ = **{fmt(r["oc"])}**
- **Gesamtinvestition: {fmt(r["total"])}**

**Deal-Steigerung**
- Aktuell: {params.monthly_leads} × {params.current_rate}% = **{r["cd"]:.1f} Deals/Mo.**
- Ziel: {params.monthly_leads} × {params.target_rate}% = **{r["td"]:.1f} Deals/Mo.**
- Zusätzlich: **+{r["ad"]:.1f} Deals/Mo.**""")
            with cb:
                st.markdown(f"""
**Gewinn-Berechnung**
- Mehrumsatz: {r["ad"]:.1f} × {fmt(params.deal_value)} = **{fmt(r["mr"])}/Mo.**
- Monatsmarge: {fmt(r["mr"])} × {params.margin_rate}% = **{fmt(r["mm"])}/Mo.**
- **Jahresgewinn: {fmt(r["am"])}**

**ROI-Metriken**
- Nettogewinn: {fmt(r["am"])} − {fmt(r["total"])} = **{fmt(r["net"])}**
- ROI: **{r["roi"]:.0f}%**
- Payback: **{r["pb"]:.1f} Monate**""")

        with s2:
            cons_ad = params.monthly_leads * 0.20 - r["cd"]
            cons_am = cons_ad * params.deal_value * (params.margin_rate/100) * 12
            cons_roi = ((cons_am - r["total"]) / r["total"]) * 100
            best_am  = r["am"] * 1.25
            best_roi = ((best_am - r["total"]) / r["total"]) * 100
            c_c, c_r, c_b = st.columns(3)
            with c_c:
                st.markdown(f"""**🔵 Konservativ (20%)**\n- Jahresgewinn: **{fmt(cons_am)}**\n- ROI: **{cons_roi:.0f}%**\n\n*Investition lohnt sich.*""")
            with c_r:
                st.markdown(f"""**🟢 Realistisch ({params.target_rate}%)**\n- Jahresgewinn: **{fmt(r["am"])}**\n- ROI: **{r["roi"]:.0f}%**\n\n*Das ist der Basisfall.*""")
            with c_b:
                st.markdown(f"""**🟡 Optimistisch (+25%)**\n- Jahresgewinn: **{fmt(best_am)}**\n- ROI: **{best_roi:.0f}%**\n\n*Upside-Szenario.*""")

        with s3:
            st.markdown(f"""
**Top-Argumente für CFO & CEO**

1. **Gewinn, nicht Umsatz** — {fmt(r["am"])} zusätzlicher Jahresgewinn — echter Deckungsbeitrag, kein Umsatzversprechen.

2. **Schnelle Amortisation** — Payback in {r["pb"]:.1f} Monaten. Schneller als jede Software-Einführung.

3. **Opportunitätskosten** — Jeder Monat ohne Training kostet {fmt(r["mm"])} entgangenen Gewinn. Nichts-Tun ist nicht kostenlos.

4. **Begrenzter Downside** — Selbst bei nur 20% Abschlussquote bleibt der ROI positiv. Das Risiko ist asymmetrisch.

5. **Referenzen statt Versprechen** — Zwei Kunden des Anbieters haben 22–28% erreicht. Das sind Marktdaten, kein Pitch.""")

        # Export
        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)
        d1, d2 = st.columns([1, 4])
        with d1:
            pdf = generate_pdf(r, params)
            st.download_button("⬇️ PDF herunterladen", data=pdf,
                               file_name=f"joey_bc_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf")

    st.markdown('<div class="footer">HR loves Finance · Anne Schuster Consulting · anneschuster.com</div>',
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()

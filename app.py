import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import json
import requests

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Joey's Business Case | HR loves Finance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── App Background ── */
.stApp {
    background-color: #F5F0E6;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1E2A5E !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #F5F0E6 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #B8BCDE !important;
    font-family: 'DM Serif Display', serif !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stSliderThumb"] {
    background-color: #B8BCDE;
}

/* ── Main Title ── */
.main-title {
    font-family: 'DM Serif Display', serif;
    color: #1E2A5E;
    font-size: 2.6rem;
    line-height: 1.15;
    margin-bottom: 0.2rem;
}
.main-subtitle {
    color: #6B7280;
    font-size: 1rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* ── Scenario Box ── */
.scenario-box {
    background: #1E2A5E;
    border-radius: 16px;
    padding: 2rem 2.4rem;
    color: #F5F0E6;
    margin-bottom: 1.5rem;
}
.scenario-box h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #B8BCDE;
    margin-bottom: 1rem;
}
.scenario-box p {
    font-size: 0.95rem;
    line-height: 1.7;
    opacity: 0.92;
}

/* ── Mission Box ── */
.mission-box {
    background: #B8BCDE;
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.2rem;
    border-left: 4px solid #1E2A5E;
}
.mission-box h3 {
    font-family: 'DM Serif Display', serif;
    color: #1E2A5E;
    font-size: 1.1rem;
    margin-bottom: 0.6rem;
}
.mission-box ul {
    margin: 0;
    padding-left: 1.2rem;
    color: #1E2A5E;
    font-size: 0.92rem;
    line-height: 1.8;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #1E2A5E;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    color: #F5F0E6;
}
.kpi-card .kpi-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #B8BCDE;
    margin-bottom: 0.4rem;
}
.kpi-card .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #F5F0E6;
    line-height: 1;
}
.kpi-card .kpi-sub {
    font-size: 0.75rem;
    color: #B8BCDE;
    margin-top: 0.3rem;
}

/* ── Leitfragen ── */
.leitfrage {
    background: #F5F0E6;
    border: 1.5px solid #1E2A5E;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    color: #1E2A5E;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* ── Chat Bubbles ── */
.chat-user {
    background: #1E2A5E;
    color: #F5F0E6;
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.92rem;
    line-height: 1.6;
    max-width: 85%;
    margin-left: auto;
}
.chat-agent {
    background: #fff;
    border: 1.5px solid #B8BCDE;
    color: #1E2A5E;
    border-radius: 16px 16px 16px 4px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.92rem;
    line-height: 1.6;
    max-width: 85%;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: 1.5px solid #1E2A5E;
    border-radius: 8px;
    color: #1E2A5E;
    font-weight: 500;
    padding: 0.4rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: #1E2A5E !important;
    color: #F5F0E6 !important;
}

/* ── Recommendation blocks ── */
.rec-success {
    background: #D1FAE5;
    border-left: 4px solid #059669;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    color: #065F46;
}
.rec-warning {
    background: #FEF3C7;
    border-left: 4px solid #D97706;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    color: #92400E;
}

/* ── Divider ── */
.navy-divider {
    border: none;
    border-top: 2px solid #1E2A5E;
    margin: 1.5rem 0;
    opacity: 0.15;
}

/* ── Tag pill ── */
.tag-pill {
    display: inline-block;
    background: #B8BCDE;
    color: #1E2A5E;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-right: 0.4rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Data Classes ─────────────────────────────────────────────────────────────
@dataclass
class TrainingParameters:
    participants: int
    cost_per_person: float
    monthly_leads: int
    current_close_rate: float
    target_close_rate: float
    deal_value: float
    margin_rate: float
    training_days: int = 3
    daily_rate: float = 400.0

@dataclass
class ROIResults:
    total_investment: float
    training_costs: float
    opportunity_costs: float
    current_deals: float
    target_deals: float
    additional_deals: float
    monthly_revenue: float
    monthly_margin: float
    annual_margin: float
    roi_percentage: float
    roi_multiple: float
    payback_months: float
    net_benefit: float


# ─── Calculator ───────────────────────────────────────────────────────────────
class SalesROICalculator:
    def __init__(self):
        self.parameters: Optional[TrainingParameters] = None
        self.results: Optional[ROIResults] = None

    def fmt(self, amount: float) -> str:
        return f"{amount:,.0f} €".replace(",", ".")

    def calculate(self, params: TrainingParameters) -> ROIResults:
        self.parameters = params
        training_costs = params.participants * params.cost_per_person
        opportunity_costs = params.participants * params.training_days * params.daily_rate
        total_investment = training_costs + opportunity_costs

        current_deals = params.monthly_leads * (params.current_close_rate / 100)
        target_deals = params.monthly_leads * (params.target_close_rate / 100)
        additional_deals = target_deals - current_deals

        monthly_revenue = additional_deals * params.deal_value
        monthly_margin = monthly_revenue * (params.margin_rate / 100)
        annual_margin = monthly_margin * 12

        net_benefit = annual_margin - total_investment
        roi_percentage = (net_benefit / total_investment) * 100 if total_investment > 0 else 0
        roi_multiple = net_benefit / total_investment if total_investment > 0 else 0
        payback_months = (total_investment / monthly_margin) if monthly_margin > 0 else 0

        self.results = ROIResults(
            total_investment=total_investment,
            training_costs=training_costs,
            opportunity_costs=opportunity_costs,
            current_deals=current_deals,
            target_deals=target_deals,
            additional_deals=additional_deals,
            monthly_revenue=monthly_revenue,
            monthly_margin=monthly_margin,
            annual_margin=annual_margin,
            roi_percentage=roi_percentage,
            roi_multiple=roi_multiple,
            payback_months=payback_months,
            net_benefit=net_benefit
        )
        return self.results


# ─── AI Agent ─────────────────────────────────────────────────────────────────
AGENT_SYSTEM_PROMPT = """Du bist ein erfahrener Finance-Coach und Business-Case-Begleiter für HR-Professionals.
Deine Aufgabe ist es, die Teilnehmerin (sie spielt die Rolle von Joey, einer HR Business Partnerin) durch einen strukturierten Business-Case-Denkprozess zu führen.

Du arbeitest nach diesem Framework (8 Schritte, aber beginne immer mit der Vorfrage):

0. DIE VORFRAGE (essenziell, immer zuerst):
   "Warum investieren wir hier – und warum jetzt?" 
   Frage: Welches konkrete Problem lösen wir? Was passiert wenn wir nicht investieren? Ist das gerade wirklich die beste Verwendung knapper Ressourcen?

1. Entscheidung klären: Was steht zur Entscheidung?
2. Relevanten Hebel festlegen: Wo wirkt das auf die P&L? (Umsatz / Profitabilität / Risiko)
3. Zentrale Annahmen explizit machen: Was glauben wir – und warum?
4. Annahmen challengen: Hält das einer kritischen Betrachtung stand?
5. Szenarien durchspielen: konservativ / realistisch / optimistisch
6. Größenordnung einordnen: grob, nachvollziehbar, transparent
7. Investition vs. Nicht-Tun: Was kostet die Initiative – was kostet Abwarten?
8. Entscheidung ermöglichen: Ist das jetzt reif für eine Entscheidung?

Das konkrete Szenario: Joey ist HR Business Partnerin. Das Sales-Team stagniert bei 15% Abschlussquote. Ein Training könnte diese auf 25% heben. Kosten: 25.000 €. Das übersteigt das Budget. CFO und CEO müssen überzeugt werden.

Dein Stil:
- Stell immer nur EINE Frage pro Nachricht
- Sei warmherzig, aber direkt und fordernd wie ein guter Coach
- Wenn die Antwort oberflächlich ist, hake nach
- Verwende konkrete Zahlen aus dem Szenario wenn hilfreich
- Sprich auf Deutsch, du-Form
- Nach ca. 6-8 Austauschen, fasse die wichtigsten Business-Case-Elemente zusammen und empfiehl, den ROI-Kalkulator zu nutzen
- Maximal 150 Wörter pro Antwort
"""

def get_agent_response(messages: list) -> str:
    """Call Anthropic API for agent response."""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "⚠️ Kein API-Key konfiguriert. Bitte `ANTHROPIC_API_KEY` in den Streamlit Secrets hinterlegen."

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-opus-4-5",
                "max_tokens": 400,
                "system": AGENT_SYSTEM_PROMPT,
                "messages": messages
            },
            timeout=30
        )
        data = response.json()
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]
        return "Entschuldigung, ich konnte keine Antwort generieren."
    except Exception as e:
        return f"Verbindungsfehler: {str(e)}"


# ─── Charts ───────────────────────────────────────────────────────────────────
def make_charts(r: ROIResults, params: TrainingParameters):
    navy, lavender, cream = "#1E2A5E", "#B8BCDE", "#F5F0E6"

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Investment vs. Jahresgewinn", "Kumulierter Gewinn (12 Monate)", "Deals: Vorher vs. Nachher"),
        horizontal_spacing=0.1
    )

    # 1. Bar: Investment vs Annual Gain
    fig.add_trace(go.Bar(
        x=["💸 Investment", "📈 Jahresgewinn"],
        y=[r.total_investment, r.annual_margin],
        marker_color=[lavender, navy],
        text=[f"{r.total_investment:,.0f} €", f"{r.annual_margin:,.0f} €"],
        textposition="auto",
        textfont=dict(color=[navy, cream]),
        name=""
    ), row=1, col=1)

    # 2. Cumulative profit
    months = list(range(13))
    cumulative = [-r.total_investment]
    for _ in range(12):
        cumulative.append(cumulative[-1] + r.monthly_margin)

    fig.add_trace(go.Scatter(
        x=months, y=cumulative,
        mode="lines+markers",
        line=dict(color=navy, width=3),
        marker=dict(color=navy, size=7),
        fill="tozeroy",
        fillcolor="rgba(30,42,94,0.08)",
        name=""
    ), row=1, col=2)

    fig.add_hline(y=0, line_dash="dash", line_color="#9CA3AF",
                  annotation_text="Break-even", row=1, col=2)

    # 3. Deals comparison
    fig.add_trace(go.Bar(
        x=["Aktuell (15%)", f"Ziel ({params.target_close_rate}%)"],
        y=[r.current_deals, r.target_deals],
        marker_color=[lavender, navy],
        text=[f"{r.current_deals:.1f}", f"{r.target_deals:.1f}"],
        textposition="auto",
        textfont=dict(color=[navy, cream]),
        name=""
    ), row=1, col=3)

    fig.update_layout(
        height=360,
        showlegend=False,
        plot_bgcolor=cream,
        paper_bgcolor=cream,
        font=dict(family="DM Sans, sans-serif", color=navy),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", linecolor="#E5E7EB")
    return fig


# ─── Sidebar Inputs ────────────────────────────────────────────────────────────
def render_sidebar():
    st.sidebar.markdown("## ROI Parameter")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Das Training**")

    participants = st.sidebar.number_input("Teilnehmer", min_value=1, max_value=50, value=10)
    cost_per_person = st.sidebar.number_input("Kosten pro Person (€)", min_value=500, max_value=20000, value=2500, step=100)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sales-Metriken**")

    monthly_leads = st.sidebar.number_input("Leads pro Monat", min_value=10, max_value=1000, value=200, step=10)
    current_rate = st.sidebar.slider("Abschlussquote aktuell (%)", 1.0, 50.0, 15.0, 0.5)
    target_rate = st.sidebar.slider("Abschlussquote Ziel (%)", 1.0, 50.0, 25.0, 0.5)
    deal_value = st.sidebar.number_input("Deal-Wert Ø (€)", min_value=1000, max_value=500000, value=15000, step=500)
    margin_rate = st.sidebar.slider("Marge (%)", 5.0, 80.0, 30.0, 1.0)

    with st.sidebar.expander("Erweiterte Parameter"):
        training_days = st.number_input("Trainingstage", min_value=1, max_value=10, value=3)
        daily_rate = st.number_input("Tagessatz Ausfall (€)", min_value=100, max_value=2000, value=400, step=50)

    return TrainingParameters(
        participants=participants,
        cost_per_person=cost_per_person,
        monthly_leads=monthly_leads,
        current_close_rate=current_rate,
        target_close_rate=target_rate,
        deal_value=deal_value,
        margin_rate=margin_rate,
        training_days=training_days,
        daily_rate=daily_rate
    )


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="main-title">Joey's Business Case</div>
    <div class="main-subtitle">HR loves Finance · Workshop Tool</div>
    """, unsafe_allow_html=True)

    # Sidebar
    params = render_sidebar()
    calc = SalesROICalculator()
    r = calc.calculate(params)

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋  Das Szenario",
        "🤖  Business Case Begleiter",
        "🔢  ROI Kalkulator"
    ])

    # ── Tab 1: Szenario ────────────────────────────────────────────────────────
    with tab1:
        col_left, col_right = st.columns([3, 2], gap="large")

        with col_left:
            st.markdown("""
            <div class="scenario-box">
                <h2>Die Protagonistin</h2>
                <p>Joey ist eine <strong>proaktive HR Business Partnerin</strong>. Sie hört zu, erkennt Muster und ergreift die Initiative, um das Business voranzubringen. Anstatt nur Budgets zu verwalten, will sie <strong>Wert schaffen</strong>.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="scenario-box" style="margin-top: 1rem;">
                <h2>Die Herausforderung</h2>
                <p>Das Sales-Team stagniert bei einer <strong>Abschlussquote von 15%</strong>. Eine neue Trainingsmethode könnte die Quote auf <strong>25%</strong> heben – aber die Investition von <strong>25.000 €</strong> übersteigt das genehmigte Budget.</p>
                <p style="margin-top: 0.8rem;">Der CFO und CEO müssen überzeugt werden – und das schnell, denn <strong>der Wettbewerb schläft nicht.</strong></p>
                <p style="margin-top: 0.8rem; font-style: italic; color: #B8BCDE;">Joey nimmt sich der Sache an.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="mission-box">
                <h3>🎯 Deine Mission</h3>
                <p style="color: #1E2A5E; font-size: 0.9rem; margin-bottom: 0.6rem;">Versetze dich in die Rolle von Joey. Entwickle eine überzeugende, datengestützte Argumentation für die Geschäftsführung.</p>
                <ul>
                    <li>Nutze den ROI-Rechner mit den genannten Werten</li>
                    <li>Ermittle den zusätzlichen <strong>Gewinn</strong> (nicht nur Umsatz!) nach 12 Monaten</li>
                    <li><em>Bonus:</em> Was ändert sich bei nur 20% Abschlussquote?</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Leitfragen für deine Argumentation**")

            questions = [
                "Wie hoch ist der ROI nach einem Jahr?",
                "Nach wie vielen Monaten amortisiert sich die Investition?",
                "Was ist das finanzielle Risiko beim Status quo?",
                "Bonus: Wie sieht der Business Case bei nur 20% Abschlussquote aus?"
            ]
            for q in questions:
                st.markdown(f'<div class="leitfrage">❓ {q}</div>', unsafe_allow_html=True)

    # ── Tab 2: AI Agent ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="background: #1E2A5E; border-radius: 12px; padding: 1.2rem 1.6rem; margin-bottom: 1.5rem; color: #F5F0E6;">
            <strong style="font-family: 'DM Serif Display', serif; font-size: 1.1rem;">Business Case Begleiter</strong><br>
            <span style="font-size: 0.88rem; color: #B8BCDE;">Ich führe dich Schritt für Schritt durch das Business-Case-Denken — bevor du zum Kalkulator gehst.</span>
        </div>
        """, unsafe_allow_html=True)

        # Session state init
        if "agent_messages" not in st.session_state:
            st.session_state.agent_messages = []
            # Initial greeting
            opening = (
                "Hallo! Schön, dass du hier bist. Bevor wir zu den Zahlen kommen, "
                "möchte ich mit dir eine Frage stellen, die viele überspringen — "
                "und die doch die wichtigste ist:\n\n"
                "**Warum investieren wir hier – und warum jetzt?**\n\n"
                "Was ist das konkrete Problem, das ihr lösen wollt?"
            )
            st.session_state.agent_messages.append({
                "role": "assistant", "content": opening
            })

        # Display conversation
        for msg in st.session_state.agent_messages:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-agent">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

        # Input
        user_input = st.chat_input("Deine Antwort …")
        if user_input:
            st.session_state.agent_messages.append({"role": "user", "content": user_input})

            # Build message history for API (only user/assistant alternating)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.agent_messages
            ]

            with st.spinner(""):
                response = get_agent_response(api_messages)

            st.session_state.agent_messages.append({"role": "assistant", "content": response})
            st.rerun()

        col_r, col_l = st.columns([1, 4])
        with col_r:
            if st.button("🔄 Neu starten"):
                st.session_state.agent_messages = []
                st.rerun()

    # ── Tab 3: ROI Kalkulator ──────────────────────────────────────────────────
    with tab3:

        # KPI Row
        c1, c2, c3, c4, c5 = st.columns(5)
        kpis = [
            ("Gesamtinvestition", calc.fmt(r.total_investment), "direkte + Ausfallkosten"),
            ("Mehrumsatz / Monat", calc.fmt(r.monthly_revenue), f"{r.additional_deals:.1f} zusätzl. Deals"),
            ("Zusatzgewinn / Monat", calc.fmt(r.monthly_margin), f"{params.margin_rate}% Marge"),
            ("Jahresgewinn", calc.fmt(r.annual_margin), "nach 12 Monaten"),
            ("Payback", f"{r.payback_months:.1f} Mon.", f"ROI: {r.roi_percentage:.0f}%"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4, c5], kpis):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)

        # Recommendation
        if r.roi_percentage > 100 and r.payback_months < 6:
            st.markdown(f"""
            <div class="rec-success">
                <strong>✅ Klare Empfehlung: Training durchführen!</strong><br>
                ROI von <strong>{r.roi_percentage:.0f}%</strong> — Payback in nur <strong>{r.payback_months:.1f} Monaten</strong>.
                Jeder investierte Euro bringt <strong>{r.roi_multiple + 1:.1f} € zurück</strong>.
                Das ist eine starke Grundlage für den Business Case.
            </div>
            """, unsafe_allow_html=True)
        elif r.roi_percentage > 30:
            st.markdown(f"""
            <div class="rec-warning">
                <strong>👍 Training lohnt sich — Argumentation schärfen.</strong><br>
                ROI von <strong>{r.roi_percentage:.0f}%</strong>, Payback in <strong>{r.payback_months:.1f} Monaten</strong>.
                Prüfe deine Annahmen zur Marge und Conversion.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#FEE2E2; border-left:4px solid #DC2626; border-radius:8px; padding:1rem 1.4rem; color:#7F1D1D;">
                <strong>⚠️ Vorsicht: ROI zu niedrig für Budgetüberschreitung.</strong><br>
                ROI von <strong>{r.roi_percentage:.0f}%</strong>. Überprüfe Parameter oder suche Alternativen.
            </div>
            """, unsafe_allow_html=True)

        # Charts
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(make_charts(r, params), use_container_width=True)

        # Detailed Breakdown & Scenarios
        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)

        s_tab1, s_tab2, s_tab3 = st.tabs(["📐 Kalkulation", "🔍 Szenarien", "💼 CFO Argumente"])

        with s_tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                **Investment-Aufbau**
                - Trainingskosten: {params.participants} × {calc.fmt(params.cost_per_person)} = **{calc.fmt(r.training_costs)}**
                - Ausfallkosten: {params.participants} × {params.training_days} Tage × {params.daily_rate} € = **{calc.fmt(r.opportunity_costs)}**
                - **Gesamtinvestition: {calc.fmt(r.total_investment)}**

                **Deal-Steigerung**
                - Aktuell: {params.monthly_leads} × {params.current_close_rate}% = **{r.current_deals:.1f} Deals/Monat**
                - Ziel: {params.monthly_leads} × {params.target_close_rate}% = **{r.target_deals:.1f} Deals/Monat**
                - Zusätzlich: **+{r.additional_deals:.1f} Deals/Monat**
                """)
            with col_b:
                st.markdown(f"""
                **Gewinn-Berechnung**
                - Mehrumsatz: {r.additional_deals:.1f} × {calc.fmt(params.deal_value)} = **{calc.fmt(r.monthly_revenue)}/Monat**
                - Monatsmarge: {calc.fmt(r.monthly_revenue)} × {params.margin_rate}% = **{calc.fmt(r.monthly_margin)}/Monat**
                - **Jahresgewinn: {calc.fmt(r.annual_margin)}**

                **ROI-Metriken**
                - Nettogewinn: {calc.fmt(r.annual_margin)} − {calc.fmt(r.total_investment)} = **{calc.fmt(r.net_benefit)}**
                - ROI: **{r.roi_percentage:.0f}%**
                - Payback: **{r.payback_months:.1f} Monate**
                """)

        with s_tab2:
            col_cons, col_real, col_bonus = st.columns(3)
            # Conservative: only 20% close rate
            cons_deals = params.monthly_leads * 0.20 - r.current_deals
            cons_margin = cons_deals * params.deal_value * (params.margin_rate / 100) * 12
            cons_roi = ((cons_margin - r.total_investment) / r.total_investment) * 100

            with col_cons:
                st.markdown(f"""
                **🔵 Konservativ (20%)**
                Abschlussquote nur auf 20%

                - Zusatzgewinn/Jahr: **{calc.fmt(cons_margin)}**
                - ROI: **{cons_roi:.0f}%**
                - Payback: **{(r.total_investment / (cons_deals * params.deal_value * params.margin_rate / 100)):.1f} Monate**

                *Auch hier: Investition lohnt sich.*
                """)
            with col_real:
                st.markdown(f"""
                **🟢 Realistisch (25%)**
                Abschlussquote auf {params.target_close_rate}%

                - Zusatzgewinn/Jahr: **{calc.fmt(r.annual_margin)}**
                - ROI: **{r.roi_percentage:.0f}%**
                - Payback: **{r.payback_months:.1f} Monate**

                *Das ist der Basisfall.*
                """)

            best_margin = r.monthly_margin * 1.25 * 12
            best_roi = ((best_margin - r.total_investment) / r.total_investment) * 100
            with col_bonus:
                st.markdown(f"""
                **🟡 Optimistisch (+25%)**
                Training wirkt besser als erwartet

                - Zusatzgewinn/Jahr: **{calc.fmt(best_margin)}**
                - ROI: **{best_roi:.0f}%**
                - Payback: **< {r.payback_months * 0.8:.1f} Monate**

                *Upside für die Argumentation.*
                """)

        with s_tab3:
            st.markdown(f"""
            **Top-Argumente für CFO & CEO**

            1. **Gewinn-Fokus** — Das Training generiert **{calc.fmt(r.annual_margin)} zusätzlichen Jahresgewinn** — das ist echtes Geld in der Kasse, kein Umsatzversprechen.

            2. **Schnelle Amortisation** — Die Investition zahlt sich in **{r.payback_months:.1f} Monaten** zurück. Schneller als jede Software-Einführung.

            3. **Opportunitätskosten** — Jeder Monat Verzögerung kostet uns **{calc.fmt(r.monthly_margin)}** entgangenen Gewinn. Der Status quo ist nicht kostenlos.

            4. **Downside ist begrenzt** — Selbst wenn das Training nur die Hälfte bringt: **{calc.fmt(r.annual_margin * 0.5)}** Jahresgewinn bei **{calc.fmt(r.total_investment)}** Einsatz ist noch immer positiv.

            5. **Marge als Hebel** — Wir reden nicht über Umsatz. Jeder zusätzliche Deal bringt **{calc.fmt(params.deal_value * params.margin_rate / 100)} echten Gewinn** — dauerhaft.
            """)

        # Export
        st.markdown("<hr class='navy-divider'>", unsafe_allow_html=True)
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "scenario": "Joey — HR Business Case Sales Training",
            "parameters": {
                "participants": params.participants,
                "cost_per_person": params.cost_per_person,
                "monthly_leads": params.monthly_leads,
                "current_close_rate": params.current_close_rate,
                "target_close_rate": params.target_close_rate,
                "deal_value": params.deal_value,
                "margin_rate": params.margin_rate
            },
            "results": {
                "total_investment": r.total_investment,
                "monthly_margin": r.monthly_margin,
                "annual_margin": r.annual_margin,
                "roi_percentage": r.roi_percentage,
                "payback_months": r.payback_months
            }
        }
        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            st.download_button(
                "⬇️ JSON Export",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"joey_roi_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
        with col_dl2:
            summary_txt = f"""Joey's Business Case — Sales Training ROI
Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}

PARAMETER
---------
Teilnehmer:         {params.participants}
Kosten/Person:      {calc.fmt(params.cost_per_person)}
Leads/Monat:        {params.monthly_leads}
Quote aktuell:      {params.current_close_rate}%
Quote Ziel:         {params.target_close_rate}%
Deal-Wert:          {calc.fmt(params.deal_value)}
Marge:              {params.margin_rate}%

ERGEBNISSE
----------
Gesamtinvestition:  {calc.fmt(r.total_investment)}
Zusatzgewinn/Monat: {calc.fmt(r.monthly_margin)}
Jahresgewinn:       {calc.fmt(r.annual_margin)}
ROI:                {r.roi_percentage:.0f}%
Payback:            {r.payback_months:.1f} Monate
"""
            st.download_button(
                "⬇️ Text Export",
                data=summary_txt,
                file_name=f"joey_roi_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )

    # Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #D1D5DB;
                text-align: center; color: #9CA3AF; font-size: 0.78rem;">
        HR loves Finance · Anne Schuster Consulting · anneschuster.com
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

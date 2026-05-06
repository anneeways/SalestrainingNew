# 🎯 Joey's Business Case — HR loves Finance

Ein interaktives Workshop-Tool für HR Business Partner, das zeigt, wie man eine datengestützte Investitionsentscheidung für die Geschäftsführung aufbereitet.

Entwickelt von **Anne Schuster Consulting** · [anneschuster.com](https://anneschuster.com)

---

## Das Szenario

Joey ist eine proaktive HR Business Partnerin. Das Sales-Team stagniert bei 15% Abschlussquote. Ein Training könnte die Quote auf 25% heben — aber die Investition von 25.000 € übersteigt das genehmigte Budget. CFO und CEO müssen überzeugt werden.

---

## Features

- **Business Case Begleiter** — KI-Agent führt durch ein strukturiertes 8-Schritte-Framework (inkl. der oft übersprungenen Vorfrage: *„Warum investieren wir hier — und warum jetzt?"*)
- **ROI Kalkulator** — Interaktive Berechnung mit anpassbaren Parametern
- **Szenarien** — Konservativ (20%) / Realistisch (25%) / Optimistisch
- **CFO Argumente** — Fertige Argumentationslinien für die Geschäftsführung
- **Export** — JSON und Text-Download der Ergebnisse

---

## Setup

### 1. Repository klonen

```bash
git clone https://github.com/DEIN-USERNAME/joeys-business-case.git
cd joeys-business-case
```

### 2. Abhängigkeiten installieren (lokal)

```bash
pip install -r requirements.txt
```

### 3. API-Key konfigurieren

Der Business Case Begleiter nutzt die Anthropic API. Du brauchst einen API-Key von [console.anthropic.com](https://console.anthropic.com).

**Lokal:** Erstelle eine Datei `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

**Streamlit Community Cloud:** App Settings → Secrets → folgendes eintragen:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

### 4. App starten

```bash
streamlit run app.py
```

---

## Deployment auf Streamlit Community Cloud

1. Repository auf GitHub pushen
2. Auf [share.streamlit.io](https://share.streamlit.io) einloggen
3. „New app" → GitHub-Repo auswählen → `app.py` als Main file
4. Unter „Advanced settings" → Secrets den API-Key eintragen
5. Deploy klicken

---

## Standard-Werte (Szenario Joey)

| Parameter | Wert |
|---|---|
| Teilnehmer | 10 |
| Kosten pro Person | 2.500 € |
| Gesamtinvestition Training | 25.000 € |
| Leads pro Monat | 200 |
| Abschlussquote aktuell | 15% |
| Abschlussquote Ziel | 25% |
| Ø Deal-Wert | 15.000 € |
| Marge | 30% |
| Trainingstage | 3 |
| Tagessatz Ausfall | 400 € |

---

## Projektstruktur

```
├── app.py              # Hauptanwendung
├── requirements.txt    # Python-Abhängigkeiten
├── README.md           # Diese Datei
└── .streamlit/
    └── secrets.toml    # API-Key (nicht ins Git einchecken!)
```

> **Hinweis:** `.streamlit/secrets.toml` unbedingt in `.gitignore` aufnehmen.

---

## Lizenz

Dieses Tool ist für interne Workshop- und Coaching-Zwecke entwickelt.  
© Anne Schuster Consulting

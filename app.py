import streamlit as st
import pandas as pd
import hashlib

# ------------- Benutzerverwaltung (Login) ----------------
USER_CREDENTIALS = {
    "admin2025": hashlib.sha256("admin2025".encode()).hexdigest()
}

def check_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed

# --------- Minimalistisches Login UI mit Emojis ----------
def show_login_ui():
    st.markdown("""
        <style>
        .login-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: #f9f9f9;
        }
        .footer-text {
            text-align: center;
            font-size: 0.85rem;
            color: #aaa;
            margin-top: 1.5rem;
        }
        </style>
        
    """, unsafe_allow_html=True)

    st.markdown("## 🔐 Anmeldung zur Feedback-Kategorisierung")
    st.markdown("Bitte gib deinen Benutzernamen und dein Passwort ein, um fortzufahren.")

    username = st.text_input("👤 Benutzername")
    password = st.text_input("🔑 Passwort", type="password")
    login_button = st.button("🚀 Loslegen")

    if login_button:
        if check_login(username, password):
            st.session_state.logged_in = True
        else:
            st.error("❌ Falscher Benutzername oder Passwort")

    st.markdown("""<div class="footer-text">© 2025 Feedback Analyzer</div>""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_ui()
    st.stop()

# ------------------ Nach dem Login ------------------

st.title("📊 Regelbasierte Feedback-Kategorisierung")

# Sidebar – Kategorieverwaltung
st.sidebar.header("Kategorien")
st.sidebar.markdown("<style>textarea { height: 400px !important; }</style>", unsafe_allow_html=True)
kategorien = st.sidebar.text_area("(eine pro Zeile)", """
Login
TAN Probleme
App abstürze
Fehler / Bugs
Rückzahlungsoptionen
Zahlungsprobleme
Kompliziert / Unklar
Feature-Wünsche / Kritik
Sprachprobleme
Sicherheit
Tagesgeld
Werbung
UI/UX
unübersichtlich
langsam
Kundenservice
Kontaktmöglichkeiten
Vertrauenswürdigkeit
Gebühren
Sonstiges
""").splitlines()

# Regel-Editor (optional)
st.sidebar.subheader("Kategorie-Regel ergänzen")
new_keyword = st.sidebar.text_input("Schlüsselwort")
selected_category = st.sidebar.selectbox("Zielkategorie", kategorien)
if st.sidebar.button("Regel hinzufügen"):
    st.session_state.setdefault("custom_rules", {}).setdefault(selected_category, []).append(new_keyword.lower())
    st.sidebar.success(f"Regel hinzugefügt für '{selected_category}': {new_keyword}")

# Datei-Upload
uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])

# Regelbasierte Kategorisierung
@st.cache_data(show_spinner=False)
def kategorisieren_feedback(text, custom_rules):
    text = text.lower()
    rule_map = {
        "Feature-Wünsche / Kritik": ["funktion fehlt", "wäre gut", "nicht vorgesehen", "keine sofortüberweisung", "nicht verfügbar", "feature fehlt", "nicht vorhanden", "funktion sollte"],
        "Fehler / Bugs": ["funktioniert nicht", "bug", "problem", "fehler", "geht nicht", "nicht möglich", "technisch defekt", "abbruch", "bricht ab"],
        "unübersichtlich": ["übersicht", "unübersichtlich", "nicht klar", "zu viel", "durcheinander", "nicht durchblickbar", "nichts gefunden"],
        "langsam": ["langsam", "lädt", "ewig", "dauert lange", "träge", "verzögert", "hängt", "nicht geladen"],
        "Kundenservice": ["kontakt", "hotline", "rückruf", "telefon", "support", "ansprechpartner", "niemand erreichbar", "keine antwort"],
        "Rückzahlungsoptionen": ["rückzahlung", "ratenkauf", "tilgung", "zurückzahlen", "raten", "teilzahlung", "zahlungspause"],
        "Login": ["login", "einloggen", "anmeldung", "passwort", "verbindung", "login nicht möglich", "anmelden"],
        "App abstürze": ["absturz", "hängt", "schließt sich", "crasht", "app reagiert nicht", "abgestürzt"],
        "TAN Probleme": ["tan", "bestätigungscode", "sms", "code kommt nicht", "verifikation", "authentifizierung"],
        "Gebühren": ["gebühr", "zinsen", "bearbeitungsgebühr", "kosten", "preis", "nicht kostenlos"],
        "UI/UX": ["veraltet", "nicht modern", "altmodisch", "design 90er", "nicht mehr zeitgemäß", "unmodern"],
        "Kompliziert / Unklar": ["kompliziert", "nicht verständlich", "nicht intuitiv", "nicht selbsterklärend", "schwierig", "nicht erklärt"],
        "Vertrauenswürdigkeit": ["vertrauen", "abzocke", "unsicher", "zweifel", "nicht vertrauenswürdig", "datenschutz", "datenweitergabe"],
        "Sprachprobleme": ["english", "englisch", "not in german", "sprache falsch", "in englisch", "nicht auf deutsch"],
        "Werbung": ["werbung", "promo", "angebot", "rabatt", "gutschein", "aktionscode"],
        "Sicherheit": ["sicherheit", "schutz", "zugriff", "unsicher", "sicherheitsproblem", "sicherheitsbedenken", "datenleck"],
        "Tagesgeld": ["tagesgeld", "zins", "geldanlage", "sparkonto", "verzinsung", "anlage"],
        "Zahlungsprobleme": ["zahlung", "überweisung", "geld senden", "transfer", "keine buchung", "zahlung nicht möglich"],
        "Kontaktmöglichkeiten": ["ansprechpartner", "kontaktmöglichkeit", "rückruf", "keine meldung", "niemand reagiert"]
    }
    # Ergänze mit individuellen Regeln
    for k, v in custom_rules.items():
        rule_map.setdefault(k, []).extend(v)
    for kategorie, schluessel in rule_map.items():
        if any(s in text for s in schluessel):
            return kategorie
    return "Sonstiges"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'Feedback' not in df.columns:
        st.error("Die Datei benötigt eine Spalte namens 'Feedback'")
    else:
        with st.spinner("Analysiere Feedback..."):
            rules = st.session_state.get("custom_rules", {})
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: kategorisieren_feedback(x, rules))

        st.success("Analyse abgeschlossen")
        st.dataframe(df[['Feedback', 'Kategorie']])

        # Visualisierung
        st.subheader("📊 Verteilung der Kategorien")
        chart_data = df['Kategorie'].value_counts().reset_index()
        chart_data.columns = ['Kategorie', 'Anzahl']
        st.bar_chart(data=chart_data, x='Kategorie', y='Anzahl')

        # Downloads
        csv = df.to_csv(index=False).encode('utf-8')
        excel_io = pd.ExcelWriter("output.xlsx", engine="openpyxl")
        df.to_excel(excel_io, index=False, sheet_name="Kategorisiert")
        excel_io.close()

        st.download_button("📥 Download als CSV", csv, "kategorisiertes_feedback.csv", "text/csv")
        with open("output.xlsx", "rb") as f:
            st.download_button("📥 Download als Excel", f.read(), "kategorisiertes_feedback.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

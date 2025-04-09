import streamlit as st
import pandas as pd
import hashlib
import openai
import streamlit.components.v1 as components

# ------------- Benutzerverwaltung (Login) ----------------
USER_CREDENTIALS = {
    "admin2025": hashlib.sha256("admin2025".encode()).hexdigest()
}

def check_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed

# --------- Login UI im Stil der mobilen Fitness-App ----------
def show_login_ui():
    st.markdown("""
        <style>
        body {
            background-color: #f3f3f3;
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 90vh;
            background: linear-gradient(to bottom right, #8B0E47, #360033);
            border-radius: 0;
            color: white;
        }
        .login-box {
            background-color: #ffffff;
            border-radius: 1rem;
            padding: 2.5rem;
            width: 100%;
            max-width: 370px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }
        .login-box h2 {
            color: #8B0E47;
            text-align: center;
            font-weight: 800;
        }
        .stTextInput > div > div > input,
        .stPassword > div > div > input {
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: 1px solid #ddd;
        }
        .login-button button {
            background: linear-gradient(to right, #C62B50, #610061);
            color: white;
            font-weight: 600;
            width: 100%;
            margin-top: 1.5rem;
            height: 3rem;
            border-radius: 2rem;
            border: none;
            font-size: 1rem;
        }
        .footer-text {
            text-align: center;
            font-size: 0.85rem;
            color: white;
            margin-top: 2rem;
        }
        </style>
        <div class="login-container">
            <div class="login-box">
                <h2>Welcome Back</h2>
    """, unsafe_allow_html=True)

    username = st.text_input("📧 Email oder Benutzername")
    password = st.text_input("🔑 Passwort", type="password")
    login_button = st.button("SIGN IN")

    if login_button:
        if check_login(username, password):
            st.session_state.logged_in = True
        else:
            st.error("❌ Falscher Benutzername oder Passwort")

    st.markdown("""</div>
        <div class="footer-text">Noch keinen Account? <b>Registrierung auf Anfrage</b></div>
        </div>""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_ui()
    st.stop()

# ------------------ Nach dem Login ------------------

st.title("📊 Feedback Kategorisierung mit Regeln oder GPT")

# Auswahl der Methode
method = st.sidebar.selectbox("Kategorisierungsmethode", ["Regelbasiert", "GPT"])
kategorien = st.sidebar.text_area("Kategorien (eine pro Zeile)", """
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

api_key = None
if method == "GPT":
    api_key = st.sidebar.text_input("🔑 OpenAI API-Key", type="password", help="Wird nicht gespeichert")

# Datei-Upload
uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])

# Regelbasierte Kategorisierung (ausgebaut)
def kategorisieren_feedback(text):
    text = text.lower()
    if any(w in text for w in ["funktion fehlt", "wäre gut", "nicht vorgesehen", "keine sofortüberweisung"]): return "Feature-Wünsche / Kritik"
    if any(w in text for w in ["funktioniert nicht", "bug", "problem", "fehler"]): return "Fehler / Bugs"
    if any(w in text for w in ["übersicht", "unübersichtlich", "nicht klar"]): return "unübersichtlich"
    if any(w in text for w in ["langsam", "lädt", "ewig"]): return "langsam"
    if any(w in text for w in ["kontakt", "hotline", "rückruf", "telefon", "support"]): return "Kundenservice"
    if any(w in text for w in ["rückzahlung", "ratenkauf", "tilgung"]): return "Rückzahlungsoptionen"
    if any(w in text for w in ["login", "einloggen", "anmeldung"]): return "Login"
    if any(w in text for w in ["absturz", "hängt", "schließt sich"]): return "App abstürze"
    if any(w in text for w in ["tan", "bestätigungscode"]): return "TAN Probleme"
    if any(w in text for w in ["gebühr", "zinsen"]): return "Gebühren"
    if any(w in text for w in ["veraltet", "nicht modern"]): return "UI/UX"
    if any(w in text for w in ["kompliziert", "nicht verständlich"]): return "Kompliziert / Unklar"
    if any(w in text for w in ["vertrauen", "abzocke", "unsicher"]): return "Vertrauenswürdigkeit"
    if any(w in text for w in ["english", "englisch"]): return "Sprachprobleme"
    if any(w in text for w in ["werbung", "promo"]): return "Werbung"
    if any(w in text for w in ["sicherheit", "schutz"]): return "Sicherheit"
    if any(w in text for w in ["tagesgeld", "zins"]): return "Tagesgeld"
    if any(w in text for w in ["zahlung", "überweisung"]): return "Zahlungsprobleme"
    if any(w in text for w in ["ansprechpartner", "rückruf"]): return "Kontaktmöglichkeiten"
    return "Sonstiges"

# GPT-Methode
@st.cache_data(show_spinner=False)
def kategorisieren_mit_gpt(feedback, kategorien, api_key):
    openai.api_key = api_key
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Ordne das Feedback einer dieser Kategorien zu: {', '.join(kategorien)}. Feedback: '{feedback}'"}],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler: {str(e)}"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'Feedback' not in df.columns:
        st.error("Die Datei benötigt eine Spalte namens 'Feedback'")
    else:
        with st.spinner("Analysiere Feedback..."):
            if method == "Regelbasiert":
                df['Kategorie'] = df['Feedback'].astype(str).apply(kategorisieren_feedback)
            elif method == "GPT" and api_key:
                df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: kategorisieren_mit_gpt(x, kategorien, api_key))
            else:
                st.warning("Bitte gültigen API-Key eingeben")

        st.success("Analyse abgeschlossen")
        st.dataframe(df[['Feedback', 'Kategorie']])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Ergebnisse als CSV herunterladen", csv, "kategorisiertes_feedback.csv", "text/csv")

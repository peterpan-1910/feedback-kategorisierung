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

# ------------- Regelbasierte Kategorisierung (erweitert) --------------
def kategorisieren_feedback(feedback, kategorien):
    feedback = feedback.lower()

    if any(word in feedback for word in ["funktion fehlt", "es fehlt", "wäre gut", "sollte möglich sein", "keine sofortüberweisung"]):
        return "Feature-Wünsche / Kritik"
    if any(word in feedback for word in ["funktioniert nicht", "geht nicht", "abbruch", "bug", "fehler"]):
        return "Fehler / Bugs"
    if any(word in feedback for word in ["übersicht", "unübersichtlich", "struktur verwirrend"]):
        return "unübersichtlich"
    if any(word in feedback for word in ["langsam", "lädt", "ewig", "dauert lange"]):
        return "langsam"
    if any(word in feedback for word in ["kontakt", "hotline", "anruf", "nicht erreichbar", "niemand erreichbar", "support"]):
        return "Kundenservice"
    if any(word in feedback for word in ["ratenkauf", "rückzahlung", "rate", "zurückzahlen"]):
        return "Rückzahlungsoptionen"
    if any(word in feedback for word in ["login", "einloggen", "anmeldung", "logout"]):
        return "Login"
    if any(word in feedback for word in ["absturz", "app hängt", "stürzt ab"]):
        return "App abstürze"
    if any(word in feedback for word in ["tan", "sms tan", "bestätigungscode"]):
        return "TAN Probleme"
    if any(word in feedback for word in ["kosten", "gebühr", "zinsen"]):
        return "Gebühren"
    if any(word in feedback for word in ["veraltet", "nicht modern", "altmodisch"]):
        return "UI/UX"
    if any(word in feedback for word in ["kompliziert", "nicht intuitiv", "nicht verständlich", "nicht selbsterklärend"]):
        return "Kompliziert / Unklar"
    if any(word in feedback for word in ["vertrauen", "abzocke", "dubios", "nicht vertrauenswürdig"]):
        return "Vertrauenswürdigkeit"
    if any(word in feedback for word in ["english", "englisch", "not in german"]):
        return "Sprachprobleme"
    if any(word in feedback for word in ["werbung", "angebot", "promo"]):
        return "Werbung"
    if any(word in feedback for word in ["sicherheit", "sicherheitsbedenken", "schutz"]):
        return "Sicherheit"
    if any(word in feedback for word in ["tagesgeld", "zins", "geldanlage"]):
        return "Tagesgeld"
    if any(word in feedback for word in ["zahlung", "überweisung", "geld senden"]):
        return "Zahlungsprobleme"
    if any(word in feedback for word in ["ansprechpartner", "kontaktmöglichkeit", "rückruf"]):
        return "Kontaktmöglichkeiten"
    return "Sonstiges"

# ------------- GPT-Kategorisierung (optional bei API-Key) --------------
def kategorisieren_mit_gpt(feedback, kategorien, api_key):
    openai.api_key = api_key
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
        Du bist ein System zur Textklassifikation. Ordne das folgende deutsche Kundenfeedback genau einer dieser Kategorien zu:
        {', '.join(kategorien)}.
        Feedback: \"{feedback}\"
        Antworte nur mit der Kategorie (ohne weitere Erklärungen).
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler: {str(e)}"

# ----------------- Streamlit App -------------------
def main():
    st.set_page_config(page_title="Feedback Analyse", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("""
            <style>
                .main {background-color: #0f1117; color: #ffffff;}
                .stTextInput > div > div > input {
                    background-color: #1e1e2f;
                    color: white;
                }
                .stTextInput > label, .stPassword > label {
                    color: #ffffff;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("# ✨ Willkommen zur KI-gestützten Feedbackanalyse")
        st.markdown("Bitte logge dich ein, um loszulegen.")

        username = st.text_input("👤 Benutzername")
        password = st.text_input("🔐 Passwort", type="password")
        login_button = st.button("🚪 Login")

        if login_button:
            if check_login(username, password):
                st.session_state.logged_in = True
            else:
                st.error("Falscher Benutzername oder Passwort")
        return

    # Nach Login
    st.markdown("## 📊 Feedback Kategorisierung auf Basis von GPT oder Regeln")

    st.sidebar.header("⚙️ Kategorien verwalten")
    default_kategorien = [
        "Login", "TAN Probleme", "App abstürze", "Fehler / Bugs",
        "Rückzahlungsoptionen", "Zahlungsprobleme", "Kompliziert / Unklar",
        "Feature-Wünsche / Kritik", "Sprachprobleme", "Sicherheit", "Tagesgeld",
        "Werbung", "UI/UX", "unübersichtlich", "langsam", "Kundenservice",
        "Kontaktmöglichkeiten", "Vertrauenswürdigkeit", "Gebühren", "Sonstiges"
    ]

    kategorien = st.sidebar.text_area("Kategorien (eine pro Zeile)", "\n".join(default_kategorien)).splitlines()

    st.sidebar.markdown("---")
    method = st.sidebar.selectbox("Kategorisierungsmethode", ["GPT", "Regelbasiert"])
    api_key = None
    if method == "GPT":
        api_key = st.sidebar.text_input("🔑 OpenAI API-Key", type="password", key="api", help="Dein OpenAI-Schlüssel wird nicht gespeichert")

    uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'Feedback' not in df.columns:
            st.error("Die Excel-Datei muss eine Spalte 'Feedback' enthalten.")
            return

        kategorien_clean = [k.strip() for k in kategorien if k.strip() != ""]

        if method == "GPT" and api_key:
            st.info("Kategorisierung läuft. Bitte etwas Geduld...")
            progress_bar = st.progress(0)
            kategorien_list = []
            for i, feedback in enumerate(df['Feedback']):
                kategorie = kategorisieren_mit_gpt(str(feedback), kategorien_clean, api_key)
                kategorien_list.append(kategorie)
                progress_bar.progress((i + 1) / len(df))
            df['Kategorie'] = kategorien_list
        else:
            df['Kategorie'] = df['Feedback'].apply(lambda x: kategorisieren_feedback(str(x), kategorien_clean))

        st.success("Kategorisierung abgeschlossen!")
        st.dataframe(df[['Feedback', 'Kategorie']])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Ergebnisse als CSV herunterladen", csv, "kategorisiertes_feedback.csv", "text/csv")

if __name__ == '__main__':
    main()

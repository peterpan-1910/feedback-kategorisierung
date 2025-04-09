import streamlit as st
import pandas as pd
import hashlib
import openai

# ------------- Benutzerverwaltung (Login) ----------------
USER_CREDENTIALS = {
    "admin2025": hashlib.sha256("admin2025".encode()).hexdigest()
}

def check_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed

# ------------- GPT-Kategorisierung (neue API Version >=1.0.0) ----------------
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

# ------------- Regelbasierte Kategorisierung (Fallback) --------------
def kategorisieren_feedback(feedback, kategorien):
    feedback = feedback.lower()
    for kat in kategorien:
        if kat.lower() in feedback:
            return kat
    if "funktion" in feedback and ("nicht vorhanden" in feedback or "fehlt"):
        return "Feature-Wünsche / Kritik"
    elif "nicht funktioniert" in feedback or "geht nicht" in feedback:
        return "Fehler / Bugs"
    elif "übersicht" in feedback or "unübersichtlich" in feedback:
        return "unübersichtlich"
    elif "langsam" in feedback or "ewig" in feedback:
        return "langsam"
    elif "kontakt" in feedback or "niemand erreichbar" in feedback:
        return "Kundenservice"
    elif "ratenkauf" in feedback or "rückzahlung" in feedback:
        return "Rückzahlungsoptionen"
    elif "login" in feedback or "einloggen" in feedback:
        return "Login"
    elif "absturz" in feedback or "hängt" in feedback:
        return "App abstürze"
    elif "english" in feedback:
        return "Nicht-deutsch"
    return "Sonstiges"

# ----------------- Streamlit App -------------------
def main():
    st.title("📊 Kundenfeedback-Kategorisierung")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        login_button = st.button("Login")

        if login_button:
            if check_login(username, password):
                st.session_state.logged_in = True
            else:
                st.error("Falscher Benutzername oder Passwort")
        return

    # Nach Login
    st.success("Eingeloggt")

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
        api_key = st.sidebar.text_input("🔑 OpenAI API-Key", type="password")

    uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'Feedback' not in df.columns:
            st.error("Die Excel-Datei muss eine Spalte 'Feedback' enthalten.")
            return

        kategorien_clean = [k.strip() for k in kategorien if k.strip() != ""]

        if method == "GPT" and api_key:
            df['Kategorie'] = df['Feedback'].apply(lambda x: kategorisieren_mit_gpt(str(x), kategorien_clean, api_key))
        else:
            df['Kategorie'] = df['Feedback'].apply(lambda x: kategorisieren_feedback(str(x), kategorien_clean))

        st.success("Kategorisierung abgeschlossen!")
        st.dataframe(df[['Feedback', 'Kategorie']])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Ergebnisse als CSV herunterladen", csv, "kategorisiertes_feedback.csv", "text/csv")

if __name__ == '__main__':
    main()

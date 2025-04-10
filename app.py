import streamlit as st
import pandas as pd
import hashlib
import json
import os

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

    st.markdown("""<div class="footer-text">© 2025 Feedback Analyzer<br>Version 1.0.0</div>""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_ui()
    st.stop()

# ------------------ Nach dem Login ------------------

st.title("📊 Regelbasierte Feedback-Kategorisierung")

# ------------------ Kategorien & Regelverwaltung ------------------

st.subheader("🗂️ Kategorien und zugehörige Schlüsselwörter")
rules_file = "custom_rules.json"
if os.path.exists(rules_file):
    with open(rules_file, "r") as f:
        all_rules = json.load(f)
else:
    all_rules = {}

for cat, terms in sorted(all_rules.items()):
    with st.expander(f"📁 {cat} ({len(terms)} Begriffe)", expanded=False):
        updated_terms = []
        for term in sorted(set(terms)):
            col1, col2, col3 = st.columns([4, 1, 1])
            new_term = col1.text_input("", value=term, key=f"edit_{cat}_{term}")
            if new_term != term:
                updated_terms.append(new_term.lower())
            else:
                updated_terms.append(term)
            if col2.button("↩️", key=f"reset_{cat}_{term}"):
                updated_terms.append(term)
            if col3.button("❌", key=f"delete_{cat}_{term}"):
                terms.remove(term)
        all_rules[cat] = list(set(updated_terms))
        with open(rules_file, "w") as f:
            json.dump(all_rules, f, indent=2)

st.markdown("---")

# Regel hinzufügen
st.subheader("➕ Neue Regel hinzufügen")
new_keyword = st.text_input("🔤 Schlüsselwort")
selected_category = st.selectbox("📌 Zielkategorie", sorted(all_rules.keys())) if all_rules else st.text_input("📌 Neue Kategorie")
if st.button("✅ Regel speichern") and new_keyword:
    all_rules.setdefault(selected_category, []).append(new_keyword.lower())
    with open(rules_file, "w") as f:
        json.dump(all_rules, f, indent=2)
    st.success(f"Regel gespeichert für '{selected_category}': {new_keyword}")
    st.experimental_rerun()

# ------------------ Datei-Upload und Kategorisierung ------------------

uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])

@st.cache_data(show_spinner=False)
def kategorisieren_feedback(text, rule_map):
    text = text.lower()
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
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: kategorisieren_feedback(x, all_rules))

        st.success("Analyse abgeschlossen")
        st.dataframe(df[['Feedback', 'Kategorie']])

        # Visualisierung
        st.subheader("📊 Verteilung der Kategorien")
        chart_data = df['Kategorie'].value_counts(normalize=True).reset_index()
        chart_data.columns = ['Kategorie', 'Anteil']
        chart_data['Anteil'] = chart_data['Anteil'] * 100

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, len(chart_data) * 0.4))
        chart_data_sorted = chart_data.sort_values(by="Anteil")
        ax.barh(chart_data_sorted['Kategorie'], chart_data_sorted['Anteil'])
        ax.set_xlabel("Anteil (%)")
        ax.set_ylabel("Kategorie")
        ax.set_title("Verteilung der Kategorien")
        for i, v in enumerate(chart_data_sorted['Anteil']):
            ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
        st.pyplot(fig)

        # Downloads
        csv = df.to_csv(index=False).encode('utf-8')
        excel_io = pd.ExcelWriter("output.xlsx", engine="openpyxl")
        df.to_excel(excel_io, index=False, sheet_name="Kategorisiert")
        excel_io.close()

        st.download_button("📥 Download als CSV", csv, "kategorisiertes_feedback.csv", "text/csv")
        with open("output.xlsx", "rb") as f:
            st.download_button("📥 Download als Excel", f.read(), "kategorisiertes_feedback.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

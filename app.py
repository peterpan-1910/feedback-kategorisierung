import streamlit as st
import pandas as pd
import hashlib
import json
import os
import re
import datetime

# ------------------ Hilfsfunktionen ------------------
@st.cache_data(show_spinner=False)
def kategorisieren_feedback(text, rule_map):
    text = text.lower()
    for kategorie, schluessel in rule_map.items():
        if any(s in text for s in schluessel):
            return kategorie
    return "Sonstiges"

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
            st.rerun()
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
menu = st.sidebar.radio("Navigiere zu", ["Analyse", "Regeln lernen"])

# ------------------ Kategorien & Regelverwaltung ------------------

rules_file = "custom_rules.json"
if os.path.exists(rules_file):
    with open(rules_file, "r") as f:
        all_rules = json.load(f)
else:
    all_rules = {}

st.markdown("## 🧠 Kategorien-Übersicht")
with st.expander("📚 Aktive Kategorien & Anzahl der Keywords", expanded=False):
    if all_rules:
        for k in sorted(all_rules.keys()):
            st.markdown(f"- **{k}**: {len(all_rules[k])} Begriffe")
    else:
        st.info("Noch keine Kategorien vorhanden.")

st.subheader("🗂️ Kategorien und zugehörige Schlüsselwörter")
changes_detected = False
for cat, terms in sorted(all_rules.items()):
    terms = list(set(terms))
    with st.expander(f"📁 {cat} ({len(terms)} Begriffe)", expanded=False):
        updated_terms = []
        for i, term in enumerate(sorted(set(terms))):
            col1, col2, col3 = st.columns([4, 1, 1])
            new_term = col1.text_input("", value=term, key=f"edit_{cat}_{term}_{i}")
            if new_term != term:
                updated_terms.append(new_term.lower())
                changes_detected = True
            else:
                updated_terms.append(term)
            if col2.button("↩️", key=f"reset_{cat}_{term}_{i}"):
                updated_terms.append(term)
                changes_detected = True
            if col3.button("❌", key=f"delete_{cat}_{term}_{i}"):
                terms.remove(term)
                changes_detected = True
        all_rules[cat] = list(set(updated_terms))

if changes_detected:
    with open(rules_file, "w") as f:
        json.dump(all_rules, f, indent=2)

st.markdown("---")

st.subheader("➕ Neue Regel hinzufügen")
new_keyword = st.text_input("🔤 Schlüsselwort")
selected_category = st.selectbox("📌 Zielkategorie", sorted(all_rules.keys())) if all_rules else st.text_input("📌 Neue Kategorie")
if st.button("✅ Regel speichern") and new_keyword:
    all_rules.setdefault(selected_category, []).append(new_keyword.lower())
    with open(rules_file, "w") as f:
        json.dump(all_rules, f, indent=2)
    st.success(f"Regel gespeichert für '{selected_category}': {new_keyword}")
    st.rerun()

# ------------------ Regel-Lernen ------------------

if menu == "Regeln lernen":
    st.subheader("🧠 Vorschläge für neue Regeln aus Feedback")
    uploaded_learn_file = st.file_uploader("📤 Excel-Datei hochladen (enthält Spalte 'Feedback')", type=["xlsx"], key="learn")

    if uploaded_learn_file:
        df_learn = pd.read_excel(uploaded_learn_file)
        if 'Feedback' not in df_learn.columns:
            st.error("Die Datei muss eine Spalte namens 'Feedback' enthalten.")
            st.stop()

        unmatched_words = {}
        for feedback in df_learn['Feedback'].astype(str):
            text = feedback.lower()
            if kategorisieren_feedback(text, all_rules) == "Sonstiges":
                for word in re.findall(r'\b\w{4,}\b', text):
                    unmatched_words[word] = unmatched_words.get(word, 0) + 1

        suggestions = sorted(unmatched_words.items(), key=lambda x: x[1], reverse=True)[:30]
        st.markdown("### 🔍 Häufige unbekannte Wörter aus 'Sonstiges'")
        for word, count in suggestions:
            col1, col2 = st.columns([3, 2])
            col1.write(f"{word} ({count}x)")

            from difflib import get_close_matches
            flat_terms = {cat: term for cat, terms in all_rules.items() for term in terms}
            term_matches = get_close_matches(word, flat_terms.values(), n=1, cutoff=0.6)
            best_term = term_matches[0] if term_matches else None
            term_category = next((cat for cat, term in flat_terms.items() if term == best_term), None)
            cat_matches = get_close_matches(word, all_rules.keys(), n=1, cutoff=0.4)
            category_suggestion = term_category if term_category else (cat_matches[0] if cat_matches else "Ignorieren")

            default_index = (sorted(all_rules.keys()).index(category_suggestion) + 1) if category_suggestion in all_rules else 0

            selected = col2.selectbox("Kategorie zuweisen", ["Ignorieren"] + sorted(all_rules.keys()), index=default_index, key=f"assign_{word}")

            if selected != "Ignorieren":
                all_rules[selected].append(word)
                with open("rule_log.csv", "a", encoding="utf-8") as log:
                    log.write(f"{datetime.datetime.now().isoformat()};{word};{selected}\n")
                with open(rules_file, "w") as f:
                    json.dump(all_rules, f, indent=2)
                st.success(f"'{word}' wurde der Kategorie '{selected}' hinzugefügt")
                st.rerun()

    if os.path.exists("rule_log.csv"):
        with open("rule_log.csv", "rb") as log_file:
            st.download_button("📥 Log als CSV herunterladen", log_file, file_name="regel_log.csv", mime="text/csv")

        df_log = pd.read_csv("rule_log.csv", sep=";")
        excel_log_path = "regel_log.xlsx"
        df_log.to_excel(excel_log_path, index=False)
        with open(excel_log_path, "rb") as xl_file:
            st.download_button("📥 Log als Excel herunterladen", xl_file, file_name="regel_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.stop()

# ------------------ Datei-Upload und Kategorisierung ------------------

uploaded_file = st.file_uploader("📤 Excel-Datei mit Feedback hochladen", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'Feedback' not in df.columns:
        st.error("Die Datei benötigt eine Spalte namens 'Feedback'")
    else:
        with st.spinner("Analysiere Feedback..."):
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: kategorisieren_feedback(x, all_rules))

        st.success("Analyse abgeschlossen")
        st.dataframe(df[['Feedback', 'Kategorie']])

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

        csv = df.to_csv(index=False).encode('utf-8')
        excel_io = pd.ExcelWriter("output.xlsx", engine="openpyxl")
        df.to_excel(excel_io, index=False, sheet_name="Kategorisiert")
        excel_io.close()

        st.download_button("📥 Download als CSV", csv, "kategorisiertes_feedback.csv", "text/csv")
        with open("output.xlsx", "rb") as f:
            st.download_button("📥 Download als Excel", f.read(), "kategorisiertes_feedback.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime
import hashlib
import re
import io
from pathlib import Path
from difflib import get_close_matches

# --- Konfiguration ---
BASE_DIR = Path(__file__).parent
RULES_PATH = BASE_DIR / "data" / "custom_rules.json"
LOG_PATH = BASE_DIR / "data" / "rule_log.csv"

# --- Default-Regeln (Original-Kategorien & Keywords) ---
DEFAULT_RULES: dict[str, list[str]] = {
    "Login": [
        # ... Keywords ...
    ],
    # ... Weitere Kategorien ...
}

# --- Authentifizierung ---
creds = st.secrets.get("credentials", {})
_USERS = {}
if creds.get("username") and creds.get("password_hash"):
    _USERS = {creds["username"]: creds["password_hash"]}
else:
    default_user = "admin2025"
    default_hash = hashlib.sha256("data2025".encode()).hexdigest()
    _USERS = {default_user: default_hash}

def login(username: str, password: str) -> bool:
    return _USERS.get(username) == hashlib.sha256(password.encode()).hexdigest()

# --- Regelverwaltung ---
@st.cache_data(show_spinner=False)
def load_rules() -> dict[str, list[str]]:
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    for cat, terms in DEFAULT_RULES.items():
        data.setdefault(cat, terms.copy())
    return data

@st.cache_data(show_spinner=False)
def save_rules(rules: dict[str, list[str]]) -> None:
    RULES_PATH.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")

# --- Kategorisierer ---
@st.cache_data(show_spinner=False)
def build_pattern_map(rules: dict[str, list[str]]) -> dict[str, re.Pattern]:
    patterns = {}
    for cat, terms in rules.items():
        if terms:
            esc = [re.escape(t) for t in set(terms)]
            patterns[cat] = re.compile(r"\b(?:%s)\b" % "|".join(esc), re.IGNORECASE)
    return patterns

@st.cache_data(show_spinner=False)
def categorize(text: str, patterns: dict[str, re.Pattern]) -> str:
    for cat, pat in patterns.items():
        if pat.search(text):
            return cat
    return "Sonstiges"

# --- UI-Komponenten ---
def show_login() -> bool:
    user = st.text_input("Benutzername", key="user_input")
    pwd = st.text_input("Passwort", type="password", key="pwd_input")
    if st.button("Loslegen"):
        if login(user, pwd):
            st.session_state.authenticated = True
            return True
        st.error("Falsche Anmeldedaten")
    return False

def sidebar_menu(options: list[str]) -> str:
    return st.sidebar.radio("Navigation", options)

# --- Hauptprogramm ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    if show_login():
        st.experimental_rerun()
    else:
        st.stop()

rules = load_rules()
patterns = build_pattern_map(rules)
mode = sidebar_menu(["Analyse", "Regeln verwalten", "Regeln lernen"])

# --- Analyse ---
if mode == "Analyse":
    st.title("📊 Feedback-Kategorisierung")
    uploaded = st.file_uploader("Excel upload (Spalte 'Feedback')", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        if 'Feedback' in df.columns:
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: categorize(x, patterns))
            st.dataframe(df[['Feedback','Kategorie']])
            counts = df['Kategorie'].value_counts(normalize=True).mul(100)
            fig, ax = plt.subplots()
            counts.sort_values().plot.barh(ax=ax)
            ax.set_xlabel("Anteil (%)")
            st.pyplot(fig)
            # CSV Download
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name="feedback.csv",
                mime="text/csv"
            )
            # Excel Download via BytesIO
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Kategorien")
                writer.save()
            towrite.seek(0)
            st.download_button(
                label="Download Excel",
                data=towrite,
                file_name="feedback.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Die Datei benötigt eine Spalte 'Feedback'.")

# --- Regeln verwalten ---
elif mode == "Regeln verwalten":
    st.title("🔧 Regeln verwalten")
    # Bestehende Keywords pro Kategorie editierbar mit Lösch-Option
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            updated_terms = []
            for term in rules[cat]:
                col1, col2 = st.columns([4, 1])
                new_term = col1.text_input("", value=term, key=f"edit_{cat}_{term}")
                if col2.button("❌ Entfernen", key=f"del_{cat}_{term}"):
                    continue
                updated_terms.append(new_term)
            rules[cat] = updated_terms
    st.markdown("---")
    # Neues Keyword hinzufügen
    st.subheader("➕ Neues Schlüsselwort hinzufügen")
    selected_category = st.selectbox("Kategorie auswählen", sorted(rules.keys()), key="new_sel_cat")
    new_kw = st.text_input("Neues Schlüsselwort", key="new_keyword")
    if st.button("Hinzufügen", key="add_keyword_btn") and new_kw:
        rules[selected_category].append(new_kw)
        save_rules(rules)
        st.success(f"Keyword '{new_kw}' wurde der Kategorie '{selected_category}' hinzugefügt.")
        st.experimental_rerun()
elif mode == "Regeln lernen":
    st.title("🧠 Regeln lernen")
    uploaded_learn = st.file_uploader("Feedback Excel (Spalte 'Feedback')", type=["xlsx"], key="learn")
    if uploaded_learn:
        df_learn = pd.read_excel(uploaded_learn)
        if 'Feedback' not in df_learn.columns:
            st.error("Die Datei benötigt eine Spalte 'Feedback'.")
        else:
            unmatched = {}
            for fb in df_learn['Feedback'].astype(str):
                if categorize(fb.lower(), patterns) == "Sonstiges":
                    for w in re.findall(r"\w{4,}", fb.lower()): unmatched[w] = unmatched.get(w,0)+1
            suggestions = sorted(unmatched.items(), key=lambda x: x[1], reverse=True)[:30]
            st.subheader("Vorschläge für neue Keywords aus 'Sonstiges' (Top 30)")
            for word, cnt in suggestions:
                cols = st.columns([4,2])
                cols[0].write(f"{word} ({cnt}x)")
                choice = cols[1].selectbox("Kategorie", ["Ignorieren"]+sorted(rules.keys()), key=word)
                if choice != "Ignorieren":
                    rules.setdefault(choice, []).append(word)
                    with open(LOG_PATH,'a',encoding='utf-8') as logf:
                        logf.write(f"{datetime.datetime.now().isoformat()};{word};{choice}\n")
                    save_rules(rules)
                    st.success(f"'{word}' wurde zu '{choice}' hinzugefügt.")
                    st.experimental_rerun()

# --- Persistenz am Ende ---
save_rules(rules)

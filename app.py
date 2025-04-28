import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime
import hashlib
import re
from pathlib import Path
from difflib import get_close_matches

# Konfiguration
BASE_DIR = Path(__file__).parent
RULES_PATH = BASE_DIR / "data" / "custom_rules.json"
LOG_PATH = BASE_DIR / "data" / "rule_log.csv"

# Authentifizierung
creds = st.secrets.get("credentials", {})
_USERS = {}
if creds.get("username") and creds.get("password_hash"):
    _USERS = {creds["username"]: creds["password_hash"]}

def login(username: str, password: str) -> bool:
    return _USERS.get(username) == hashlib.sha256(password.encode()).hexdigest()

# Regelverwaltung
@st.cache_data(show_spinner=False)
def load_rules() -> dict[str, list[str]]:
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps({}, indent=2), encoding="utf-8")
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))

@st.cache_data(show_spinner=False)
def save_rules(rules: dict[str, list[str]]) -> None:
    RULES_PATH.write_text(json.dumps(rules, indent=2), encoding="utf-8")

# Kategorisierer
@st.cache_data(show_spinner=False)
def build_pattern_map(rules: dict[str, list[str]]) -> dict[str, re.Pattern]:
    patterns: dict[str, re.Pattern] = {}
    for cat, terms in rules.items():
        if not terms:
            continue
        escaped = [re.escape(t) for t in set(terms)]
        patterns[cat] = re.compile(r"\b(?:%s)\b" % "|".join(escaped), re.IGNORECASE)
    return patterns

@st.cache_data(show_spinner=False)
def categorize(text: str, patterns: dict[str, re.Pattern]) -> str:
    for cat, pat in patterns.items():
        if pat.search(text):
            return cat
    return "Sonstiges"

# UI-Komponenten
def show_login():
    st.markdown("## 🔐 Anmeldung")
    st.text_input("Benutzername", key="user_input")
    st.text_input("Passwort", type="password", key="pwd_input")
    if st.button("Loslegen"):
        if login(st.session_state.user_input, st.session_state.pwd_input):
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Falsche Anmeldedaten")

def sidebar_menu(options: list[str]) -> str:
    return st.sidebar.radio("Navigation", options)

# Hauptprogramm
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    show_login()
    st.stop()

rules = load_rules()
patterns = build_pattern_map(rules)
mode = sidebar_menu(["Analyse", "Regeln verwalten", "Regeln lernen"])

if mode == "Analyse":
    st.title("📊 Feedback-Kategorisierung")
    uploaded = st.file_uploader("Excel hochladen", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        if 'Feedback' in df.columns:
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda x: categorize(x, patterns))
            st.dataframe(df)
            counts = df['Kategorie'].value_counts(normalize=True).mul(100)
            fig, ax = plt.subplots()
            counts.sort_values().plot.barh(ax=ax)
            ax.set_xlabel("Anteil (%)")
            st.pyplot(fig)
            st.download_button("Als CSV", df.to_csv(index=False), "feedback.csv")
            st.download_button("Als Excel", df.to_excel(index=False, sheet_name="Kategorien"), "feedback.xlsx")
        else:
            st.error("Spalte 'Feedback' fehlt.")

elif mode == "Regeln verwalten":
    st.title("🔧 Regeln verwalten")
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            edited = st.text_area("Keywords (Komma-separiert)", value=", ".join(rules[cat]), key=cat)
            rules[cat] = [k.strip().lower() for k in edited.split(",") if k.strip()]
    st.markdown("---")
    new_cat = st.text_input("Neue Kategorie")
    new_kw = st.text_input("Neues Keyword")
    if st.button("Hinzufügen") and new_cat and new_kw:
        rules.setdefault(new_cat, []).append(new_kw.lower())
        save_rules(rules)
        st.experimental_rerun()

elif mode == "Regeln lernen":
    st.title("🧠 Regeln lernen")
    uploaded_learn = st.file_uploader("Feedback-Excel (Spalte 'Feedback')", type=["xlsx"], key="learn")
    if uploaded_learn:
        df_learn = pd.read_excel(uploaded_learn)
        if 'Feedback' not in df_learn.columns:
            st.error("Spalte 'Feedback' fehlt.")
            st.stop()
        unmatched: dict[str, int] = {}
        for fb in df_learn['Feedback'].astype(str):
            if categorize(fb.lower(), patterns) == "Sonstiges":
                for w in fb.split():
                    if len(w) > 3:
                        unmatched[w] = unmatched.get(w, 0) + 1
        suggestions = sorted(unmatched.items(), key=lambda x: x[1], reverse=True)[:30]
        st.subheader("🔍 Unbekannte Wörter")
        for word, cnt in suggestions:
            cols = st.columns([3, 2])
            cols[0].write(f"{word} ({cnt}x)")
            sel = cols[1].selectbox("Kategorie", ["Ignorieren"] + sorted(rules.keys()), key=word)
            if sel != "Ignorieren":
                rules.setdefault(sel, []).append(word)
                with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"{datetime.datetime.now().isoformat()};{word};{sel}\n")
                save_rules(rules)
                st.experimental_rerun()

# Regeln speichern
save_rules(rules)

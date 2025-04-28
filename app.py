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

# --- Konfiguration & Caching ---
# Default-Regeln aus JSON; Initial befüllt über existing custom_rules.json
DEFAULT_RULES: dict[str, list[str]] = {}

BASE_DIR = Path(__file__).parent
RULES_PATH = BASE_DIR / "data" / "custom_rules.json"
LOG_PATH = BASE_DIR / "data" / "rule_log.csv"

@st.cache_data(show_spinner=False)
def init_users():
    creds = st.secrets.get("credentials", {})
    if creds.get("username") and creds.get("password_hash"):
        return {creds["username"]: creds["password_hash"]}
    return {"admin2025": hashlib.sha256("data2025".encode()).hexdigest()}

@st.cache_data(show_spinner=False)
def load_rules():
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    for cat, terms in DEFAULT_RULES.items(): data.setdefault(cat, terms.copy())
    return data

@st.cache_data(show_spinner=False)
def build_patterns(rules):
    pats = {}
    for cat, terms in rules.items():
        if terms:
            escaped = [re.escape(t) for t in terms]
            pats[cat] = re.compile(r"\b(?:%s)\b" % "|".join(escaped), re.IGNORECASE)
    return pats

# For fast categorization: return vectorized series
@st.cache_data(show_spinner=False)
def categorize_series(feedback_series, patterns):
    df = pd.DataFrame({ 'Feedback': feedback_series })
    df['Kategorie'] = 'Sonstiges'
    for cat, pat in patterns.items():
        mask = df['Feedback'].str.contains(pat)
        df.loc[mask & (df['Kategorie'] == 'Sonstiges'), 'Kategorie'] = cat
    return df['Kategorie']

def save_rules(rules):
    RULES_PATH.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
    # Clear memoized caches
    load_rules.clear()
    build_patterns.clear()

# --- Authentifizierung ---
_USERS = init_users()

def login(user: str, pwd: str) -> bool:
    return _USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest()

# --- UI: Login ---
def show_login():
    st.markdown("<h1 style='text-align:center;'>🔐 Login</h1>", unsafe_allow_html=True)
    user = st.text_input("👤 Benutzername", key="user_input")
    pwd = st.text_input("🔑 Passwort", type="password", key="pwd_input")
    if st.button("🚀 Anmelden"):
        if login(user, pwd):
            st.session_state.authenticated = True
        else:
            st.error("❌ Ungültige Anmeldedaten")

# --- Main ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    show_login()
    st.stop()

# --- Flow: Modus-Auswahl ---
rules = load_rules()
patterns = build_patterns(rules)
mode = st.sidebar.radio("Modus", ["Analyse", "Regeln verwalten", "Regeln lernen"])

# --- Analyse ---
if mode == "Analyse":
    st.title("📊 Feedback-Kategorisierung")
    uploaded = st.file_uploader("Excel-Datei (Spalte 'Feedback')", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        if 'Feedback' in df.columns:
            df['Kategorie'] = categorize_series(df['Feedback'].astype(str), patterns)
            st.dataframe(df[['Feedback', 'Kategorie']])
            counts = df['Kategorie'].value_counts(normalize=True).mul(100)
            fig, ax = plt.subplots()
            counts.sort_values().plot.barh(ax=ax)
            ax.set_xlabel("Anteil (%)")
            st.pyplot(fig)
            # Downloads
            st.download_button("Download CSV", df.to_csv(index=False), "feedback.csv", "text/csv")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Kategorien")
            buf.seek(0)
            st.download_button("Download Excel", buf, "feedback.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("Spalte 'Feedback' nicht gefunden.")

# --- Regeln verwalten ---
elif mode == "Regeln verwalten":
    st.title("🔧 Regeln verwalten")
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            updated = []
            for term in rules[cat]:
                cols = st.columns([4,1])
                new = cols[0].text_input("", value=term, key=f"edit_{cat}_{term}")
                remove = cols[1].checkbox("❌", key=f"rem_{cat}_{term}")
                if not remove:
                    updated.append(new)
            rules[cat] = updated
    st.markdown("---")
    st.subheader("➕ Neues Keyword hinzufügen")
    tgt = st.selectbox("Kategorie auswählen", sorted(rules.keys()), key="new_cat")
    new_kw = st.text_input("Neues Keyword", key="new_kw")
    if st.button("Hinzufügen") and new_kw:
        rules[tgt].append(new_kw)
        save_rules(rules)
        st.success(f"'{new_kw}' wurde zu '{tgt}' hinzugefügt.")

# --- Regeln lernen ---
elif mode == "Regeln lernen":
    st.title("🧠 Regeln lernen")
    uploaded = st.file_uploader("Excel (Spalte 'Feedback')", type=["xlsx"], key="learn")
    if uploaded:
        df = pd.read_excel(uploaded)
        if 'Feedback' in df.columns:
            unmatched = {}
            for fb in df['Feedback'].astype(str):
                if categorize(fb.lower(), patterns) == "Sonstiges":
                    for w in re.findall(r"\w{4,}", fb.lower()):
                        unmatched[w] = unmatched.get(w, 0) + 1
            suggestions = sorted(unmatched.items(), key=lambda x: x[1], reverse=True)[:30]
            st.subheader("Vorschläge für neue Keywords aus 'Sonstiges'")
            for word, cnt in suggestions:
                cols = st.columns([4, 2])
                cols[0].write(f"{word} ({cnt}x)")
                choice = cols[1].selectbox("Kategorie", ["Ignorieren"] + sorted(rules.keys()), key=word)
                if choice != "Ignorieren":
                    rules.setdefault(choice, []).append(word)
                    with open(LOG_PATH, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now().isoformat()};{word};{choice}\n")
                    save_rules(rules)
                    st.success(f"'{word}' wurde zu '{choice}' hinzugefügt.")

# --- Persistenz ---
save_rules(rules)

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

# --- Default-Regeln ---
DEFAULT_RULES = {
    # Hier vollständige Kategorien & Keywords einfügen
}

# --- Authentifizierung ---
def init_users():
    creds = st.secrets.get("credentials", {})
    if creds.get("username") and creds.get("password_hash"):
        return {creds["username"]: creds["password_hash"]}
    return {"admin2025": hashlib.sha256("data2025".encode()).hexdigest()}

_USERS = init_users()

def login(user: str, pwd: str) -> bool:
    return _USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest()

# --- Regeln laden/speichern ---
@st.cache_data
def load_rules():
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    for cat, terms in DEFAULT_RULES.items(): data.setdefault(cat, terms.copy())
    return data

@st.cache_data
def save_rules(rules):
    RULES_PATH.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")

# --- Kategorisierung ---
@st.cache_data
def build_patterns(rules):
    pats = {}
    for cat, terms in rules.items():
        if terms:
            esc = [re.escape(t) for t in terms]
            pats[cat] = re.compile(r"\b(?:%s)\b" % "|".join(esc), re.IGNORECASE)
    return pats

@st.cache_data
def categorize(text, pats):
    for cat, pat in pats.items():
        if pat.search(text): return cat
    return "Sonstiges"

# --- UI: Login ---
def show_login():
    st.markdown("<div style='text-align:center;'><h1>🔐 Login</h1></div>", unsafe_allow_html=True)
    user = st.text_input("👤 User", key="user_input")
    pwd = st.text_input("🔑 Pass", type="password", key="pwd_input")
    if st.button("🚀 Login"):
        if login(user, pwd):
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

# --- Main ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    show_login()
    st.stop()

# --- Flow: Modus-Auswahl ---
rules = load_rules()
patterns = build_patterns(rules)
mode = st.sidebar.radio("Modus", ["Analyse", "Regeln verwalten", "Regeln lernen"] )

# --- Analyse ---
if mode == "Analyse":
    st.title("📊 Analyse")
    uploaded = st.file_uploader("Excel (Spalte 'Feedback')", type=["xlsx"])
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
            st.download_button("Download CSV", df.to_csv(index=False), "feedback.csv", "text/csv")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Kategorien")
            buf.seek(0)
            st.download_button("Download Excel", buf, "feedback.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("Spalte 'Feedback' fehlt.")

# --- Regeln verwalten ---
elif mode == "Regeln verwalten":
    st.title("🔧 Regeln verwalten")
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            updated = []
            for i, term in enumerate(rules[cat]):
                c1, c2 = st.columns([4,1])
                new = c1.text_input("", value=term, key=f"edit_{cat}_{i}")
                if not c2.button("❌", key=f"del_{cat}_{i}"):
                    updated.append(new)
            rules[cat] = updated
    st.markdown("---")
    st.subheader("➕ Neues Keyword hinzufügen")
    tgt = st.selectbox("Kategorie", sorted(rules.keys()), key="new_cat")
    new_kw = st.text_input("Keyword", key="new_kw")
    if st.button("Hinzufügen", key="add_kw") and new_kw:
        rules[tgt].append(new_kw)
        save_rules(rules)
        st.success(f"'{new_kw}' zu '{tgt}' hinzugefügt.")
        st.experimental_rerun()

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
                    for w in re.findall(r"\w{4,}", fb.lower()): unmatched[w] = unmatched.get(w,0)+1
            for w, cnt in sorted(unmatched.items(), key=lambda x:-x[1])[:30]:
                cols = st.columns([4,2])
                cols[0].write(f"{w} ({cnt}x)")
                choice = cols[1].selectbox("Kategorie", ["Ignorieren"]+sorted(rules.keys()), key=w)
                if choice != "Ignorieren":
                    rules.setdefault(choice, []).append(w)
                    with open(LOG_PATH, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now().isoformat()};{w};{choice}\n")
                    save_rules(rules)
                    st.success(f"'{w}' zu '{choice}' hinzugefügt.")
                    st.experimental_rerun()

# --- Persistenz ---
save_rules(rules)

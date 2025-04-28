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
    # Alle Kategorien mit Keywords hier einfügen
}

# --- Authentifizierung ---
def init_users():
    creds = st.secrets.get("credentials", {})
    if creds.get("username") and creds.get("password_hash"):
        return {creds["username"]: creds["password_hash"]}
    # Default
    return {"admin2025": hashlib.sha256("data2025".encode()).hexdigest()}

_USERS = init_users()

def login(username: str, password: str) -> bool:
    return _USERS.get(username) == hashlib.sha256(password.encode()).hexdigest()

# --- Regeln laden/speichern ---
@st.cache_data
def load_rules():
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2), encoding="utf-8")
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    # Ergänze Defaults
    for cat, terms in DEFAULT_RULES.items():
        data.setdefault(cat, terms.copy())
    return data

@st.cache_data
def save_rules(rules):
    RULES_PATH.write_text(json.dumps(rules, indent=2), encoding="utf-8")

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

# --- UI ---
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

rules = load_rules()
patterns = build_patterns(rules)
# Sidebar navigation
choice = st.sidebar.radio("Modus", ["Analyse", "Regeln verwalten", "Regeln lernen"]）

if choice == "Analyse":
    ...
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    show_login()
    st.stop()

rules = load_rules()
patterns = build_patterns(rules)
choice = st.sidebar.radio("Modus", ["Analyse","Regeln verwalten","Regeln lernen"])

if choice == "Analyse":
    st.title("📊 Analyse")
    up = st.file_uploader("Excel (Feedback)")
    if up:
        df = pd.read_excel(up)
        if 'Feedback' in df:
            df['Kat'] = df['Feedback'].astype(str).apply(lambda x: categorize(x, patterns))
            st.dataframe(df)
            cnt = df['Kat'].value_counts(normalize=True)*100
            fig, ax = plt.subplots()
            cnt.sort_values().plot.barh(ax=ax)
            st.pyplot(fig)
            st.download_button("CSV", df.to_csv(index=False), "f.csv","text/csv")
            buf=io.BytesIO();pd.ExcelWriter(buf,engine='openpyxl').book;
            with pd.ExcelWriter(buf,engine='openpyxl') as w: df.to_excel(w,index=False)
            buf.seek(0)
            st.download_button("Excel",buf,"f.xlsx","application/vnd.ms-excel")
elif choice == "Regeln verwalten":
    st.title("⚙️ Manage Rules")
    for c in rules:
        with st.expander(c):
            terms=rules[c]
            rem=[]
            for i,t in enumerate(terms):
                col1,col2=st.columns([4,1])
                nt=col1.text_input("",value=t,key=f"r_{c}_{i}")
                if col2.button("❌",key=f"d_{c}_{i}"): rem.append(i)
                else: terms[i]=nt
            rules[c]=[t for idx,t in enumerate(terms) if idx not in rem]
    st.write("## Add New")
    nc=st.text_input("New Cat")
    nk=st.text_input("New Keyword")
    if st.button("Add") and nk:
        tgt=nc if nc else st.selectbox("Cat",list(rules))
        rules.setdefault(tgt,[]).append(nk)
        save_rules(rules)
        st.experimental_rerun()
else:
    st.title("🧠 Learn Rules")
    up=st.file_uploader("Excel (Feedback)",key='l')
    if up:
        d=pd.read_excel(up)
        if 'Feedback' in d:
            un={}
            for fb in d['Feedback'].astype(str):
                if categorize(fb,patterns)=='Sonstiges':
                    for w in re.findall(r"\w{4,}",fb):un[w]=un.get(w,0)+1
            for w,cnt in sorted(un.items(),key=lambda x:-x[1])[:30]:
                st.write(w,cnt)
                choice=st.selectbox("Cat",["Ignorieren"]+list(rules),key=w)
                if choice!='Ignorieren':
                    rules.setdefault(choice,[]).append(w);save_rules(rules);st.experimental_rerun()

save_rules(rules)

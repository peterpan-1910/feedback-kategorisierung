# feedback_app/app.py

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

# --- DEFAULT_RULES (vollständige Kategorien & Keywords) ---
# Füge hier deine vollständigen Listen ein
DEFAULT_RULES: dict[str, list[str]] = {
    "Login": [
        "einloggen", "login", "passwort", "anmeldung", "einloggen fehlgeschlagen", "nicht einloggen", "login funktioniert nicht",
        "authentifizierung fehler", "probleme beim anmelden", "nicht angemeldet", "zugriff", "fehlermeldung", "konto", "abmeldung",
        "kennwort", "verbindungsfehler", "sitzung", "anmeldedaten", "nutzerdaten", "loginversuch", "keine anmeldung möglich",
        "probleme mit login", "passwort falsch", "kennwort zurücksetzen", "neues passwort", "loginseite", "loginfenster",
        "verbindung fehlgeschlagen", "nicht authentifiziert", "anmeldung abgelehnt", "nutzerdaten ungültig", "app meldet fehler",
        "einloggen unmöglich", "nicht mehr angemeldet", "verbindung wird getrennt", "sitzung beendet", "session läuft ab",
        "fehlversuch login", "loginblockade"
    ],
    "TAN Probleme": [
        "tan", "code", "authentifizierung", "bestätigungscode", "code kommt nicht", "tan nicht erhalten", "sms tan",
        "tan eingabe", "problem mit tan", "keine tan bekommen", "tan ungültig", "tan feld fehlt", "neue tan", "tan abgelaufen",
        "tan funktioniert nicht", "tan wird nicht akzeptiert", "falscher tan code", "keine tan sms", "tan verzögert", "push tan",
        "photo tan", "mTAN", "secure tan", "tan app", "tan mail", "email tan", "keine tan gesendet", "2-faktor tan",
        "tan bleibt leer", "probleme mit authentifizierung"
    ],
    # ... alle weiteren Kategorien analog ergänzen ...
}

# --- Nutzerverwaltung ---
@st.cache_data(show_spinner=False)
def init_users() -> dict[str, str]:
    creds = st.secrets.get("credentials", {})
    if creds.get("username") and creds.get("password_hash"):
        return {creds["username"]: creds["password_hash"]}
    # Default-Credentials
    return {"admin2025": hashlib.sha256("data2025".encode()).hexdigest()}

_USERS = init_users()

def login(user: str, pwd: str) -> bool:
    return _USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest()

# --- Regelverwaltung ---
@st.cache_data(show_spinner=False)
def load_rules() -> dict[str, list[str]]:
    """
    Lädt Regeln. Beim ersten Aufruf erzeugt es die JSON-Datei mit DEFAULT_RULES.
    Beim Laden vorhandener Regeln werden fehlende Default-Begriffe ergänzt, ohne User-Daten zu überschreiben.
    """
    if RULES_PATH.exists():
        data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        # Ergänze fehlende Defaults
        for cat, terms in DEFAULT_RULES.items():
            if cat in data:
                for term in terms:
                    if term not in data[cat]:
                        data[cat].append(term)
            else:
                data[cat] = terms.copy()
        return data
    else:
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(
            json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return DEFAULT_RULES.copy()

@st.cache_data(show_spinner=False)
def save_rules(rules: dict[str, list[str]]) -> None:
    """
    Speichert das aktuelle Regel-Set und invalideert den Cache.
    """
    RULES_PATH.write_text(
        json.dumps(rules, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    # Cache invalidieren
    load_rules.clear()
    build_patterns.clear()

# --- Kategorisierung ---
@st.cache_data(show_spinner=False)
def build_patterns(rules: dict[str, list[str]]) -> dict[str, re.Pattern]:
    pats: dict[str, re.Pattern] = {}
    for cat, terms in rules.items():
        if terms:
            esc = [re.escape(t) for t in terms]
            pats[cat] = re.compile(r"\b(?:%s)\b" % "|".join(esc), re.IGNORECASE)
    return pats

@st.cache_data(show_spinner=False)
def categorize_series(feedback_series: pd.Series, patterns: dict[str, re.Pattern]) -> pd.Series:
    df = pd.DataFrame({ 'Feedback': feedback_series })
    df['Kategorie'] = 'Sonstiges'
    for cat, pat in patterns.items():
        mask = df['Feedback'].str.contains(pat, regex=True)
        df.loc[mask & (df['Kategorie'] == 'Sonstiges'), 'Kategorie'] = cat
    return df['Kategorie']

# --- UI: Login ---
def show_login() -> bool:
    st.markdown("<div style='text-align:center;'><h2>🔐 Anmeldung</h2></div>", unsafe_allow_html=True)
    user = st.text_input("👤 Benutzername", key="user_input")
    pwd = st.text_input("🔑 Passwort", type="password", key="pwd_input")
    if st.button("🚀 Anmelden"):
        if login(user, pwd):
            st.session_state.authenticated = True
            return True
        else:
            st.error("❌ Ungültige Anmeldedaten")
    return False

# --- Main ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    if show_login():
        st.experimental_rerun()
    else:
        st.stop()

# Lade Regeln & Patterns
rules = load_rules()
patterns = build_patterns(rules)

# Sidebar-Navigation
mode = st.sidebar.radio("Modus", ["Analyse", "Regeln verwalten", "Regeln lernen"])

# --- Analyse ---
if mode == "Analyse":
    st.title("📊 Feedback-Kategorisierung")
    uploaded = st.file_uploader("Excel (Spalte 'Feedback')", type=["xlsx"])
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
    # Bestehende Kategorien & Keywords
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            updated: list[str] = []
            for idx, term in enumerate(rules[cat]):
                c1, c2 = st.columns([4, 1])
                new_term = c1.text_input("", value=term, key=f"edit_{cat}_{idx}")
                remove = c2.checkbox("❌", key=f"rem_{cat}_{idx}")
                if not remove:
                    updated.append(new_term)
            rules[cat] = updated
    st.markdown("---")
    # Neue Kategorie erstellen
    new_cat_name = st.text_input("➕ Neue Kategorie hinzufügen", key="new_cat_name")
    if st.button("Kategorie erstellen") and new_cat_name:
        if new_cat_name not in rules:
            rules[new_cat_name] = []
            save_rules(rules)
            st.success(f"Kategorie '{new_cat_name}' erstellt.")
        else:
            st.error(f"Kategorie '{new_cat_name}' existiert bereits.")
    st.markdown("---")
    # Neues Keyword hinzufügen
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
        df_learn = pd.read_excel(uploaded)
        if 'Feedback' in df_learn.columns:
            unmatched: dict[str, int] = {}
            for fb in df_learn['Feedback'].astype(str):
                if categorize_series(pd.Series([fb]), patterns).iloc[0] == "Sonstiges":
                    for w in re.findall(r"\w{4,}", fb.lower()):
                        unmatched[w] = unmatched.get(w, 0) + 1
            suggestions = sorted(unmatched.items(), key=lambda x: x[1], reverse=True)[:30]
            st.subheader("Vorschläge für neue Keywords aus 'Sonstiges'")
            for idx, (word, cnt) in enumerate(suggestions):
                cols = st.columns([4, 2])
                cols[0].write(f"{word} ({cnt}x)")
                choice = cols[1].selectbox("Kategorie", ["Ignorieren"] + sorted(rules.keys()), key=f"learn_{idx}")
                if choice != "Ignorieren":
                    rules.setdefault(choice, []).append(word)
                    with open(LOG_PATH, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now().isoformat()};{word};{choice}\n")
                    save_rules(rules)
                    st.success(f"'{word}' wurde zu '{choice}' hinzugefügt.")

# --- Persistenz am Ende ---
save_rules(rules)
```

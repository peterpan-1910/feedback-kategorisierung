# Projektstruktur siehe README

### 1. `config.py` `config.py`
```python
from pathlib import Path

BASE_DIR = Path(__file__).parent
RULES_PATH = BASE_DIR / "data" / "custom_rules.json"
LOG_PATH = BASE_DIR / "data" / "rule_log.csv"
```

### 2. `auth.py`
```python
import hashlib
import streamlit as st

# Speicherung der Hash-Paare in Streamlit Secrets (nie im Code selbst)
_USERS = {
    st.secrets.credentials.username: st.secrets.credentials.password_hash
}

def login(username: str, password: str) -> bool:
    hash_input = hashlib.sha256(password.encode()).hexdigest()
    return _USERS.get(username) == hash_input
```

### 3. `rules_manager.py`
```python
import json
from streamlit import cache_data
from config import RULES_PATH

# Default-Regeln (Initiales Set, unverändert erhalten)
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
    "App abstürze": [
        "absturz", "hängt", "app stürzt ab", "reagiert nicht", "crash", "app friert ein", "schließt sich", "hängt sich auf",
        "abgestürzt", "beendet sich", "app hängt sich auf", "app schließt unerwartet", "fehler beim starten", "app startet nicht",
        "startet nicht mehr", "app funktioniert nicht", "nichts passiert", "plötzlich beendet", "bleibt stehen", "app reagiert nicht",
        "schwarzer bildschirm", "app lädt nicht", "absturz beim öffnen", "abbruch", "fehler beim öffnen", "startproblem",
        "app bleibt hängen", "app hängt fest", "schließt nach start", "app stürzt ständig ab"
    ],
    "Fehler / Bugs": [
        "fehler", "bug", "problem", "funktioniert nicht", "technischer fehler", "defekt", "störung", "anwendungsfehler",
        "fehlerhaft", "problematisch", "systemfehler", "fehlermeldung", "appfehler", "softwareproblem", "ausnahmefehler",
        "programmfehler", "fehleranzeige", "abbruchfehler", "nicht verfügbar", "error", "fehlfunktion", "nicht geladen",
        "seitenfehler", "prozessfehler", "absturzmeldung", "stopp", "hänger", "service nicht erreichbar", "ladefehler",
        "modulproblem"
    ],
    "Rückzahlungsoptionen": [
        "rückzahlung", "raten", "tilgung", "zurückzahlen", "zahlung aufteilen", "zahlungspause", "rate ändern",
        "tilgungsplan", "rückzahlung ändern", "ratenzahlung", "rückzahlungsplan", "abzahlungsoption", "zahlung stunden",
        "zahlungsaufschub", "zahlung reduzieren", "monatsrate ändern", "zahlung anpassen", "flexible raten",
        "anpassung rate", "kreditrückzahlung", "anzahlung", "zahlung verschieben", "abzahlungsdauer", "rückzahlungsart",
        "zahlung in teilen", "verzögerung", "teilrückzahlung", "ablösung kredit", "rate pausieren", "rate aussetzen"
    ],
    "Zahlungsprobleme": [
        "zahlung", "überweisung", "geld senden", "keine buchung", "zahlung funktioniert nicht", "zahlung fehlgeschlagen",
        "nicht überwiesen", "nicht angekommen", "probleme mit zahlung", "überweisung hängt", "zahlung nicht möglich",
        "zahlung abgelehnt", "konnte nicht zahlen", "buchung nicht durchgeführt", "fehlende zahlung", "problem mit lastschrift",
        "banküberweisung gescheitert", "nicht gebucht", "zahlungsvorgang fehlerhaft", "betrag nicht abgebucht",
        "zahlung wurde nicht verarbeitet", "lastschrift fehlgeschlagen", "überweisung nicht angekommen",
        "zahlung nicht bestätigt", "abbuchung fehlt", "keine bestätigung", "geld nicht übertragen",
        "buchung offen", "geld nicht gutgeschrieben", "fehlermeldung bei zahlung"
    ],
    "Kompliziert / Unklar": [
        "kompliziert", "nicht verständlich", "nicht intuitiv", "schwer zu verstehen", "unklar", "nicht eindeutig",
        "umständlich", "nicht nutzerfreundlich", "unverständlich", "verwirrend", "komplizierter vorgang",
        "nicht nachvollziehbar", "nicht klar erklärt", "unlogisch", "verwirrende navigation", "menü unverständlich",
        "unklare anleitung", "komplizierte beschreibung", "sperrig", "nicht selbsterklärend",
        "nicht selbsterklärlich", "verwirrende benennung", "missverständlich", "komplexe struktur",
        "kein roter faden", "nicht eindeutig beschrieben", "nicht eindeutig erklärt", "nicht selbsterklärende schritte",
        "nicht klar gegliedert", "undurchsichtig"
    ],
    "Feature-Wünsche / Kritik": [
        "funktion fehlt", "wäre gut", "feature", "nicht vorgesehen", "funktion sollte", "funktion benötigt",
        "ich wünsche mir", "bitte ergänzen", "könnte man hinzufügen", "nicht verfügbar", "funktion nicht vorhanden",
        "funktion deaktiviert", "fehlt in der app", "keine möglichkeit", "nicht vorgesehen", "nicht enthalten",
        "noch nicht verfügbar", "sollte implementiert werden", "gewünschtes feature", "funktion vermisst",
        "kein button", "nicht auswählbar", "keine option", "option fehlt", "nicht konfigurierbar",
        "könnte verbessert werden", "wünschenswert", "funktion erweitern", "benutzerwunsch", "nicht freigeschaltet"
    ],
    "Sprachprobleme": [
        "englisch", "nicht auf deutsch", "sprache falsch", "nur englisch", "kein deutsch",
        "nicht lokalisiert", "übersetzung fehlt", "englische sprache", "sprache ändern",
        "menü englisch", "texte nicht übersetzt", "nur englische version",
        "übersetzungsfehler", "falsche sprache", "texte nicht verständlich",
        "fehlende lokalisierung", "keine deutsche sprache", "falsche sprachversion",
        "spracheinstellungen fehlen", "menü auf englisch", "fehlende übersetzung",
        "sprachlich unklar", "kein sprachwechsel", "interface englisch",
        "nicht auf deutsch verfügbar", "englischer hilfetext", "sprachumschaltung fehlt",
        "keine lokalisierung", "fehlende sprachwahl", "hilfe nur englisch"
    ],
    "Sicherheit": [
        "sicherheit", "schutz", "sicherheitsproblem", "datenleck", "nicht sicher", "unsicher",
        "sicherheitsbedenken", "keine 2-faktor", "risiko", "zugriffsproblem",
        "sicherheitslücke", "keine verschlüsselung", "unsichere verbindung",
        "unsicherer zugang", "schutz fehlt", "keine passwortabfrage",
        "fehlende sicherheit", "daten ungeschützt", "authentifizierung unklar",
        "zugriff ohne sicherheit", "fehlender schutzmechanismus", "kein logout",
        "automatischer logout fehlt", "keine warnmeldung", "sicherheitsmeldung fehlt",
        "datenweitergabe", "keine session begrenzung", "session nicht gesichert",
        "zugangsdaten unverschlüsselt", "zugriffsrechte unklar"
    ],
    "Tagesgeld": [
        "tagesgeld", "zins", "geldanlage", "sparzins", "zinskonto", "zinsen fehlen",
        "tagesgeldkonto", "keine verzinsung", "tagesgeldrate", "zinsbindung",
        "verzinsung", "zinsänderung", "tagesgeldkonto nicht sichtbar",
        "tagesgeld nicht auswählbar", "zins niedrig", "zinsangebot",
        "anlagezins", "keine zinsinfo", "zins falsch angezeigt",
        "tagesgeld fehler", "nicht verzinst", "zins fehlt",
        "tagesgeldrate nicht geändert", "tagesgeldrate nicht angepasst",
        "zinsbuchung fehlt", "zinsrate falsch", "zins wird nicht berechnet",
        "tagesgeldkonto fehlt", "keine zinsanpassung", "tagesgeldoption fehlt"
    ],
    "Werbung": [
        "werbung", "angebot", "promo", "aktionscode", "zu viel werbung",
        "nervige werbung", "nicht relevant", "spam", "werbeeinblendung",
        "promotion", "werbeanzeige", "werbebanner", "werbebotschaft",
        "unpassende werbung", "irrelevante werbung", "werbeaktion",
        "werbung eingeblendet", "push werbung", "email werbung",
        "werbung auf startseite", "nicht deaktivierbar", "werbung bei login",
        "keine option zum abschalten", "störende werbung", "zu viele angebote",
        "angebote nerven", "werbung in app", "werbung zu präsent",
        "popup werbung", "unnötige angebote"
    ],
    "UI/UX": [
        "veraltet", "nicht modern", "design alt", "nicht intuitiv",
        "menüführung schlecht", "layout veraltet", "keine struktur",
        "nicht übersichtlich", "nicht schön", "altbacken", "altmodisch",
        "nicht benutzerfreundlich", "unübersichtliches layout",
        "...


@cache_data(show_spinner=False)
def load_rules() -> dict[str, list[str]]:
    if RULES_PATH.exists():
        try:
            return json.loads(RULES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
            return DEFAULT_RULES.copy()
    else:
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
        return DEFAULT_RULES.copy()

@cache_data(show_spinner=False)
def save_rules(rules: dict[str, list[str]]) -> None:
    RULES_PATH.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
```

### 4. `categorizer.py`
```python
import re
from streamlit import cache_data

@cache_data(show_spinner=False)
def build_pattern_map(rules: dict[str, list[str]]) -> dict[str, re.Pattern]:
    patterns: dict[str, re.Pattern] = {}
    for cat, terms in rules.items():
        if not terms:
            continue
        escaped = [re.escape(t) for t in set(terms) if t]
        pattern = re.compile(r"\b(?:%s)\b" % "|".join(escaped), re.IGNORECASE)
        patterns[cat] = pattern
    return patterns

@cache_data(show_spinner=False)
def categorize(text: str, patterns: dict[str, re.Pattern]) -> str:
    for cat, pat in patterns.items():
        if pat.search(text):
            return cat
    return "Sonstiges"
```

### 5. `ui_components.py`
```python
import streamlit as st
from auth import login

# Zentrales UI für Login
def show_login():
    st.markdown("## 🔐 Anmeldung zur Feedback-Kategorisierung")
    st.text_input("👤 Benutzername", key="user_input")
    st.text_input("🔑 Passwort", type="password", key="pwd_input")
    if st.button("🚀 Loslegen"):
        if login(st.session_state.user_input, st.session_state.pwd_input):
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("❌ Falsche Anmeldedaten")

# Sidebar-Navigation
def sidebar_menu(options: list[str]) -> str:
    return st.sidebar.radio("Navigation", options)
```

### 6. `app.py`
```python
import streamlit as st
from ui_components import show_login, sidebar_menu
from rules_manager import load_rules, save_rules
from categorizer import build_pattern_map, categorize
from config import LOG_PATH
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches

# Auth-Initialisierung
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login()
    st.stop()

# Daten laden
rules = load_rules()
patterns = build_pattern_map(rules)
mode = sidebar_menu(["Analyse", "Regeln verwalten", "Regeln lernen"])

# ---------------- Analyse ----------------
if mode == "Analyse":
    st.title("📊 Regelbasierte Feedback-Kategorisierung")
    uploaded = st.file_uploader("📤 Excel mit Feedback hochladen", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        if 'Feedback' in df.columns:
            df['Kategorie'] = df['Feedback'].astype(str).apply(lambda t: categorize(t, patterns))
            st.dataframe(df[['Feedback', 'Kategorie']])
            counts = df['Kategorie'].value_counts(normalize=True).mul(100)
            fig, ax = plt.subplots()
            counts.sort_values().plot.barh(ax=ax)
            ax.set_xlabel("Anteil (%)")
            st.pyplot(fig)
            st.download_button("Als CSV", df.to_csv(index=False), "feedback.csv")
            st.download_button("Als Excel", df.to_excel(index=False), "feedback.xlsx")
        else:
            st.error("Spalte 'Feedback' fehlt.")

# ---------------- Regeln verwalten ----------------
elif mode == "Regeln verwalten":
    st.title("🔧 Regeln verwalten")
    # Bestehende Kategorien und Keywords
    for cat in sorted(rules.keys()):
        with st.expander(f"📁 {cat} ({len(rules[cat])} Begriffe)"):
            # Editierbare Liste
            terms_str = ", ".join(rules[cat])
            edited = st.text_area("Begriffe (Komma-separiert)", value=terms_str, key=f"edit_{cat}")
            new_list = [t.strip().lower() for t in edited.split(",") if t.strip()]
            rules[cat] = new_list
    st.markdown("---")
    # Neue Regel hinzufügen
    st.subheader("➕ Neue Regel hinzufügen")
    option_list = ["<Neue Kategorie>"] + sorted(rules.keys())
    sel_cat = st.selectbox("Kategorie auswählen", option_list, index=0)
    if sel_cat == "<Neue Kategorie>":
        sel_cat = st.text_input("Name der neuen Kategorie", key="new_cat_name")
    new_kw = st.text_input("Neues Schlüsselwort", key="new_kw")
    if st.button("Hinzufügen") and new_kw:
        rules.setdefault(sel_cat, []).append(new_kw.lower())
        save_rules(rules)
        st.success(f"'{new_kw}' wurde zu '{sel_cat}' hinzugefügt")
        st.experimental_rerun()

# ---------------- Regeln lernen ----------------
elif mode == "Regeln lernen":
    st.title("🧠 Regeln lernen")
    uploaded_learn = st.file_uploader("📤 Excel mit Feedback (Spalte 'Feedback')", type=["xlsx"], key="learn")
    if uploaded_learn:
        df_learn = pd.read_excel(uploaded_learn)
        if 'Feedback' not in df_learn.columns:
            st.error("Spalte 'Feedback' fehlt.")
            st.stop()
        unmatched = {}
        for fb in df_learn['Feedback'].astype(str):
            text = fb.lower()
            if categorize(text, patterns) == "Sonstiges":
                for w in text.split():
                    if len(w) > 3:
                        unmatched[w] = unmatched.get(w, 0) + 1
        suggestions = sorted(unmatched.items(), key=lambda x: x[1], reverse=True)[:30]
        st.subheader("🔍 Häufige unbekannte Wörter")
        for word, cnt in suggestions:
            cols = st.columns([3,2])
            cols[0].write(f"{word} ({cnt}x)")
            # Vorschlag anhand ähnlicher Begriffe
            flat = {t:cat for cat, terms in rules.items() for t in terms}
            match = get_close_matches(word, flat.keys(), n=1, cutoff=0.6)
            default = match[0] if match else None
            sel = cols[1].selectbox("Kategorie", ["Ignorieren"] + sorted(rules.keys()), index=(sorted(rules.keys()).index(default)+1 if default else 0), key=f"assign_{word}")
            if sel != "Ignorieren":
                rules.setdefault(sel, []).append(word)
                with open(LOG_PATH, 'a', encoding='utf-8') as log:
                    import datetime
                    log.write(f"{datetime.datetime.now().isoformat()};{word};{sel}\n")
                save_rules(rules)
                st.success(f"'{word}' wurde der Kategorie '{sel}' hinzugefügt")
                st.experimental_rerun()

# Persistenz am Ende
save_rules(rules)
```

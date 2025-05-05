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

# --- GitHub-Integration ---
try:
    from github import Github
except ImportError:
    Github = None  # PyGithub nicht installiert

# GitHub-Token und Repo-Name aus Streamlit Secrets
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")  # Format: "user/repo"

def push_rules_to_github(rules: dict[str, list[str]]):
    """
    Commitet und pusht custom_rules.json per GitHub API.
    VORAUSSETZUNG: PyGithub installiert + GITHUB_TOKEN, REPO_NAME gesetzt.
    """
    if Github is None or not GITHUB_TOKEN or not REPO_NAME:
        st.warning("GitHub-Commit übersprungen (PyGithub/Tokens nicht konfiguriert)")
        return
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(REPO_NAME)
        content_path = "data/custom_rules.json"
        contents = repo.get_contents(content_path)
        new_content = json.dumps(rules, indent=2, ensure_ascii=False)
        repo.update_file(
            path=content_path,
            message="[Streamlit] Update custom_rules.json",
            content=new_content,
            sha=contents.sha
        )
        st.info("custom_rules.json erfolgreich nach GitHub gepusht.")
    except Exception as e:
        st.error(f"GitHub-Push fehlgeschlagen: {e}")

# --- Konfiguration ---
BASE_DIR = Path(__file__).parent
RULES_PATH = BASE_DIR / "data" / "custom_rules.json"
LOG_PATH = BASE_DIR / "data" / "rule_log.csv"

# --- Default-Regeln ---
DEFAULT_RULES = {
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
        "nicht ansprechend", "veraltetes interface", "kein modernes design",
        "wirkt alt", "design nicht aktuell", "unmoderne oberfläche",
        "technisch alt", "nicht responsive", "bedienung veraltet",
        "style altbacken", "nutzung unkomfortabel", "umständliches layout",
        "nicht ansehnlich", "elemente zu klein", "zu viel text", "keine icons",
        "unpraktische darstellung"
    ],
    "unübersichtlich": [
        "unübersichtlich", "nicht klar", "durcheinander", "nicht strukturiert",
        "keine ordnung", "keine übersicht", "zu komplex", "schlecht aufgebaut",
        "nicht nachvollziehbar", "layout chaotisch", "verwirrend",
        "keine menüstruktur", "kein überblick", "unklare gliederung",
        "unstrukturierte darstellung", "unübersichtliche seite",
        "navigation schwierig", "kompliziertes menü", "kein roter faden",
        "menüführung unklar", "fehlende kategorien", "kein filter",
        "ohne sortierung", "unleserlich", "überladen", "optisch unklar",
        "nicht gut erkennbar", "kategorie fehlt"
    ],
    "langsam": [
        "langsam", "lädt lange", "dauert ewig", "träge", "reaktionszeit",
        "verzögert", "ewiges laden", "warten", "verbindung langsam",
        "nicht flüssig", "app ist träge", "verzögerte reagieren",
        "ladeprobleme", "app ist langsam", "reagiert langsam",
        "lange ladezeit", "performanceschwäche", "zu langsam",
        "langsamer aufbau", "app lädt nicht sofort", "träge benutzung",
        "startet langsam", "verarbeitung dauert", "menü öffnet langsam",
        "daten laden ewig", "prozess dauert", "feedback dauert",
        "anmeldung langsam", "reaktion zu spät", "verarbeitung verzögert"
    ],
    "Kundenservice": [
        "support", "hotline", "rückruf", "keine antwort", "niemand erreichbar",
        "service schlecht", "lange wartezeit", "kundendienst", "keine hilfe",
        "service reagiert nicht", "keine unterstützung", "reagiert nicht",
        "kontakt nicht möglich", "wartezeit", "keine rückmeldung",
        "telefonisch nicht erreichbar", "keine lösung", "antwort dauert",
        "kundenberatung fehlt", "keine antwort erhalten", "hotline nicht erreichbar",
        "keine serviceleistung", "kundensupport schlecht", "kundenbetreuung mangelhaft",
        "kundenservice reagiert nicht", "service schwer erreichbar", "service antwortet nicht",
        "nicht geholfen", "unfreundlicher support", "hilft nicht weiter"
    ],
    "Kontaktmöglichkeiten": [
        "ansprechpartner", "kontakt", "rückruf", "nicht erreichbar", "kein kontakt",
        "keine kontaktdaten", "hilfe fehlt", "kontaktformular", "keine rückmeldung",
        "support kontakt", "kein formular", "supportformular fehlt",
        "kundendienst kontaktieren", "telefon fehlt", "email fehlt", "nur hotline",
        "kontakt schwierig", "kontaktierung unklar", "kontaktoption fehlt",
        "keine kontaktmöglichkeit", "nicht ansprechbar", "support schwer erreichbar",
        "kein livechat", "keine supportmail", "anfrage nicht möglich",
        "kein rückruf erhalten", "kontaktseite leer", "keine kontaktfunktion",
        "kontaktmöglichkeit nicht ersichtlich", "anfrageformular fehlt"
    ],
    "Vertrauenswürdigkeit": [
        "vertrauen", "abzocke", "nicht seriös", "zweifelhaft", "skepsis",
        "nicht glaubwürdig", "unsicher", "nicht transparent", "betrugsverdacht",
        "nicht vertrauenswürdig", "datensicherheit", "nicht nachvollziehbar",
        "intransparente kosten", "unseriös", "abzocker", "misstrauen",
        "unsicheres gefühl", "nicht überprüfbar", "unvollständig",
        "zweifelhaftes angebot", "kein impressum", "keine transparenz",
        "zweifelhaftes verhalten", "verdacht auf betrug", "unsichere kommunikation",
        "fehlende datensicherheit", "keine aufklärung", "unzuverlässig",
        "fragwürdig", "irreführend"
    ],
    "Gebühren": [
        "gebühr", "zinsen", "bearbeitungsgebühr", "kosten", "preis", "zu teuer",
        "gebühren nicht klar", "versteckte kosten", "nicht kostenlos",
        "zusatzkosten", "gebühren unklar", "bankgebühren",
        "gebührenerhöhung", "nicht transparent", "kosten zu hoch",
        "gebührenänderung", "kontoführungsgebühr", "auszahlungsgebühr",
        "transaktionsgebühr", "gebühr zu hoch", "zu hohe zinsen",
        "gebühreninfo fehlt", "unverhältnismäßige gebühr", "gebühr nicht nachvollzierbar",
        "entgelt", "gebührenbelastung", "gebühr nicht verständlich",
        "servicegebühr", "provision", "kostenaufstellung fehlt"
    ]
}

# --- Nutzerverwaltung ---
try:
    from github import Github
except ImportError:
    Github = None  # PyGithub nicht installiert


# GitHub-Integration: Token in Streamlit-Secrets als GITHUB_TOKEN hinterlegen
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")  # z.B. "user/repo"

# Funktion zum Pushen der Regeln via GitHub-API
def push_rules_to_github(rules: dict[str, list[str]]):
    """
    Commitet und pusht custom_rules.json in dein GitHub-Repo.
    Vorher muss GITHUB_TOKEN (mit repo-Berechtigung) und REPO_NAME in st.secrets gesetzt sein.
    """
    if not GITHUB_TOKEN or not REPO_NAME:
        st.warning("GitHub-Token oder Repo-Name nicht konfiguriert: push_rules_to_github übersprungen.")
        return
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(REPO_NAME)
        path = "data/custom_rules.json"
        # Hole aktuellen SHA
        contents = repo.get_contents(path)
        new_content = json.dumps(rules, indent=2, ensure_ascii=False)
        repo.update_file(
            path=path,
            message="[Streamlit] Update custom_rules.json",
            content=new_content,
            sha=contents.sha
        )
        st.info("custom_rules.json erfolgreich nach GitHub gepusht.")
    except Exception as e:
        st.error(f"Fehler beim Push zu GitHub: {e}")


@st.cache_data(show_spinner=False)
def init_users():
    creds = st.secrets.get("credentials", {})
    if creds.get("username") and creds.get("password_hash"):
        return {creds["username"]: creds["password_hash"]}
    return {"admin2025": hashlib.sha256("data2025".encode()).hexdigest()}

_USERS = init_users()

def login(user: str, pwd: str) -> bool:
    return _USERS.get(user) == hashlib.sha256(pwd.encode()).hexdigest()

# --- Regeln laden/speichern ---
@st.cache_data(show_spinner=False)
def load_rules():
    if not RULES_PATH.exists():
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False), encoding="utf-8")
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    for cat, terms in DEFAULT_RULES.items():
        data.setdefault(cat, terms.copy())
    return data

def save_rules(rules):
    RULES_PATH.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
    load_rules.clear()

# --- Kategorisierung ---
@st.cache_data(show_spinner=False)
def build_patterns(rules):
    pats = {}
    for cat, terms in rules.items():
        if terms:
            esc = [re.escape(t) for t in terms]
            pats[cat] = re.compile(r"\b(?:%s)\b" % "|".join(esc), re.IGNORECASE)
    return pats

@st.cache_data(show_spinner=False)
def categorize_series(feedback_series, patterns):
    df = pd.DataFrame({ 'Feedback': feedback_series })
    df['Kategorie'] = 'Sonstiges'
    for cat, pat in patterns.items():
        mask = df['Feedback'].str.contains(pat)
        df.loc[mask & (df['Kategorie'] == 'Sonstiges'), 'Kategorie'] = cat
    return df['Kategorie']

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

rules = load_rules()
patterns = build_patterns(rules)
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
    # Bestehende Kategorien & Keywords bearbeiten
    for cat in sorted(rules.keys()):
        with st.expander(f"{cat} ({len(rules[cat])} Begriffe)"):
            updated = []
            for idx, term in enumerate(rules[cat]):
                c1, c2 = st.columns([4, 1])
                new_term = c1.text_input("", value=term, key=f"edit_{cat}_{idx}")
                remove = c2.checkbox("❌", key=f"rem_{cat}_{idx}")
                if not remove:
                    updated.append(new_term)
            rules[cat] = updated
    st.markdown("---")
    # Neue Kategorie erstellen
    st.subheader("➕ Neue Kategorie hinzufügen")
    new_cat_name = st.text_input("Name der neuen Kategorie", key="new_cat_name")
    if st.button("Kategorie erstellen", key="create_cat") and new_cat_name:
        if new_cat_name not in rules:
            rules[new_cat_name] = []
            save_rules(rules)
            st.success(f"Kategorie '{new_cat_name}' wurde erstellt.")
        else:
            st.error(f"Kategorie '{new_cat_name}' existiert bereits.")
    st.markdown("---")
    # Neues Keyword hinzufügen
    st.subheader("➕ Neues Keyword hinzufügen")
    tgt = st.selectbox("Kategorie auswählen", sorted(rules.keys()), key="new_cat")
    new_kw = st.text_input("Neues Keyword", key="new_kw")
    if st.button("Hinzufügen", key="add_kw") and new_kw:
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

# --- Persistenz ---
save_rules(rules)

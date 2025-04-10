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
menu = st.sidebar.radio("Navigiere zu", ["Analyse", "Regeln lernen"])

if menu == "Kategorien verwalten":
    
    st.stop()

# ------------------ Kategorien & Regelverwaltung ------------------

rules_file = "custom_rules.json"
if os.path.exists(rules_file):
    with open(rules_file, "r") as f:
        all_rules = json.load(f)
else:
    all_rules = {
        # Hinweis: Jede Kategorie hat jetzt mindestens 30 semantisch passende Begriffe
        "Login": ["einloggen", "login", "passwort", "anmeldung", "einloggen fehlgeschlagen", "nicht einloggen", "login funktioniert nicht", "authentifizierung fehler", "probleme beim anmelden", "nicht angemeldet", "zugriff", "fehlermeldung", "konto", "abmeldung", "kennwort", "verbindungsfehler", "sitzung", "anmeldedaten", "nutzerdaten", "loginversuch", "keine anmeldung möglich", "probleme mit login", "passwort falsch", "kennwort zurücksetzen", "neues passwort", "loginseite", "loginfenster", "verbindung fehlgeschlagen", "nicht authentifiziert", "anmeldung abgelehnt", "nutzerdaten ungültig", "app meldet fehler", "einloggen unmöglich", "nicht mehr angemeldet", "verbindung wird getrennt", "sitzung beendet", "session läuft ab", "fehlversuch login", "loginblockade"],
        "TAN Probleme": ["tan", "code", "authentifizierung", "bestätigungscode", "code kommt nicht", "tan nicht erhalten", "sms tan", "tan eingabe", "problem mit tan", "keine tan bekommen", "tan ungültig", "tan feld fehlt", "neue tan", "tan abgelaufen", "tan funktioniert nicht", "tan wird nicht akzeptiert", "falscher tan code", "keine tan sms", "tan verzögert", "push tan", "photo tan", "mTAN", "secure tan", "tan app", "tan mail", "email tan", "keine tan gesendet", "2-faktor tan", "tan bleibt leer", "probleme mit authentifizierung"],
        "App abstürze": ["absturz", "hängt", "app stürzt ab", "reagiert nicht", "crash", "app friert ein", "schließt sich", "hängt sich auf", "abgestürzt", "beendet sich", "app hängt sich auf", "app schließt unerwartet", "fehler beim starten", "app startet nicht", "startet nicht mehr", "app funktioniert nicht", "nichts passiert", "plötzlich beendet", "bleibt stehen", "app reagiert nicht", "schwarzer bildschirm", "app lädt nicht", "absturz beim öffnen", "abbruch", "fehler beim öffnen", "startproblem", "app bleibt hängen", "app hängt fest", "schließt nach start", "app stürzt ständig ab"],
        "Fehler / Bugs": ["fehler", "bug", "problem", "funktioniert nicht", "technischer fehler", "defekt", "störung", "anwendungsfehler", "fehlerhaft", "problematisch", "systemfehler", "fehlermeldung", "appfehler", "softwareproblem", "ausnahmefehler", "programmfehler", "fehleranzeige", "abbruchfehler", "nicht verfügbar", "error", "fehlfunktion", "nicht geladen", "seitenfehler", "prozessfehler", "absturzmeldung", "stopp", "hänger", "service nicht erreichbar", "ladefehler", "modulproblem"],
        "Rückzahlungsoptionen": ["rückzahlung", "raten", "tilgung", "zurückzahlen", "zahlung aufteilen", "zahlungspause", "rate ändern", "tilgungsplan", "rückzahlung ändern", "ratenzahlung", "rückzahlungsplan", "abzahlungsoption", "zahlung stunden", "zahlungsaufschub", "zahlung reduzieren", "monatsrate ändern", "zahlung anpassen", "flexible raten", "anpassung rate", "kreditrückzahlung", "anzahlung", "zahlung verschieben", "abzahlungsdauer", "rückzahlungsart", "zahlung in teilen", "verzögerung", "teilrückzahlung", "ablösung kredit", "rate pausieren", "rate aussetzen"],
        "Zahlungsprobleme": ["zahlung", "überweisung", "geld senden", "keine buchung", "zahlung funktioniert nicht", "zahlung fehlgeschlagen", "nicht überwiesen", "nicht angekommen", "probleme mit zahlung", "überweisung hängt", "zahlung nicht möglich", "zahlung abgelehnt", "konnte nicht zahlen", "buchung nicht durchgeführt", "fehlende zahlung", "problem mit lastschrift", "banküberweisung gescheitert", "nicht gebucht", "zahlungsvorgang fehlerhaft", "betrag nicht abgebucht", "zahlung wurde nicht verarbeitet", "lastschrift fehlgeschlagen", "überweisung nicht angekommen", "zahlung nicht bestätigt", "abbuchung fehlt", "keine bestätigung", "geld nicht übertragen", "buchung offen", "geld nicht gutgeschrieben", "fehlermeldung bei zahlung"],
        "Kompliziert / Unklar": ["kompliziert", "nicht verständlich", "nicht intuitiv", "schwer zu verstehen", "unklar", "nicht eindeutig", "umständlich", "nicht nutzerfreundlich", "unverständlich", "verwirrend", "komplizierter vorgang", "nicht nachvollziehbar", "nicht klar erklärt", "unlogisch", "verwirrende navigation", "menü unverständlich", "unklare anleitung", "komplizierte beschreibung", "sperrig", "nicht selbsterklärend", "nicht selbsterklärlich", "verwirrende benennung", "missverständlich", "komplexe struktur", "kein roter faden", "nicht eindeutig beschrieben", "nicht eindeutig erklärt", "nicht selbsterklärende schritte", "nicht klar gegliedert", "undurchsichtig"],
        "Feature-Wünsche / Kritik": ["funktion fehlt", "wäre gut", "feature", "nicht vorgesehen", "funktion sollte", "funktion benötigt", "ich wünsche mir", "bitte ergänzen", "könnte man hinzufügen", "nicht verfügbar", "funktion nicht vorhanden", "funktion deaktiviert", "fehlt in der app", "keine möglichkeit", "nicht vorgesehen", "nicht enthalten", "noch nicht verfügbar", "sollte implementiert werden", "gewünschtes feature", "funktion vermisst", "kein button", "nicht auswählbar", "keine option", "option fehlt", "nicht konfigurierbar", "könnte verbessert werden", "wünschenswert", "funktion erweitern", "benutzerwunsch", "nicht freigeschaltet"],
        "Sprachprobleme": ["englisch", "nicht auf deutsch", "sprache falsch", "nur englisch", "kein deutsch", "nicht lokalisiert", "übersetzung fehlt", "englische sprache", "sprache ändern", "menü englisch", "texte nicht übersetzt", "nur englische version", "übersetzungsfehler", "falsche sprache", "texte nicht verständlich", "fehlende lokalisierung", "keine deutsche sprache", "falsche sprachversion", "spracheinstellungen fehlen", "menü auf englisch", "fehlende übersetzung", "sprachlich unklar", "kein sprachwechsel", "interface englisch", "nicht auf deutsch verfügbar", "englischer hilfetext", "sprachumschaltung fehlt", "keine lokalisierung", "fehlende sprachwahl", "hilfe nur englisch"],
        "Sicherheit": ["sicherheit", "schutz", "sicherheitsproblem", "datenleck", "nicht sicher", "unsicher", "sicherheitsbedenken", "keine 2-faktor", "risiko", "zugriffsproblem", "sicherheitslücke", "keine verschlüsselung", "unsichere verbindung", "unsicherer zugang", "schutz fehlt", "keine passwortabfrage", "fehlende sicherheit", "daten ungeschützt", "authentifizierung unklar", "zugriff ohne sicherheit", "fehlender schutzmechanismus", "kein logout", "automatischer logout fehlt", "keine warnmeldung", "sicherheitsmeldung fehlt", "datenweitergabe", "keine session begrenzung", "session nicht gesichert", "zugangsdaten unverschlüsselt", "zugriffsrechte unklar"],
        "Tagesgeld": ["tagesgeld", "zins", "geldanlage", "sparzins", "zinskonto", "zinsen fehlen", "tagesgeldkonto", "keine verzinsung", "tagesgeldrate", "zinsbindung", "verzinsung", "zinsänderung", "tagesgeldkonto nicht sichtbar", "tagesgeld nicht auswählbar", "zins niedrig", "zinsangebot", "anlagezins", "keine zinsinfo", "zins falsch angezeigt", "tagesgeld fehler", "nicht verzinst", "zins fehlt", "tagesgeldrate nicht geändert", "tagesgeldrate nicht angepasst", "zinsbuchung fehlt", "zinsrate falsch", "zins wird nicht berechnet", "tagesgeldkonto fehlt", "keine zinsanpassung", "tagesgeldoption fehlt"],
        "Werbung": ["werbung", "angebot", "promo", "aktionscode", "zu viel werbung", "nervige werbung", "nicht relevant", "spam", "werbeeinblendung", "promotion", "werbeanzeige", "werbebanner", "werbebotschaft", "unpassende werbung", "irrelevante werbung", "werbeaktion", "werbung eingeblendet", "push werbung", "email werbung", "werbung auf startseite", "nicht deaktivierbar", "werbung bei login", "keine option zum abschalten", "störende werbung", "zu viele angebote", "angebote nerven", "werbung in app", "werbung zu präsent", "popup werbung", "unnötige angebote"],
        "UI/UX": ["veraltet", "nicht modern", "design alt", "nicht intuitiv", "menüführung schlecht", "layout veraltet", "keine struktur", "nicht übersichtlich", "nicht schön", "altbacken", "altmodisch", "nicht benutzerfreundlich", "unübersichtliches layout", "nicht ansprechend", "veraltetes interface", "kein modernes design", "wirkt alt", "design nicht aktuell", "unmoderne oberfläche", "technisch alt", "nicht responsive", "bedienung veraltet", "style altbacken", "nutzung unkomfortabel", "umständliches layout", "nicht ansehnlich", "elemente zu klein", "zu viel text", "keine icons", "unpraktische darstellung"],
        "unübersichtlich": ["unübersichtlich", "nicht klar", "durcheinander", "nicht strukturiert", "keine ordnung", "keine übersicht", "zu komplex", "schlecht aufgebaut", "nicht nachvollziehbar", "layout chaotisch", "verwirrend", "keine menüstruktur", "kein überblick", "unklare gliederung", "unübersichtliches menü", "nicht übersichtlich", "unstrukturierte darstellung", "unübersichtliche seite", "navigation schwierig", "kompliziertes menü", "kein roter faden", "menüführung unklar", "fehlende kategorien", "kein filter", "ohne sortierung", "unleserlich", "überladen", "optisch unklar", "nicht gut erkennbar", "kategorie fehlt"],
        "langsam": ["langsam", "lädt lange", "dauert ewig", "träge", "reaktionszeit", "verzögert", "ewiges laden", "warten", "verbindung langsam", "nicht flüssig", "app ist träge", "verzögertes reagieren", "ladeprobleme", "app ist langsam", "reagiert langsam", "lange ladezeit", "performanceschwäche", "zu langsam", "langsamer aufbau", "app lädt nicht sofort", "träge benutzung", "startet langsam", "verarbeitung dauert", "menü öffnet langsam", "daten laden ewig", "prozess dauert", "feedback dauert", "anmeldung langsam", "reaktion zu spät", "verarbeitung verzögert"],
        "Kundenservice": ["support", "hotline", "rückruf", "keine antwort", "niemand erreichbar", "service schlecht", "lange wartezeit", "kundendienst", "keine hilfe", "service reagiert nicht", "keine unterstützung", "reagiert nicht", "kontakt nicht möglich", "wartezeit", "keine rückmeldung", "telefonisch nicht erreichbar", "keine lösung", "antwort dauert", "kundenberatung fehlt", "keine antwort erhalten", "hotline nicht erreichbar", "keine serviceleistung", "kundensupport schlecht", "kundenbetreuung mangelhaft", "kundenservice reagiert nicht", "service schwer erreichbar", "service antwortet nicht", "nicht geholfen", "unfreundlicher support", "hilft nicht weiter"],
        "Kontaktmöglichkeiten": ["ansprechpartner", "kontakt", "rückruf", "nicht erreichbar", "kein kontakt", "keine kontaktdaten", "hilfe fehlt", "kontaktformular", "keine rückmeldung", "support kontakt", "kein formular", "supportformular fehlt", "kundendienst kontaktieren", "telefon fehlt", "email fehlt", "nur hotline", "kontakt schwierig", "kontaktierung unklar", "kontaktoption fehlt", "keine kontaktmöglichkeit", "nicht ansprechbar", "support schwer erreichbar", "kein livechat", "keine supportmail", "anfrage nicht möglich", "kein rückruf erhalten", "kontaktseite leer", "keine kontaktfunktion", "kontaktmöglichkeit nicht ersichtlich", "anfrageformular fehlt"],
        "Vertrauenswürdigkeit": ["vertrauen", "abzocke", "nicht seriös", "zweifelhaft", "skepsis", "nicht glaubwürdig", "unsicher", "nicht transparent", "betrugsverdacht", "nicht vertrauenswürdig", "datensicherheit", "nicht nachvollziehbar", "intransparente kosten", "unseriös", "abzocker", "misstrauen", "unsicheres gefühl", "nicht überprüfbar", "unvollständig", "zweifelhaftes angebot", "kein impressum", "keine transparenz", "zweifelhaftes verhalten", "verdacht auf betrug", "unsichere kommunikation", "fehlende datensicherheit", "keine aufklärung", "unzuverlässig", "fragwürdig", "irreführend"],
        "Gebühren": ["gebühr", "zinsen", "bearbeitungsgebühr", "kosten", "preis", "zu teuer", "gebühren nicht klar", "versteckte kosten", "nicht kostenlos", "zusatzkosten", "gebühren unklar", "bankgebühren", "gebührenerhöhung", "nicht transparent", "kosten zu hoch", "gebührenänderung", "kontoführungsgebühr", "auszahlungsgebühr", "transaktionsgebühr", "gebühr zu hoch", "zu hohe zinsen", "gebühreninfo fehlt", "unverhältnismäßige gebühr", "gebühr nicht nachvollziehbar", "entgelt", "gebührenbelastung", "gebühr nicht verständlich", "servicegebühr", "provision", "kostenaufstellung fehlt"]
    }

if menu == "Regeln lernen":
    with st.expander("🧠 Kategorien & Schlüsselwörter anzeigen", expanded=False):
        if all_rules:
            for cat, terms in sorted(all_rules.items()):
                with st.container():
                    st.markdown(f"<details><summary><strong>📁 {cat} ({len(terms)} Begriffe)</strong></summary><p>{', '.join(sorted(terms))}</p></details>", unsafe_allow_html=True)
    with st.expander("✏️ Schlüsselwörter verwalten", expanded=False):
        if all_rules:
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
                    continue  # gelöscht
                                all_rules[cat] = list(set(updated_terms))
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
        st.experimental_rerun()


# entfernt aus Analyse-Bereich
rules_file = "custom_rules.json"
default_rules = all_rules.copy() if 'all_rules' in globals() else {}
if os.path.exists(rules_file):
    with open(rules_file, "r") as f:
        loaded_rules = json.load(f)
    # Ersetze Einträge mit denen aus dem Code (nicht nur ergänzen)
    for key, value in default_rules.items():
        if key not in loaded_rules or len(loaded_rules[key]) < len(value):
            loaded_rules[key] = value
    all_rules = loaded_rules
else:
    all_rules = default_rules





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
                for word in text.split():
                    if len(word) > 3 and word not in unmatched_words:
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

            if category_suggestion != "Ignorieren":
                default_index = ["Ignorieren"] + sorted(all_rules.keys()).index(category_suggestion) + 1
            else:
                default_index = 0

            selected = col2.selectbox("Kategorie zuweisen", ["Ignorieren"] + sorted(all_rules.keys()), index=default_index, key=f"assign_{word}")

            if selected != "Ignorieren":
                all_rules[selected].append(word)
                with open("rule_log.csv", "a", encoding="utf-8") as log:
                    import datetime
                    log.write(f"{datetime.datetime.now().isoformat()};{word};{selected}")
                with open(rules_file, "w") as f:
                    json.dump(all_rules, f, indent=2)
                st.success(f"'{word}' wurde der Kategorie '{selected}' hinzugefügt")
                st.experimental_rerun()

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

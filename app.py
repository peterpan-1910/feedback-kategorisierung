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
            st.experimental_rerun()
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
    all_rules = {
        "Login": ["einloggen", "login", "passwort", "anmeldung", "einloggen fehlgeschlagen", "nicht einloggen", "login funktioniert nicht", "authentifizierung fehler", "probleme beim anmelden", "nicht angemeldet", "zugriff", "fehlermeldung", "konto", "abmeldung", "kennwort", "verbindungsfehler", "sitzung", "anmeldedaten", "nutzerdaten", "loginversuch", "keine anmeldung möglich", "probleme mit login", "passwort falsch", "kennwort zurücksetzen", "neues passwort", "loginseite", "loginfenster", "verbindung fehlgeschlagen", "nicht authentifiziert", "anmeldung abgelehnt", "nutzerdaten ungültig", "app meldet fehler", "einloggen unmöglich", "nicht mehr angemeldet", "verbindung wird getrennt", "sitzung beendet", "session läuft ab", "fehlversuch login", "loginblockade"],
        "TAN Probleme": ["tan", "code", "authentifizierung", "bestätigungscode", "code kommt nicht", "tan nicht erhalten", "sms tan", "tan eingabe", "problem mit tan", "keine tan bekommen", "tan ungültig", "tan feld fehlt", "neue tan", "tan abgelaufen", "tan funktioniert nicht", "tan wird nicht akzeptiert", "falscher tan code", "keine tan sms", "tan verzögert", "push tan", "photo tan", "mTAN", "secure tan", "tan app", "tan mail", "email tan", "keine tan gesendet", "2-faktor tan", "tan bleibt leer", "probleme mit authentifizierung"],
        "App abstürze": ["absturz", "hängt", "app stürzt ab", "reagiert nicht", "crash", "app friert ein", "schließt sich", "hängt sich auf", "abgestürzt", "beendet sich", "app hängt sich auf", "app schließt unerwartet", "fehler beim starten", "app startet nicht", "startet nicht mehr", "app funktioniert nicht", "nichts passiert", "plötzlich beendet", "bleibt stehen", "app reagiert nicht", "schwarzer bildschirm", "app lädt nicht", "absturz beim öffnen", "abbruch", "fehler beim öffnen", "startproblem", "app bleibt hängen", "app hängt fest", "schließt nach start", "app stürzt ständig ab"],
        "Fehler / Bugs": ["fehler", "bug", "problem", "funktioniert nicht", "technischer fehler", "defekt", "störung", "anwendungsfehler", "fehlerhaft", "problematisch", "systemfehler", "fehlermeldung", "appfehler", "softwareproblem", "ausnahmefehler", "programmfehler", "fehleranzeige", "abbruchfehler", "nicht verfügbar", "error", "fehlfunktion", "nicht geladen", "seitenfehler", "prozessfehler", "absturzmeldung", "stopp", "hänger", "service nicht erreichbar", "ladefehler", "modulproblem"],
        "Rückzahlungsoptionen": ["rückzahlung", "raten", "tilgung", "zurückzahlen", "zahlung aufteilen", "zahlungspause", "rate ändern", "tilgungsplan", "rückzahlung ändern", "ratenzahlung", "rückzahlungsplan", "abzahlungsoption", "zahlung stunden", "zahlungsaufschub", "zahlung reduzieren", "monatsrate ändern", "zahlung anpassen", "flexible raten", "anpassung rate", "kreditrückzahlung", "anzahlung", "zahlung verschieben", "abzahlungsdauer", "rückzahlungsart", "zahlung in teilen", "verzögerung", "teilrückzahlung", "ablösung kredit", "rate pausieren", "rate aussetzen"],
        "Zahlungsprobleme": ["zahlung", "überweisung", "geld senden", "keine buchung", "zahlung funktioniert nicht", "zahlung fehlgeschlagen", "nicht überwiesen", "nicht angekommen", "probleme mit zahlung", "überweisung hängt", "zahlung nicht möglich", "zahlung abgelehnt", "konnte nicht zahlen", "buchung nicht durchgeführt", "fehlende zahlung", "problem mit lastschrift", "banküberweisung gescheitert", "nicht gebucht", "zahlungsvorgang fehlerhaft", "betrag nicht abgebucht", "zahlung wurde nicht verarbeitet", "lastschrift fehlgeschlagen", "überweisung nicht angekommen", "zahlung nicht bestätigt", "abbuchung fehlt", "keine bestätigung", "geld nicht übertragen", "buchung offen", "geld nicht gutgeschrieben", "fehlermeldung bei zahlung"],
        "Kompliziert / Unklar": ["kompliziert", "nicht verständlich", "nicht intuitiv", "schwer zu verstehen", "unklar", "nicht eindeutig", "umständlich", "nicht nutzerfreundlich", "unverständlich", "verwirrend", "komplizierter vorgang", "nicht nachvollziehbar", "nicht klar erklärt", "unlogisch", "verwirrende navigation", "menü unverständlich", "unklare anleitung", "komplizierte beschreibung", "sperrig", "nicht selbsterklärend", "nicht selbsterklärlich", "verwirrende benennung", "missverständlich", "komplexe struktur", "kein roter faden", "nicht eindeutig beschrieben", "nicht eindeutig erklärt", "nicht selbsterklärende schritte", "nicht klar gegliedert", "undurchsichtig"],
        "Feature-Wünsche / Kritik": ["funktion fehlt", "wäre gut", "feature", "nicht vorgesehen", "funktion sollte", "funktion benötigt", "ich wünsche mir", "bitte ergänzen", "könnte man hinzufügen", "nicht verfügbar", "funktion nicht vorhanden", "funktion deaktiviert", "fehlt in der app", "keine möglichkeit", "nicht vorgesehen", "nicht enthalten", "noch nicht verfügbar", "sollte implementiert werden", "gewünschtes feature", "funktion vermisst", "kein button", "nicht auswählbar", "keine option", "option fehlt", "nicht konfigurierbar", "könnte verbessert werden", "wünschenswert", "funktion erweitern", "benutzerwunsch", "nicht freigeschaltet"],
        "Sprachprobleme": ["englisch", "nicht auf deutsch", "sprache falsch", "nur englisch", "kein deutsch", "nicht lokalisiert", "übersetzung fehlt", "englische sprache", "sprache ändern", "menü englisch", "texte nicht übersetzt", "nur englische version", "übersetzungsfehler", "falsche sprache", "texte nicht verständlich", "fehlende lokalisierung", "keine deutsche sprache", "falsche sprachversion", "spracheinstellungen fehlen", "menü auf englisch", "fehlende übersetzung", "sprachlich unklar", "kein sprachwechsel", "interface englisch", "nicht auf deutsch verfügbar", "englischer hilfetext", "sprachumschaltung

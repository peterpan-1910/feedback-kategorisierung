import streamlit as st
import pandas as pd
import hashlib
import openai
import streamlit.components.v1 as components

# ------------- Benutzerverwaltung (Login) ----------------
USER_CREDENTIALS = {
    "admin2025": hashlib.sha256("admin2025".encode()).hexdigest()
}

def check_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed

# ------------- Regelbasierte Kategorisierung (optimiert mit Trainingsdaten) --------------
def kategorisieren_feedback(feedback, kategorien):
    feedback = feedback.lower()

    if any(word in feedback for word in ["funktion fehlt", "es fehlt", "wäre gut", "sollte möglich sein", "keine sofortüberweisung", "nicht verfügbar", "feature fehlt", "nicht vorgesehen"]):
        return "Feature-Wünsche / Kritik"
    if any(word in feedback for word in ["funktioniert nicht", "geht nicht", "abbruch", "bug", "fehler", "problem", "hängt sich auf", "störung"]):
        return "Fehler / Bugs"
    if any(word in feedback for word in ["übersicht", "unübersichtlich", "struktur verwirrend", "layout verwirrend", "nicht klar"]):
        return "unübersichtlich"
    if any(word in feedback for word in ["langsam", "lädt", "ewig", "dauert lange", "reagiert träge", "hängt"]):
        return "langsam"
    if any(word in feedback for word in ["kontakt", "hotline", "anruf", "nicht erreichbar", "niemand erreichbar", "support", "kundenservice", "rückruf", "telefon", "ansprechperson"]):
        return "Kundenservice"
    if any(word in feedback for word in ["ratenkauf", "rückzahlung", "rate", "zurückzahlen", "tilgung", "zahlung pausieren"]):
        return "Rückzahlungsoptionen"
    if any(word in feedback for word in ["login", "einloggen", "anmeldung", "logout", "anmeldeproblem", "sitzung"]):
        return "Login"
    if any(word in feedback for word in ["absturz", "app hängt", "stürzt ab", "app schließt sich", "schmiert ab"]):
        return "App abstürze"
    if any(word in feedback for word in ["tan", "sms tan", "bestätigungscode", "authentifizierung"]):
        return "TAN Probleme"
    if any(word in feedback for word in ["kosten", "gebühr", "zinsen", "preis", "bearbeitungsgebühr"]):
        return "Gebühren"
    if any(word in feedback for word in ["veraltet", "nicht modern", "altmodisch", "wie aus 2010", "nicht mehr zeitgemäß"]):
        return "UI/UX"
    if any(word in feedback for word in ["kompliziert", "nicht intuitiv", "nicht verständlich", "nicht selbsterklärend", "komplizierte bedienung"]):
        return "Kompliziert / Unklar"
    if any(word in feedback for word in ["vertrauen", "abzocke", "dubios", "nicht vertrauenswürdig", "unsicher", "fragwürdig"]):
        return "Vertrauenswürdigkeit"
    if any(word in feedback for word in ["english", "englisch", "not in german", "sprache falsch"]):
        return "Sprachprobleme"
    if any(word in feedback for word in ["werbung", "angebot", "promo", "aktionscode", "gutschein"]):
        return "Werbung"
    if any(word in feedback for word in ["sicherheit", "sicherheitsbedenken", "schutz", "datenleck", "unbefugter zugriff"]):
        return "Sicherheit"
    if any(word in feedback for word in ["tagesgeld", "zins", "geldanlage", "sparfunktion"]):
        return "Tagesgeld"
    if any(word in feedback for word in ["zahlung", "überweisung", "geld senden", "zahlung geht nicht", "kein transfer"]):
        return "Zahlungsprobleme"
    if any(word in feedback for word in ["ansprechpartner", "kontaktmöglichkeit", "rückruf", "niemand erreichbar"]):
        return "Kontaktmöglichkeiten"
    return "Sonstiges"

# ------------- GPT-Kategorisierung (optional bei API-Key) --------------
def kategorisieren_mit_gpt(feedback, kategorien, api_key):
    openai.api_key = api_key
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
        Du bist ein System zur Textklassifikation. Ordne das folgende deutsche Kundenfeedback genau einer dieser Kategorien zu:
        {', '.join(kategorien)}.
        Feedback: \"{feedback}\"
        Antworte nur mit der Kategorie (ohne weitere Erklärungen).
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler: {str(e)}"

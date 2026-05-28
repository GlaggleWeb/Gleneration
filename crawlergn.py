import os
import random
import requests
from huggingface_hub import HfApi, hf_hub_download

# --- KONFIGURATION ---
DATASET_REPO_ID = "GlaggleWeb/glenerationwissen"
FILE_NAME = "wissen.txt"

ALLGEMEINE_THEMEN = [
    "Deutsche_Sprache", "Grammatik", "Umgangssprache", "Kommunikation", 
    "Alltag", "Kultur", "Natur", "Freundschaft", "Familie", "Sport", 
    "Musik", "Literatur", "Geographie", "Kunst", "Kochen", "Geschichte",
    "Philosophie", "Architektur", "Astronomie", "Biologie", "Chemie"
]

BLACKLIST = [
    "covid", "corona", "virus", "pandemie", "krieg", "medizin", 
    "infektion", "politik", "wahl", "symptom", "erregung", "militär"
]

def fetch_detailed_data():
    """Holt die ausführliche Einleitung eines Wikipedia-Artikels im Reintext."""
    thema = random.choice(ALLGEMEINE_THEMEN)
    
    # Die große MediaWiki-API für ausführliche Plain-Texte (explaintext=1)
    url = "https://de.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": "1",       # Holt die komplette, ausführliche Einleitung
        "explaintext": "1",   # Konvertiert HTML direkt in sauberen Text
        "titles": thema,
        "format": "json"
    }
    headers = {"User-Agent": "KI-LinguistikBot/1.0 (kontakt@deine-email.de)"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            pages = response.json().get("query", {}).get("pages", {})
            page_id = list(pages.keys())[0]
            
            if page_id != "-1":
                title = pages[page_id].get("title", "")
                extract = pages[page_id].get("extract", "")
                
                # Blacklist-Filter
                text_to_check = (title + " " + extract).lower()
                if any(bad_word in text_to_check for bad_word in BLACKLIST):
                    print(f"-> Thema '{title}' übersprungen (Blacklist).")
                    return None
                
                if extract and len(extract) > 200:
                    return f"THEMA: {title}\nTEXT:\n{extract}\n\n--------------------------\n\n"
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")
    return None

def get_existing_content(token):
    """Lädt die existierende Datei von Hugging Face herunter, um Daten anzuhängen."""
    try:
        local_path = hf_hub_download(
            repo_id=DATASET_REPO_ID,
            filename=FILE_NAME,
            repo_type="dataset",
            token=token
        )
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("Alte Modelldaten erfolgreich von Hugging Face geladen.")
        return content
    except Exception:
        print("Keine alte Datei auf Hugging Face gefunden. Erstelle eine neue.")
        return ""

def upload_to_hf(file_name, token):
    """Lädt die Datei auf Hugging Face hoch."""
    api = HfApi()
    try:
        api.upload_file(
            path_or_fileobj=file_name,
            path_in_repo=file_name,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=token,
            commit_message="Erweitere linguistisches Basis-Wissen (ausführlich)"
        )
        print(f"🔥 Erfolg! {file_name} wurde aktualisiert auf Hugging Face hochgeladen.")
    except Exception as e:
        print(f"Upload fehlgeschlagen: {e}")

def main():
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Fehler: HF_TOKEN fehlt!")
        return

    print("1. Lade bestehende Wissensbasis von Hugging Face...")
    existing_text = get_existing_content(token)

    print("2. Suche nach ausführlichem Grammatik-Material...")
    new_content = None
    versuche = 0
    while not new_content and versuche < 10:
        versuche += 1
        new_content = fetch_detailed_data()
        
    if new_content:
        # Alt und Neu zusammenfügen
        all_content = existing_text + new_content
        
        # Lokal speichern
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(all_content)
            
        print("3. Starte Upload der erweiterten Datei...")
        upload_to_hf(FILE_NAME, token)
    else:
        print("Kein passender Text gefunden.")

if __name__ == "__main__":
    main()

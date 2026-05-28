import os
import random
import requests
from huggingface_hub import HfApi

# --- KONFIGURATION ---
DATASET_REPO_ID = "GlaggleWeb/glenerationwissen"  # <-- Exakt an dein Repo angepasst!
FILE_NAME = "wissen.txt"

ALLGEMEINE_THEMEN = [
    "Grammatik", "Umgangssprache", "Kommunikation", 
    "Alltag", "Kultur", "Natur", "Freundschaft", "Familie", "Sport", 
    "Musik", "Literatur", "Geographie", "Kunst", "Kochen", "Geschichte",
    "Philosophie", "Architektur", "Astronomie", "Biologie", "Chemie"
]

BLACKLIST = [
    "covid", "corona", "virus", "pandemie", "krieg", "medizin", 
    "infektion", "politik", "wahl", "symptom", "erregung", "militär"
]

def fetch_clean_data():
    """Holt Text zu einem allgemeinen Thema und filtert Schrott heraus."""
    thema = random.choice(ALLGEMEINE_THEMEN)
    url = f"https://de.wikipedia.org/api/rest_v1/page/summary/{thema}"
    headers = {"User-Agent": "KI-LinguistikBot/1.0 (kontakt@deine-email.de)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "")
            extract = data.get("extract", "")
            
            # Blacklist-Filter
            text_to_check = (title + " " + extract).lower()
            if any(bad_word in text_to_check for bad_word in BLACKLIST):
                print(f"-> Thema '{title}' übersprungen (Blacklist).")
                return None
                
            # Qualitäts-Check: Nur Texte mit Inhalt
            if extract and len(extract) > 150:
                return f"THEMA: {title}\nTEXT: {extract}\n\n--------------------------\n\n"
            else:
                print(f"-> Thema '{title}' war zu kurz.")
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")
    return None

def upload_to_hf(file_name):
    """Lädt die Datei auf Hugging Face hoch."""
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Fehler: HF_TOKEN fehlt in den GitHub-Umgebungsvariablen!")
        return

    api = HfApi()
    try:
        api.upload_file(
            path_or_fileobj=file_name,
            path_in_repo=file_name,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=token,
            commit_message="Erweitere linguistisches Basis-Wissen"
        )
        print(f"🔥 Erfolg! {file_name} wurde auf Hugging Face hochgeladen.")
    except Exception as e:
        print(f"Upload fehlgeschlagen: {e}")

def main():
    print("Suche nach sauberem Grammatik- und Strukturmaterial...")
    
    new_content = None
    versuche = 0
    
    # Der Bot versucht es bis zu 10 Mal, um garantiert einen guten Text zu finden
    while not new_content and versuche < 10:
        versuche += 1
        new_content = fetch_clean_data()
        
    if new_content:
        with open(FILE_NAME, "a", encoding="utf-8") as f:
            f.write(new_content)
        print("Neuen Text lokal gesichert. Starte Upload...")
        upload_to_hf(FILE_NAME)
    else:
        print("Auch nach 10 Versuchen kein passender Text gefunden. Bitte Themenliste prüfen.")

if __name__ == "__main__":
    main()

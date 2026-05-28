import os
import random
import requests
from huggingface_hub import HfApi

# --- KONFIGURATION ---
DATASET_REPO_ID = "GlaggleWeb/DEIN_DATASET_NAME"  # <-- HIER ANPASSEN!
FILE_NAME = "wissen.txt"

# Themen, die ein gutes linguistisches Fundament (Grammatik, Alltag) bieten
ALLGEMEINE_THEMEN = [
    "Deutsche_Sprache", "Grammatik", "Umgangssprache", "Kommunikation", 
    "Alltag", "Kultur", "Natur", "Freundschaft", "Familie", "Sport", 
    "Musik", "Literatur", "Geographie", "Kunst", "Kochen"
]

# Themen, die wir absolut NICHT in der Basis-Datenbank haben wollen
BLACKLIST = [
    "covid", "corona", "virus", "pandemie", "krieg", "medizin", 
    "infektion", "politik", "wahl", "symptom", "erregung"
]

def fetch_clean_data():
    """Holt Text zu einem allgemeinen Thema und filtert Schrott heraus."""
    # Wähle zufällig ein sicheres, allgemeines Thema aus unserer Liste
    thema = random.choice(ALLGEMEINE_THEMEN)
    url = f"https://de.wikipedia.org/api/rest_v1/page/summary/{thema}"
    headers = {"User-Agent": "KI-LinguistikBot/1.0 (kontakt@deine-email.de)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "")
            extract = data.get("extract", "")
            
            # Sicherheits-Check: Enthält der Text Wörter aus der Blacklist?
            text_to_check = (title + " " + extract).lower()
            if any(bad_word in text_to_check for bad_word in BLACKLIST):
                print(f"Überspringe '{title}', da es auf der Blacklist steht.")
                return None
                
            if extract and len(extract) > 100:  # Nur Texte mit vernünftiger Länge
                return f"THEMA: {title}\nTEXT: {extract}\n\n--------------------------\n\n"
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")
    return None

def upload_to_hf(file_name):
    """Lädt die Datei auf Hugging Face hoch."""
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Fehler: HF_TOKEN fehlt!")
        return

    api = HfApi()
    try:
        api.upload_file(
            path_or_fileobj=file_name,
            path_in_repo=file_name,
            repo_id=GlaggleWeb/glenerationwissen,
            repo_type="dataset",
            token=token,
            commit_message="Erweitere linguistisches Basis-Wissen"
        )
        print(f"Erfolgreich zu Hugging Face hochgeladen.")
    except Exception as e:
        print(f"Upload fehlgeschlagen: {e}")

def main():
    print("Suche nach sauberem Grammatik- und Strukturmaterial...")
    new_content = fetch_clean_data()
    
    if new_content:
        with open(FILE_NAME, "a", encoding="utf-8") as f:
            f.write(new_content)
        print("Neuen Text lokal angehängt.")
        upload_to_hf(FILE_NAME)
    else:
        print("Kein passender Text im aktuellen Durchlauf gefunden.")

if __name__ == "__main__":
    main()

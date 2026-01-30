"""
Script: transcribe_video.py
Obiettivo: Trascrivere un video YouTube usando Apify.
"""

import os
import sys
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
from openai import OpenAI

load_dotenv()


def translate_to_italian(text: str) -> str:
    """
    Traduce il testo in italiano usando Claude via OpenRouter.
    Se il testo è già in italiano, lo restituisce così com'è.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[WARN] OPENROUTER_API_KEY mancante, skip traduzione")
        return text
    
    # Se il testo è corto, non vale la pena tradurlo
    if len(text) < 50:
        return text
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL_CLAUDE", "anthropic/claude-3.5-sonnet"),
            messages=[
                {
                    "role": "system",
                    "content": "Sei un traduttore professionale. Traduci il seguente testo in italiano. Se il testo è già in italiano, restituiscilo esattamente come è. Non aggiungere commenti o spiegazioni, solo la traduzione."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=8000,
            temperature=0.3
        )
        translated = response.choices[0].message.content.strip()
        print(f"[INFO] Traduzione completata: {len(text)} -> {len(translated)} chars")
        return translated
    except Exception as e:
        print(f"[WARN] Errore traduzione: {e}, uso testo originale")
        return text

def get_transcription(video_url: str) -> dict:
    """
    Scarica la trascrizione di un video YouTube tramite Apify.
    Restituisce un dizionario con 'text' (testo completo) e 'metadata'.
    """
    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        raise ValueError("APIFY_API_KEY mancante nel file .env")

    client = ApifyClient(api_key)

    # Configurazione input per pintostudio/youtube-transcript-scraper
    run_input = {
        "videoUrl": video_url,
        "language": "it",  # Default italiano, ma lo scraper spesso auto-detecta
        "addVideoInfo": True
    }

    # Esegui l'actor
    run = client.actor("pintostudio/youtube-transcript-scraper").call(run_input=run_input)

    # Recupera i risultati dal dataset
    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
    
    if not dataset_items:
        raise Exception("Nessuna trascrizione trovata o errore nello scraper.")

    # Debug: stampa la struttura dei dati ricevuti
    print(f"[DEBUG] Received {len(dataset_items)} items from Apify")
    for i, item in enumerate(dataset_items):
        print(f"[DEBUG] Item {i} keys: {list(item.keys())}")
        # Stampa un campione dei dati per capire la struttura
        for key, value in item.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"[DEBUG]   {key}: (string, {len(value)} chars)")
            elif isinstance(value, list):
                print(f"[DEBUG]   {key}: (list, {len(value)} items)")
                if value and len(value) > 0:
                    print(f"[DEBUG]     First item type: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"[DEBUG]     First item keys: {list(value[0].keys())}")
            else:
                print(f"[DEBUG]   {key}: {value}")

    # Funzione ricorsiva per estrarre testo da qualsiasi struttura
    def extract_text_recursive(obj, depth=0):
        texts = []
        if depth > 10:  # Protezione ricorsione
            return texts
            
        if isinstance(obj, str):
            if len(obj) > 5:  # Ignora stringhe troppo corte
                texts.append(obj)
        elif isinstance(obj, dict):
            # Cerca campi di testo comuni
            for key in ["text", "content", "segment", "caption", "line", "transcript_text"]:
                if key in obj and obj[key]:
                    result = extract_text_recursive(obj[key], depth + 1)
                    texts.extend(result)
            # Se non trovato, cerca in tutti i valori che sembrano contenere testo
            if not texts:
                for key, value in obj.items():
                    if key.lower() in ["title", "videotitle", "url", "videoid", "id", "duration", "start", "end"]:
                        continue
                    result = extract_text_recursive(value, depth + 1)
                    texts.extend(result)
        elif isinstance(obj, list):
            for item in obj:
                result = extract_text_recursive(item, depth + 1)
                texts.extend(result)
        return texts

    full_text = ""
    title = "Unknown Title"
    
    for item in dataset_items:
        # Estrai il titolo se disponibile
        for title_key in ["title", "videoTitle", "video_title"]:
            if title_key in item and item[title_key]:
                title = item[title_key]
                break
        
        # Formato specifico Apify: item["data"] contiene lista di {start, dur, text}
        if "data" in item and isinstance(item["data"], list):
            for segment in item["data"]:
                if isinstance(segment, dict) and "text" in segment:
                    full_text += segment["text"] + " "
        else:
            # Fallback: Estrai testo ricorsivamente
            texts = extract_text_recursive(item)
            full_text += " ".join(texts) + " "

    if not full_text.strip():
        # Se ancora vuoto, prova a stampare l'intera struttura per debug
        print(f"[DEBUG] Full structure: {json.dumps(dataset_items, indent=2, default=str)[:5000]}")
        raise Exception("Trascrizione vuota - il video potrebbe non avere sottotitoli disponibili.")

    # Traduci automaticamente in italiano se necessario
    print("[INFO] Avvio traduzione in italiano...")
    translated_text = translate_to_italian(full_text.strip())

    return {
        "text": translated_text,
        "metadata": {
            "title": title,
            "url": video_url
        }
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python transcribe_video.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    try:
        result = get_transcription(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Errore: {str(e)}", file=sys.stderr)
        sys.exit(1)

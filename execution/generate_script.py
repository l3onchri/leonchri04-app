"""
Script: generate_script.py
Obiettivo: Generare un nuovo script video basato su trascrizione e ricerca.
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def generate_video_script(original_transcript: str, research_data: str) -> str:
    """
    Genera un nuovo script video integrando l'originale con la ricerca.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL_CLAUDE", "anthropic/claude-3.5-sonnet")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY mancante nel file .env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    prompt = f"""
    Sei uno sceneggiatore video esperto (Video Scriptwriter).
    
    Il tuo compito è creare uno script per un NUOVO video YouTube che sia migliore dell'originale, integrando nuove informazioni trovate online.
    
    INPUT:
    1. Trascrizione video originale (fonte di ispirazione):
    {original_transcript[:10000]}...
    
    2. Ricerca approfondita sui temi (nuove info da includere):
    {research_data[:10000]}...
    
    ISTRUZIONI:
    - Scrivi uno script coinvolgente, con Hook iniziale, Corpo centrale strutturato, e Call to Action.
    - Mantieni un tono vivace e interessante.
    - Integra i fatti trovati nella ricerca per dare valore aggiunto rispetto al video originale.
    - Formato output: Markdown ben formattato.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Sei un creatore di contenuti virali. Scrivi script ottimizzati per l'engagement."},
            {"role": "user", "content": prompt}
        ],
        extra_headers={
            "HTTP-Referer": "https://antigravity.app", 
            "X-Title": "Antigravity App"
        }
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    # Input atteso: Questo script richiede due input specifici.
    # Possiamo passarli come file paths
    if len(sys.argv) < 3:
        print("Uso: python generate_script.py <transcript_file> <research_file>")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    research_path = sys.argv[2]
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            # Se è json, estrai text, altrimenti raw
            content = f.read()
            try:
                data = json.loads(content)
                transcript = data.get("text", content)
            except:
                transcript = content
                
        with open(research_path, 'r', encoding='utf-8') as f:
            research = f.read()
            
        final_script = generate_video_script(transcript, research)
        print(final_script)
        
    except Exception as e:
        print(f"Errore: {str(e)}", file=sys.stderr)
        sys.exit(1)

"""
Script: extract_topics.py
Obiettivo: Estrarre i topic principali da una trascrizione usando Claude.
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI  # Usiamo client OpenAI compatibile con OpenRouter

load_dotenv()

def extract_topics(transcript_text: str) -> list:
    """
    Estrae 3-5 topic principali dalla trascrizione.
    Restituisce una lista di stringhe.
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
    Analizza la seguente trascrizione di un video YouTube ed estrai i 3-5 argomenti principali (Key Topics).
    Restituisci SOLO una lista JSON di stringhe, senza altro testo.
    
    Trascrizione:
    {transcript_text[:15000]}  # Tronca per evitare limiti di token se troppo lungo
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Sei un esperto analista di contenuti. Estrai topic rilevanti e specifici."},
            {"role": "user", "content": prompt}
        ],
        extra_headers={
            "HTTP-Referer": "https://antigravity.app", 
            "X-Title": "Antigravity App"
        }
    )

    content = response.choices[0].message.content.strip()
    
    # Pulisci il markdown json se presente
    if "```json" in content:
        content = content.replace("```json", "").replace("```", "")
    
    try:
        topics = json.loads(content)
        return topics
    except json.JSONDecodeError:
        # Fallback se non è JSON puro
        return [line.strip("- ") for line in content.split("\n") if line.strip()]

if __name__ == "__main__":
    # Leggi da stdin (pipe) o file
    if len(sys.argv) > 1:
        # Se c'è un file argomento, leggilo
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # Altrimenti leggi da stdin
        text = sys.stdin.read()
        
    try:
        data = json.loads(text)
        transcript = data.get("text", "")
    except:
        transcript = text

    if not transcript:
        print("Errore: Nessun testo in input", file=sys.stderr)
        sys.exit(1)

    try:
        topics = extract_topics(transcript)
        print(json.dumps(topics, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Errore: {str(e)}", file=sys.stderr)
        sys.exit(1)

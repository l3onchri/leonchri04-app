"""
Script: research_topics.py
Obiettivo: Ricercare approfondimenti sui topic usando Perplexity Sonar.
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def research_topics(topics: list) -> str:
    """
    Esegue una ricerca online per ogni topic e compila un report.
    Usa Perplexity Sonar via OpenRouter.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL_PERPLEXITY", "perplexity/sonar")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY mancante nel file .env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    combined_research = "# Risultati Ricerca\n\n"

    # Per semplicità, facciamo un'unica chiamata grossa o una per topic.
    # Una chiamata per topic è più accurata ma più lenta costosa. 
    # Optiamo per una chiamata unica raggruppata se sono pochi, o loop.
    # Utente vuole "ricercare online questi topics". Facciamo un loop.
    
    for topic in topics:
        # Processing topic silently to avoid Windows encoding issues
        
        prompt = f"""
        Effettua una ricerca approfondita sul seguente argomento: "{topic}".
        Fornisci dati recenti, fatti interessanti e dettagli che non sono ovvi.
        Includi le fonti URL alla fine.
        """

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Sei un ricercatore esperto. Usa il web per trovare informazioni aggiornate."},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "https://antigravity.app", 
                    "X-Title": "Antigravity App"
                }
            )
            
            result = response.choices[0].message.content
            combined_research += f"## {topic}\n\n{result}\n\n---\n\n"
            
        except Exception as e:
            combined_research += f"## {topic}\n\nErrore durante la ricerca: {str(e)}\n\n"

    return combined_research

if __name__ == "__main__":
    # Input atteso: JSON list of strings da stdin o file
    input_data = []
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()
        
    try:
        input_data = json.loads(raw)
        if not isinstance(input_data, list):
            raise ValueError("L'input deve essere una lista JSON di argomenti.")
    except Exception as e:
        print(f"Errore lettura input: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        report = research_topics(input_data)
        print(report)
    except Exception as e:
        print(f"Errore: {str(e)}", file=sys.stderr)
        sys.exit(1)

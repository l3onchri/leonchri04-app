# Execution Scripts

Questa directory contiene gli script Python deterministici per l'esecuzione.

## Principi

- **Deterministici**: Stesso input = stesso output
- **Ben commentati**: Codice chiaro e documentato
- **Testabili**: Facili da verificare
- **Affidabili**: Gestione errori robusta

## Struttura Consigliata

```python
"""
Nome Script: nome_script.py
Descrizione: Breve descrizione di cosa fa lo script
Input: Descrizione input atteso
Output: Descrizione output prodotto
"""

import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

def main():
    """Funzione principale."""
    pass

if __name__ == "__main__":
    main()
```

## Convenzioni

- Nomi file in snake_case
- Documentazione con docstring
- Gestione errori con try/except
- Logging appropriato

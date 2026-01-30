# Guida al Deployment di LEONCHRI04 GENERATOR

Questa applicazione è completamente dockerizzata per un deployment facile e veloce su qualsiasi server (VPS, AWS, DigitalOcean, ecc.).

## Prerequisiti
- **Docker** e **Docker Compose** installati sul server.
- Le tue chiavi API (OpenRouter, Apify).

## 1. Preparazione
Copia l'intera cartella del progetto sul tuo server. Puoi usare `git` o SCP.

Assicurati di avere il file `.env` nella root del progetto con le tue chiavi:

```env
APIFY_API_KEY=tua_chiave_apify
OPENROUTER_API_KEY=tua_chiave_openrouter
OPENROUTER_MODEL_CLAUDE=google/gemini-2.0-flash-001
OPENROUTER_MODEL_PERPLEXITY=perplexity/sonar
```

## 2. Configurazione per Produzione
Nel file `.env`, aggiungi o modifica queste variabili per la produzione:

```env
# URL del backend (come visto dal browser dell'utente)
NEXT_PUBLIC_API_URL=http://tuo-indrizzo-ip-o-dominio:8000

# Domini autorizzati a chiamare il backend (CORS)
ALLOWED_ORIGINS=http://tuo-indrizzo-ip-o-dominio:3000
```

> **Nota**: Se stai testando in locale, puoi lasciare i valori di default (localhost).

## 3. Avvio
Dalla cartella principale del progetto, esegui:

```bash
docker-compose up --build -d
```

- `--build`: Costruisce le immagini (necessario la prima volta).
- `-d`: Esegue in background (detached mode).

## 4. Verifica
- **Frontend**: Apri `http://tuo-server:3000` nel browser.
- **Backend API**: `http://tuo-server:8000/docs` (Swagger UI).
- **Log**: Per vedere se tutto gira bene, usa `docker-compose logs -f`.

## 5. Aggiornamenti
Se modifichi il codice, per aggiornare il server:

1. Scarica il nuovo codice (`git pull`).
2. Riavvia i container con rebuild:
   ```bash
   docker-compose up --build -d
   ```

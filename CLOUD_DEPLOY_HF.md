# Guida al Deploy: Hugging Face + Vercel

Questa guida ti spiega passo passo come mettere online l'app gratuitamente e senza usare Docker sul tuo PC.

## Parte 1: Backend su Hugging Face Spaces

Hugging Face Spaces ospiterà il nostro server Python (il "cervello").

1.  **Crea lo Space**:
    *   Vai su [Hugging Face Spaces](https://huggingface.co/spaces) e clicca "Create new Space".
    *   **Space name**: `antigravity-backend` (o simile).
    *   **License**: MIT (opzionale).
    *   **SDK**: Seleziona **Docker** (Molto importante!).
    *   **Space hardware**: Mantieni "CPU Basic (Free)".
    *   Clicca "Create Space".

2.  **Carica i file (IMPORTANTE)**:
    *   Una volta creato lo space, vedrai una pagina che dice "App not running yet". Clicca su **"Files"** in alto a destra.
    *   Clicca **"Add file" -> "Upload files"**.
    *   Devi caricare i file in questo modo esatto (tutti nella "radice" dello Space):
        1.  Tutto il contenuto della cartella `backend/` (`Dockerfile`, `main.py`, `requirements0.txt`, `README.md`, e la cartella `api`).
        2.  **MOLTO IMPORTANTE**: Devi caricare anche la cartella `execution/` che si trova fuori da `backend`.
    
    *   **Come fare l'upload corretto**:
        *   Trascina lo file di `backend`: `Dockerfile`, `main.py`, `requirements0.txt`, `README.md`.
        *   Trascina la cartella `backend/api` così com'è.
        *   Trascina la cartella `execution` (quella che sta nella cartella principale del progetto) così com'è.
    
    *   **Struttura finale che devi vedere su Hugging Face**:
        ```
        /api/
        /execution/
        Dockerfile
        main.py
        requirements0.txt
        README.md
        ```

3.  **Aggiungi le API KEY (Secrets)**:
    *   Nello Space, vai su **"Settings"** (in alto).
    *   Scorri fino a **"Variables and secrets"**.
    *   Clicca **"New secret"** per ogni chiave che hai nel tuo `.env` locale:
        *   `APIFY_API_KEY`: Incolla la tua chiave Apify.
        *   `OPENROUTER_API_KEY`: Incolla la tua chiave OpenRouter.
        *   `ALLOWED_ORIGINS`: Inserisci `*` per testare, oppure l'URL che Vercel ti darà (es. `https://antigravity-frontend.vercel.app`).

4.  **Attendi il Build**:
    *   Torna su **"App"**. Vedrai "Building". Attendi qualche minuto.
    *   Quando diventa "Running", copia l'indirizzo web in alto (es. `https://huggingface.co/spaces/tuonome/antigravity-backend` -> copia il link diretto all'iframe se serve, ma solitamente l'API è `https://tuonome-antigravity-backend.hf.space`).
    *   **TEST**: Aggiungi `/api/health` alla fine dell'URL (es. `https://tuonome-antigravity-backend.hf.space/api/health`). Se vedi `{"status":"healthy"}`, funziona!

---

## Parte 2: Frontend su Vercel

Vercel ospiterà il sito web (Next.js).

1.  **Prepara il codice su GitHub**:
    *   Assicurati che tutto il tuo progetto (la cartella principale `app-antigravity`) sia su un repository GitHub aggiornato.

2.  **Crea il progetto su Vercel**:
    *   Vai su [Vercel Dashboard](https://vercel.com/dashboard) e clicca "Add New..." -> "Project".
    *   Seleziona il tuo repository GitHub.
    *   Configura il progetto:
        *   **Framework Preset**: Next.js (dovrebbe rilevarlo automatico).
        *   **Root Directory**: Clicca "Edit" e seleziona la cartella `frontend`.
        *   **IMPORTANTE**: Se Vercel si lamenta della build, assicurati che la cartella `src` sia dentro `frontend`.
    *   **Environment Variables**: Espandi la sezione. Aggiungi:
        *   Nome: `NEXT_PUBLIC_API_URL`
        *   Valore: L'URL del tuo backend Hugging Face (senza slash finale, es. `https://tuonome-antigravity-backend.hf.space`).

3.  **Deploy**:
    *   Clicca "Deploy".
    *   Vercel costruirà il sito. In meno di un minuto dovrebbe essere online!

4.  **Collegamento Finale**:
    *   Copia l'URL del sito Vercel (es. `https://antigravity-frontend.vercel.app`).
    *   Torna su Hugging Face -> Settings -> Secrets.
    *   Aggiorna `ALLOWED_ORIGINS` con questo URL (se avevi messo `*` puoi lasciarlo, ma è meno sicuro).

---

## Risoluzione Problemi Comuni

*   **Il Backend da errore "OpenAI Error"**: Hai dimenticato di impostare i Secrets nelle Settings di Hugging Face.
*   **Il Frontend non carica i dati**: Controlla la Console del browser (F12). Se dice "CORS error", controlla `ALLOWED_ORIGINS` su Hugging Face. Se dice "404 Not Found", controlla che `NEXT_PUBLIC_API_URL` sia corretto e non abbia uno slash `/` di troppo alla fine.

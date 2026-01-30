"""
Backend API con FastAPI.
Entry point principale per l'API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Carica variabili d'ambiente
load_dotenv()

# Inizializza app FastAPI
app = FastAPI(
    title="App API",
    description="API Backend",
    version="1.0.0"
)

# Configura CORS per permettere richieste dal frontend
# In produzione, ALLOWED_ORIGINS dovrebbe contenere l'URL di Vercel (es. https://myapp.vercel.app)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

# Aggiungi wildcard per Vercel preview deployments (opzionale, ma utile)
# Attenzione: allow_origins=["*"] non funziona con allow_credentials=True in alcuni browser/configurazioni,
# ma HF Spaces spesso richiede flessibilità. Per ora manteniamo la lista esplicita ma estendibile.

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint di health check."""
    return {"status": "ok", "message": "API is running"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Import e include routers
try:
    # Tentativo 1: Import relativo (es. esecuzione come modulo) o root flat
    from api import endpoints
except ImportError as e1:
    print(f"Tentativo 1 (flat) fallito: {e1}")
    try:
        # Tentativo 2: Import assoluto (es. esecuzione da root con cartella backend)
        from backend.api import endpoints
    except ImportError as e2:
        print(f"Tentativo 2 (nested) fallito: {e2}")
        # Se falliscono entrambi, probabilmente l'errore è nel primo (dipendenze interne)
        # o non siamo né in root né fuori. Rilanciamo l'errore più significativo.
        raise e1

app.include_router(endpoints.router, prefix="/api", tags=["video-processing"])


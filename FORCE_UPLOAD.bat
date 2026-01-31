@echo off
echo ==========================================
echo   PULIZIA E CARICAMENTO SU HUGGING FACE
echo ==========================================
echo.
echo Questo script forzera' il caricamento della cartella HF_UPLOAD_READY
echo cancellando e sovrascrivendo tutto il "casino" online.
echo.
set /p TOKEN="Incolla il tuo TOKEN di Hugging Face (lo trovi in Settings -> Access Tokens): "

if "%TOKEN%"=="" (
    echo Token non inserito!
    pause
    exit /b
)

echo.
echo Preparazione caricamente...
cd HF_UPLOAD_READY

:: Rimuovi git precedente se esiste
if exist .git rmdir /s /q .git

:: Inizializza nuovo repo e committa tutto
git init -b main
git config user.email "deploy@antigravity.com"
git config user.name "Antigravity Deployer"
git add .
git commit -m "Clean Manual Upload"

echo.
echo Caricamento in corso... (Attendere...)
git push --force https://l3onchri:%TOKEN%@huggingface.co/spaces/l3onchri/antigravity-backend main

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo   SUCCESSO! Space ripulito e aggiornato.
    echo   Vai su Hugging Face e dovresti vedere "Building".
) else (
    echo   ERRORE! Controlla di aver incollato il token corretto.
)
echo ==========================================
pause

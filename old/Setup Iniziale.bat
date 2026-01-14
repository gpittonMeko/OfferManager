@echo off
REM OfferManager - Setup e Installazione Dipendenze
cd /d "%~dp0"
title OfferManager - Setup Iniziale
color 0A
echo.
echo ================================================================
echo                   OFFERMANAGER - SETUP
echo ================================================================
echo.
echo Questo script installera' tutte le dipendenze necessarie.
echo.
pause
echo.
echo Installazione dipendenze in corso...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
if errorlevel 1 (
    echo.
    echo ================================================================
    echo ERRORE nell'installazione!
    echo ================================================================
    echo.
    echo Python non e' installato o non e' nel PATH.
    echo.
    echo Scarica Python da: https://www.python.org/downloads/
    echo Durante l'installazione, seleziona "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo.
echo ================================================================
echo INSTALLAZIONE COMPLETATA CON SUCCESSO!
echo ================================================================
echo.
echo Ora puoi usare OfferManager con doppio click su:
echo.
echo   - "Avvia Desktop App.bat"    [GUI con finestra]
echo   - "Avvia Web App.bat"        [Interfaccia web]
echo   - "Avvia Menu CLI.bat"       [Menu testuale]
echo.
echo ================================================================
pause


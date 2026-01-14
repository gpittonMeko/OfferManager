@echo off
cd /d "%~dp0"
title Crea Eseguibile
cls
echo.
echo ================================================================
echo             CREAZIONE ESEGUIBILE .EXE
echo ================================================================
echo.
echo Questo creerà OfferManager.exe che funziona senza Python
echo.
pause

REM Installa PyInstaller se non presente
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo.
    echo Installazione PyInstaller...
    pip install pyinstaller
)

echo.
echo Creazione eseguibile in corso...
echo Attendi qualche minuto...
echo.

pyinstaller --name=OfferManager --onefile --windowed --add-data="templates;templates" desktop_app_demo.py

cls
echo.
echo ================================================================
echo                     COMPLETATO!
echo ================================================================
echo.
if exist "dist\OfferManager.exe" (
    echo ✅ Eseguibile creato con successo!
    echo.
    echo File: dist\OfferManager.exe
    echo.
    echo Puoi:
    echo   - Copiarlo su altri PC
    echo   - Funziona senza Python
    echo   - Doppio click per avviare
    echo.
) else (
    echo ❌ Errore nella creazione
    echo.
)
echo ================================================================
pause

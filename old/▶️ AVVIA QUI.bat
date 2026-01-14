@echo off
cd /d "%~dp0"
title OfferManager
color 0B
cls
echo.
echo ================================================================
echo.
echo                    OFFERMANAGER
echo            Configuratore di Offerte
echo.
echo ================================================================
echo.
python desktop_app_demo.py
if errorlevel 1 (
    cls
    echo.
    echo ================================================================
    echo                        ERRORE!
    echo ================================================================
    echo.
    echo Devi prima installare le dipendenze!
    echo.
    echo SOLUZIONE:
    echo    Doppio click su: "Setup Iniziale.bat"
    echo.
    echo Poi riprova questo file.
    echo.
    echo ================================================================
    pause
)


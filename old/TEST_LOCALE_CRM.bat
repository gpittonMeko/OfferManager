@echo off
REM Test CRM locale - Versione semplificata
cd /d "%~dp0"
title OfferManager CRM Test
cls
echo.
echo ================================================================
echo           OFFERMANAGER CRM - TEST LOCALE
echo ================================================================
echo.
echo Avvio CRM con dashboard commerciali...
echo.
start http://localhost:5000
echo.
echo Browser in apertura su: http://localhost:5000
echo.
echo Login Demo:
echo    Username: marco
echo    Password: demo123
echo.
echo ================================================================
echo.
python crm_app.py
if errorlevel 1 (
    echo.
    echo ERRORE! Esegui prima:
    echo    pip install flask flask-sqlalchemy
    pause
)


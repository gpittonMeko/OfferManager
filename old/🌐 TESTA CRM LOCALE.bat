@echo off
cd /d "%~dp0"
title OfferManager CRM - Test Locale
cls
echo.
echo ================================================================
echo          OFFERMANAGER CRM - TEST LOCALE
echo ================================================================
echo.
echo Avvio CRM con dashboard e analytics...
echo.
echo Dopo l'avvio, apri il browser:
echo.
echo     http://localhost:5000
echo.
echo Login Demo:
echo     Username: marco
echo     Password: demo123
echo.
echo Per fermare: CTRL+C
echo.
echo ================================================================
echo.
python crm_app.py
pause


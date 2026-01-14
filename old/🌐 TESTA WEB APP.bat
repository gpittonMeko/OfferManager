@echo off
cd /d "%~dp0"
title OfferManager - Web App
cls
echo.
echo ================================================================
echo              OFFERMANAGER - WEB APP
echo ================================================================
echo.
echo Avvio server web...
echo.
echo Dopo l'avvio, apri il browser e vai su:
echo.
echo     http://localhost:5000
echo.
echo Oppure premi CTRL+Click sul link qui sotto:
echo     http://127.0.0.1:5000
echo.
echo Per fermare: Premi CTRL+C
echo.
echo ================================================================
echo.
python app.py
pause


@echo off
cd /d "%~dp0"
title OfferManager CRM
cls
echo Installazione dipendenze...
pip install -q flask flask-sqlalchemy 2>nul
echo Avvio app su http://localhost:5000
echo.
echo Login: marco / demo123
echo.
python crm_app.py
pause




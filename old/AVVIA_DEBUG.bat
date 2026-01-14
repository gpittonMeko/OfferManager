@echo off
cd /d "%~dp0"
title OfferManager CRM - Debug
cls
echo ======================================
echo Installazione dipendenze...
echo ======================================
echo.
pip install flask flask-sqlalchemy
echo.
echo ======================================
echo Avvio app...
echo ======================================
echo.
python crm_app.py
pause




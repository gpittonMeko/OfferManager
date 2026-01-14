@echo off
cd /d "%~dp0"
title Riavvia CRM
cls
echo.
echo ================================================================
echo              RIAVVIO CRM CON NUOVA DASHBOARD
echo ================================================================
echo.
echo Chiusura processi Python esistenti...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Avvio CRM aggiornato...
echo.
start http://localhost:5000
echo.
echo Browser in apertura...
echo.
echo Login: marco / demo123
echo.
echo ================================================================
echo.
python crm_app.py
pause


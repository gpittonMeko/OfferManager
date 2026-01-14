@echo off
cd /d "%~dp0"
title OfferManager CRM Completo
cls
echo.
echo ================================================================
echo           OFFERMANAGER CRM - VERSIONE COMPLETA
echo ================================================================
echo.
echo Incluso:
echo   ✅ Generatore offerte automatico
echo   ✅ Dashboard con grafici
echo   ✅ Gestione lead e contatti
echo   ✅ Vista Excel per mese
echo   ✅ 30+ prodotti integrati (MIR/UR/Unitree)
echo.
echo Avvio...
echo.
start http://localhost:5000
timeout /t 2 /nobreak >nul
echo Browser in apertura...
echo.
echo Login: marco / demo123
echo.
echo ================================================================
echo.
python app_completa.py
pause


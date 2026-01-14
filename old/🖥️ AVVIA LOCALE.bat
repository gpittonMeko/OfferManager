@echo off
cd /d "%~dp0"
title OfferManager CRM - Locale
cls
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║         🖥️  AVVIO OFFERMANAGER CRM IN LOCALE 🖥️             ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Installazione dipendenze e avvio app...
echo.

REM Installa dipendenze
echo  📦 Verifica dipendenze...
pip install -q flask flask-sqlalchemy 2>nul
if errorlevel 1 (
    echo  ⚠️  Installazione dipendenze in corso...
    pip install flask flask-sqlalchemy
)

echo  ✅ Dipendenze OK
echo.
echo  🚀 Avvio app su http://localhost:5000
echo.
echo  👤 Login:
echo     Username: marco
echo     Password: demo123
echo.
echo  ⚠️  Per fermare: Chiudi questa finestra
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Avvia app
python crm_app.py

pause






















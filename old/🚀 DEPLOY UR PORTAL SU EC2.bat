@echo off
cd /d "%~dp0"
title Deploy UR Portal su EC2 - 13.53.183.146
cls
color 0B
echo.
echo ================================================================
echo     🚀 DEPLOY UR PORTAL SU EC2
echo ================================================================
echo.
echo IP EC2: 13.53.183.146:8000
echo.
echo Questo script caricherà i file modificati per UR Portal
echo sulla macchina EC2 e riavvierà il servizio.
echo.
echo ================================================================
echo.

REM Verifica file
if not exist "ur_portal_direct.py" (
    echo ❌ ERRORE: ur_portal_direct.py non trovato!
    pause
    exit /b 1
)

if not exist "ur_portal_integration.py" (
    echo ❌ ERRORE: ur_portal_integration.py non trovato!
    pause
    exit /b 1
)

if not exist "crm_app_completo.py" (
    echo ❌ ERRORE: crm_app_completo.py non trovato!
    pause
    exit /b 1
)

if not exist "templates\app_mekocrm_completo.html" (
    echo ❌ ERRORE: templates\app_mekocrm_completo.html non trovato!
    pause
    exit /b 1
)

echo ✓ Tutti i file trovati
echo.

REM Chiedi percorso chiave
set /p KEY_PATH="Inserisci il percorso completo della chiave .pem (es: C:\Users\user\chiave.pem): "
if "%KEY_PATH%"=="" (
    echo ❌ ERRORE: Percorso chiave non inserito!
    pause
    exit /b 1
)

if not exist "%KEY_PATH%" (
    echo ❌ ERRORE: File chiave non trovato: %KEY_PATH%
    pause
    exit /b 1
)

set EC2_IP=13.53.183.146
set EC2_USER=ubuntu

echo.
echo ================================================================
echo  📤 Caricamento file su EC2...
echo ================================================================
echo.

echo [1/4] ur_portal_direct.py...
scp -i "%KEY_PATH%" -o StrictHostKeyChecking=no ur_portal_direct.py %EC2_USER%@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ❌ Errore caricamento ur_portal_direct.py
    pause
    exit /b 1
)
echo ✓ Caricato

echo.
echo [2/4] ur_portal_integration.py...
scp -i "%KEY_PATH%" -o StrictHostKeyChecking=no ur_portal_integration.py %EC2_USER%@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ❌ Errore caricamento ur_portal_integration.py
    pause
    exit /b 1
)
echo ✓ Caricato

echo.
echo [3/4] crm_app_completo.py...
scp -i "%KEY_PATH%" -o StrictHostKeyChecking=no crm_app_completo.py %EC2_USER%@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ❌ Errore caricamento crm_app_completo.py
    pause
    exit /b 1
)
echo ✓ Caricato

echo.
echo [4/4] templates/app_mekocrm_completo.html...
scp -i "%KEY_PATH%" -o StrictHostKeyChecking=no templates\app_mekocrm_completo.html %EC2_USER%@%EC2_IP%:/home/ubuntu/offermanager/templates/
if errorlevel 1 (
    echo ❌ Errore caricamento app_mekocrm_completo.html
    pause
    exit /b 1
)
echo ✓ Caricato

echo.
echo ================================================================
echo  🔄 Riavvio servizio...
echo ================================================================
echo.

ssh -i "%KEY_PATH%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_IP% "cd /home/ubuntu/offermanager && sudo systemctl restart offermanager && sleep 2 && sudo systemctl status offermanager --no-pager -l"
if errorlevel 1 (
    echo ⚠ Impossibile riavviare automaticamente
    echo.
    echo Esegui manualmente:
    echo   ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP%
    echo   sudo systemctl restart offermanager
) else (
    echo ✓ Servizio riavviato
)

echo.
echo ================================================================
echo  ✅ DEPLOY COMPLETATO!
echo ================================================================
echo.
echo 🌐 App disponibile su: http://13.53.183.146:8000/app
echo.
echo 📋 Prossimi passi:
echo    1. Apri http://13.53.183.146:8000/app
echo    2. Accedi con le tue credenziali
echo    3. Prova la sincronizzazione UR Portal
echo    4. Controlla i log nella modale
echo.
pause




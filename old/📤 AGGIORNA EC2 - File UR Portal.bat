@echo off
cd /d "%~dp0"
title Aggiorna EC2 - File UR Portal Integration
cls
echo.
echo ================================================================
echo        AGGIORNA EC2 - File UR Portal Integration
echo ================================================================
echo.
echo Questo script carica i file modificati per l'integrazione UR
echo sulla macchina EC2.
echo.
echo ================================================================
echo.

REM Verifica che i file esistano
if not exist "ur_portal_direct.py" (
    echo ERRORE: File ur_portal_direct.py non trovato!
    pause
    exit /b 1
)

if not exist "ur_portal_integration.py" (
    echo ERRORE: File ur_portal_integration.py non trovato!
    pause
    exit /b 1
)

if not exist "crm_app_completo.py" (
    echo ERRORE: File crm_app_completo.py non trovato!
    pause
    exit /b 1
)

if not exist "templates\app_mekocrm_completo.html" (
    echo ERRORE: File templates\app_mekocrm_completo.html non trovato!
    pause
    exit /b 1
)

echo ✓ Tutti i file trovati
echo.

REM Chiedi IP EC2
set /p EC2_IP="Inserisci l'IP pubblico della macchina EC2: "
if "%EC2_IP%"=="" (
    echo ERRORE: IP non inserito!
    pause
    exit /b 1
)

REM Chiedi percorso chiave
set /p KEY_PATH="Inserisci il percorso completo della chiave .pem (es: C:\Users\user\chiave.pem): "
if "%KEY_PATH%"=="" (
    echo ERRORE: Percorso chiave non inserito!
    pause
    exit /b 1
)

if not exist "%KEY_PATH%" (
    echo ERRORE: File chiave non trovato: %KEY_PATH%
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  Caricamento file su EC2...
echo ================================================================
echo.

REM Carica i file modificati
echo [1/4] Caricamento ur_portal_direct.py...
scp -i "%KEY_PATH%" ur_portal_direct.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ERRORE durante il caricamento di ur_portal_direct.py
    pause
    exit /b 1
)
echo ✓ ur_portal_direct.py caricato

echo.
echo [2/4] Caricamento ur_portal_integration.py...
scp -i "%KEY_PATH%" ur_portal_integration.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ERRORE durante il caricamento di ur_portal_integration.py
    pause
    exit /b 1
)
echo ✓ ur_portal_integration.py caricato

echo.
echo [3/4] Caricamento crm_app_completo.py...
scp -i "%KEY_PATH%" crm_app_completo.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/
if errorlevel 1 (
    echo ERRORE durante il caricamento di crm_app_completo.py
    pause
    exit /b 1
)
echo ✓ crm_app_completo.py caricato

echo.
echo [4/4] Caricamento templates/app_mekocrm_completo.html...
scp -i "%KEY_PATH%" templates\app_mekocrm_completo.html ubuntu@%EC2_IP%:/home/ubuntu/offermanager/templates/
if errorlevel 1 (
    echo ERRORE durante il caricamento di app_mekocrm_completo.html
    pause
    exit /b 1
)
echo ✓ app_mekocrm_completo.html caricato

echo.
echo ================================================================
echo  Riavvio servizio su EC2...
echo ================================================================
echo.

REM Riavvia il servizio
echo Eseguo riavvio del servizio...
ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "sudo systemctl restart offermanager"
if errorlevel 1 (
    echo AVVISO: Impossibile riavviare il servizio automaticamente.
    echo Esegui manualmente su EC2:
    echo   sudo systemctl restart offermanager
) else (
    echo ✓ Servizio riavviato
)

echo.
echo ================================================================
echo  ✅ AGGIORNAMENTO COMPLETATO!
echo ================================================================
echo.
echo I file sono stati caricati su EC2 e il servizio è stato riavviato.
echo.
echo Verifica lo stato con:
echo   ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "sudo systemctl status offermanager"
echo.
echo Oppure apri nel browser:
echo   http://%EC2_IP%
echo.
pause




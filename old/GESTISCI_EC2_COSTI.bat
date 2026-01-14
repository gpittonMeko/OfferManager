@echo off
cd /d "%~dp0"
title Gestione Costi EC2
cls
echo.
echo ================================================================
echo         GESTIONE COSTI ISTANZA EC2
echo ================================================================
echo.
echo Per RISPARMIARE:
echo   - Quando NON usi l'app, STOPPA l'istanza = 0 euro/giorno
echo   - Quando serve, RIAVVIA l'istanza
echo.
echo Costi:
echo   - Istanza RUNNING: ~0.27 euro/giorno (~8 euro/mese)
echo   - Istanza STOPPED: 0 euro/giorno (paghi solo storage ~0.10 euro/mese)
echo.
echo ================================================================
echo.
set /p INSTANCE_ID="Inserisci Instance ID (es. i-0123456789abcdef): "
echo.
echo Cosa vuoi fare?
echo   1. STOPPA istanza (0 euro/giorno)
echo   2. AVVIA istanza
echo   3. Vedi STATO istanza
echo   4. Esci
echo.
set /p SCELTA="Scelta (1-4): "
echo.

if "%SCELTA%"=="1" (
    echo Stopping istanza %INSTANCE_ID%...
    aws ec2 stop-instances --instance-ids %INSTANCE_ID% --region eu-west-1
    echo.
    echo Istanza in arresto. Costi ridotti a 0 euro/giorno!
    echo Quando serve riavviala con opzione 2.
)

if "%SCELTA%"=="2" (
    echo Avvio istanza %INSTANCE_ID%...
    aws ec2 start-instances --instance-ids %INSTANCE_ID% --region eu-west-1
    echo.
    echo Istanza in avvio... (circa 1 minuto)
    echo Recupero nuovo IP pubblico...
    timeout /t 30 /nobreak >nul
    aws ec2 describe-instances --instance-ids %INSTANCE_ID% --region eu-west-1 --query "Reservations[0].Instances[0].PublicIpAddress" --output text > temp_ip.txt
    set /p NEW_IP=<temp_ip.txt
    del temp_ip.txt
    echo.
    echo Istanza avviata!
    echo Nuovo IP: %NEW_IP%
    echo Accedi a: http://%NEW_IP%
)

if "%SCELTA%"=="3" (
    echo Stato istanza %INSTANCE_ID%:
    aws ec2 describe-instances --instance-ids %INSTANCE_ID% --region eu-west-1 --query "Reservations[0].Instances[0].[State.Name,PublicIpAddress]" --output table
)

echo.
echo ================================================================
echo.
pause



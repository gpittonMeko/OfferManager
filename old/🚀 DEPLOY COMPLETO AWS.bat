@echo off
cd /d "%~dp0"
title Deploy Completo AWS
color 0B
cls
echo.
echo ================================================================
echo     OFFERMANAGER CRM - DEPLOY AUTOMATICO COMPLETO AWS
echo ================================================================
echo.
echo Questo script:
echo   ✅ Crea istanza EC2 automaticamente
echo   ✅ Carica tutti i file
echo   ✅ Installa tutto
echo   ✅ Avvia il servizio
echo   ✅ Apre il browser
echo.
echo ================================================================
echo.
pause

echo.
echo [INFO] Per usare questo script serve AWS CLI configurato.
echo.
echo Hai AWS CLI configurato? (s/N)
set /p AWS_CLI=

if /i NOT "%AWS_CLI%"=="s" (
    echo.
    echo ================================================================
    echo   INSTALLAZIONE AWS CLI
    echo ================================================================
    echo.
    echo 1. Scarica da: https://aws.amazon.com/cli/
    echo 2. Installa
    echo 3. Configura con: aws configure
    echo    (Inserisci Access Key e Secret Key da IAM)
    echo.
    echo Poi riavvia questo script.
    echo ================================================================
    pause
    exit /b
)

echo.
echo ================================================================
echo   OPZIONI DEPLOY
echo ================================================================
echo.
echo   1. Ho già un'istanza EC2 - Solo deploy codice
echo   2. Crea nuova istanza EC2 + Deploy completo
echo.
set /p OPZIONE="Scegli (1/2): "

if "%OPZIONE%"=="1" goto deploy_only
if "%OPZIONE%"=="2" goto full_deploy
goto end

:deploy_only
echo.
set /p IP_EC2="Inserisci IP pubblico EC2: "
echo.
echo Deploy su %IP_EC2%...
powershell -ExecutionPolicy Bypass -File "deploy_to_aws.ps1" -IpEC2 "%IP_EC2%"
goto end

:full_deploy
echo.
echo ================================================================
echo   CREAZIONE ISTANZA EC2
echo ================================================================
echo.
echo Creazione in corso... (può richiedere 2-3 minuti)
echo.

REM Crea istanza con AWS CLI
aws ec2 run-instances ^
    --image-id ami-0c55b159cbfafe1f0 ^
    --instance-type t2.micro ^
    --key-name LLM_14 ^
    --security-group-ids sg-XXXXXX ^
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=OfferManager-CRM}]" ^
    > ec2_instance.json

if errorlevel 1 (
    echo.
    echo ERRORE nella creazione istanza!
    echo.
    echo Usa AWS Console manuale o verifica configurazione AWS CLI
    pause
    exit /b 1
)

echo.
echo ✅ Istanza creata!
echo.
echo Attendi che sia pronta (30-60 secondi)...
timeout /t 60 /nobreak

REM Estrai IP pubblico
for /f "tokens=*" %%i in ('aws ec2 describe-instances --filters "Name=tag:Name,Values=OfferManager-CRM" --query "Reservations[0].Instances[0].PublicIpAddress" --output text') do set IP_EC2=%%i

echo.
echo IP Pubblico: %IP_EC2%
echo.
echo Deploy codice...
powershell -ExecutionPolicy Bypass -File "deploy_to_aws.ps1" -IpEC2 "%IP_EC2%"

:end
echo.
echo ================================================================
echo   COMPLETATO!
echo ================================================================
pause


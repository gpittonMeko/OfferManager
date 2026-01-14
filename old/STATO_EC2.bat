@echo off
cd /d "%~dp0"
title Stato Istanza EC2
cls
color 0B
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║              📊 STATO ISTANZA EC2 📊                         ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Verifica AWS CLI
aws --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ AWS CLI non configurato!
    echo  📂 Vedi: 🔧 SETUP AWS CLI - 5 MINUTI.txt
    pause
    exit /b 1
)

echo  ✅ AWS CLI configurato
echo.

REM Trova Instance ID
if exist "ec2_info.txt" (
    for /f "tokens=2 delims=: " %%a in ('findstr /c:"Instance ID" ec2_info.txt') do set INSTANCE_ID=%%a
    echo  📋 Instance ID: %INSTANCE_ID%
) else (
    echo  🔍 Ricerca istanza...
    for /f %%i in ('aws ec2 describe-instances --filters "Name=tag:Name,Values=OfferManager-CRM" --query "Reservations[0].Instances[0].InstanceId" --output text') do set INSTANCE_ID=%%i
    
    if "%INSTANCE_ID%"=="None" (
        echo  ❌ Istanza non trovata!
        pause
        exit /b 1
    )
    echo  ✅ Trovata: %INSTANCE_ID%
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Recupero informazioni...
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Recupera info
for /f %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].State.Name" --output text') do set STATE=%%i
for /f %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].PublicIpAddress" --output text') do set IP=%%i
for /f %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].InstanceType" --output text') do set TYPE=%%i

echo  ═══════════════════════════════════════════════════════════════
echo   INFORMAZIONI ISTANZA
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  🔑 Instance ID:    %INSTANCE_ID%
echo  💻 Tipo:           %TYPE%
echo  📍 IP Pubblico:    %IP%
echo  🚦 Stato:          %STATE%
echo.

if "%STATE%"=="running" (
    echo  🟢 ISTANZA ATTIVA
    echo.
    echo  🌐 Accedi a: http://%IP%
    echo  💰 Costo: ~0.012 euro/ora (~0.27 euro/giorno)
) else if "%STATE%"=="stopped" (
    echo  🔴 ISTANZA SPENTA
    echo.
    echo  💰 Costo: 0 euro/ora (solo storage ~0.10 euro/mese)
    echo  📱 Per avviare: START_EC2.bat
) else (
    echo  🟡 ISTANZA IN TRANSIZIONE
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

pause























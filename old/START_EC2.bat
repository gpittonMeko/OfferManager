@echo off
cd /d "%~dp0"
title Start Istanza EC2
cls
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║              ▶️  START ISTANZA EC2 ▶️                        ║
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
        echo.
        set /p INSTANCE_ID="  Inserisci Instance ID manualmente: "
    ) else (
        echo  ✅ Trovata: %INSTANCE_ID%
    )
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Avvio istanza %INSTANCE_ID%...
echo  ═══════════════════════════════════════════════════════════════
echo.

aws ec2 start-instances --instance-ids %INSTANCE_ID%

if errorlevel 1 (
    echo.
    echo  ❌ Errore durante avvio!
    pause
    exit /b 1
)

echo.
echo  ⏳ Attesa avvio... (circa 1 minuto)
echo.

REM Aspetta che sia running
aws ec2 wait instance-running --instance-ids %INSTANCE_ID%

echo  ✅ Istanza avviata!
echo.

REM Recupera nuovo IP
echo  📍 Recupero IP pubblico...
for /f %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].PublicIpAddress" --output text') do set NEW_IP=%%i

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   ✅ ISTANZA AVVIATA CON SUCCESSO!
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  🌐 Nuovo IP pubblico: %NEW_IP%
echo.
echo  📋 Accedi a: http://%NEW_IP%
echo  👤 Login: marco / demo123
echo.
echo  💡 Salva questo IP nei bookmark!
echo     (Cambia ad ogni riavvio)
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Aggiorna ec2_info.txt
if exist "ec2_info.txt" (
    echo IP Pubblico: %NEW_IP% > ec2_info_temp.txt
    findstr /v "IP Pubblico" ec2_info.txt >> ec2_info_temp.txt
    move /y ec2_info_temp.txt ec2_info.txt >nul
    echo  ✅ File ec2_info.txt aggiornato
    echo.
)

REM Chiedi se aprire browser
set /p APRI="  Aprire browser? (S/N - default S): "
if /i "%APRI%"=="" set APRI=S
if /i "%APRI%"=="S" (
    start http://%NEW_IP%
)

pause























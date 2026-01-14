@echo off
cd /d "%~dp0"
title Deploy Automatico su EC2
cls
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║         2️⃣  DEPLOY AUTOMATICO SU EC2 🚀                      ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Controlla se esiste ec2_info.txt
if exist "ec2_info.txt" (
    echo  📋 Trovato file ec2_info.txt
    echo.
    
    REM Leggi IP da file
    for /f "tokens=2 delims=: " %%a in ('findstr /c:"IP Pubblico" ec2_info.txt') do set IP_EC2=%%a
    
    echo  📍 IP trovato: %IP_EC2%
    echo.
    set /p USA_IP="  Usare questo IP? (S/N - default S): "
    if /i "%USA_IP%"=="" set USA_IP=S
    if /i "%USA_IP%"=="N" (
        set IP_EC2=
    )
)

REM Se non c'è IP, chiedi
if "%IP_EC2%"=="" (
    echo  ═══════════════════════════════════════════════════════════════
    echo.
    echo  💡 COME TROVARE L'IP:
    echo.
    echo     Opzione A - Da file ec2_info.txt (se hai creato con script)
    echo     Opzione B - Da AWS CLI:
    echo       aws ec2 describe-instances --filters "Name=tag:Name,Values=OfferManager-CRM" --query "Reservations[0].Instances[0].PublicIpAddress" --output text
    echo.
    echo     Opzione C - Da console AWS:
    echo       https://console.aws.amazon.com/ec2
    echo.
    echo  ═══════════════════════════════════════════════════════════════
    echo.
    set /p IP_EC2="  📍 Inserisci IP pubblico EC2: "
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Deploy su %IP_EC2%...
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Verifica chiave SSH
if not exist "C:\Users\user\Documents\LLM_14.pem" (
    echo  ❌ Chiave SSH non trovata!
    echo.
    echo  La chiave dovrebbe essere in:
    echo  C:\Users\user\Documents\LLM_14.pem
    echo.
    echo  Scaricala dalla console AWS o usa altra chiave.
    echo.
    pause
    exit /b 1
)

echo  ✅ Chiave SSH trovata
echo.

REM Esegui deploy PowerShell
powershell -ExecutionPolicy Bypass -File "deploy_to_aws.ps1" -IpEC2 "%IP_EC2%"

if errorlevel 1 (
    echo.
    echo  ❌ Deploy fallito!
    echo.
    echo  Controlla:
    echo    • Istanza EC2 è RUNNING
    echo    • Security Group ha porta 22 aperta
    echo    • Chiave SSH è corretta
    echo.
    pause
    exit /b 1
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   ✅ DEPLOY COMPLETATO!
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  🌐 Accedi a: http://%IP_EC2%
echo  👤 Login: marco / demo123
echo.
echo  💡 PROSSIMO STEP:
echo     Configura automazione start/stop per risparmiare:
echo     📂 3️⃣ SETUP AUTOMAZIONE.bat
echo.
echo  ═══════════════════════════════════════════════════════════════
pause























@echo off
cd /d "%~dp0"
title Setup Automazione Start/Stop
cls
color 0E
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║       3️⃣  SETUP AUTOMAZIONE START/STOP 8-19 LUN-VEN ⏰      ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  💰 RISPARMIO: Da 8 euro/mese a 2.60 euro/mese (67%%)
echo.
echo  Questa automazione:
echo    • START automatico: Lun-Ven ore 8:00
echo    • STOP automatico:  Lun-Ven ore 19:00
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Verifica AWS CLI
aws --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ AWS CLI non configurato!
    echo  📂 Vedi: 🔧 SETUP AWS CLI - 5 MINUTI.txt
    pause
    exit /b 1
)

REM Trova Instance ID
echo  🔍 Ricerca Instance ID...
echo.

if exist "ec2_info.txt" (
    for /f "tokens=2 delims=: " %%a in ('findstr /c:"Instance ID" ec2_info.txt') do set INSTANCE_ID=%%a
    echo  ✅ Instance ID trovato: %INSTANCE_ID%
    echo.
    set /p USA_ID="  Usare questo Instance ID? (S/N - default S): "
    if /i "%USA_ID%"=="" set USA_ID=S
    if /i "%USA_ID%"=="N" set INSTANCE_ID=
)

if "%INSTANCE_ID%"=="" (
    echo.
    echo  💡 Recupero Instance ID da AWS...
    for /f %%i in ('aws ec2 describe-instances --filters "Name=tag:Name,Values=OfferManager-CRM" --query "Reservations[0].Instances[0].InstanceId" --output text') do set INSTANCE_ID=%%i
    
    if "%INSTANCE_ID%"=="None" (
        echo.
        echo  ❌ Istanza non trovata automaticamente.
        echo.
        echo  Trova manualmente:
        echo    aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,Tags[?Key=='Name'].Value|[0]]" --output table
        echo.
        set /p INSTANCE_ID="  Inserisci Instance ID: "
    ) else (
        echo  ✅ Trovato: %INSTANCE_ID%
    )
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Creazione Lambda Functions e EventBridge Rules...
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Esegui setup automazione
python create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-role
echo.
python create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-start-lambda
echo.
python create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-stop-lambda
echo.
python create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-start-rule
echo.
python create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-stop-rule
echo.

if errorlevel 1 (
    echo.
    echo  ⚠️  Errore durante setup automatico!
    echo.
    echo  ALTERNATIVA: Setup manuale con AWS Instance Scheduler
    echo  📂 Vedi: ⏰ AUTOMAZIONE START-STOP 8-19.txt (OPZIONE 1)
    echo.
    pause
    exit /b 1
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   ✅ AUTOMAZIONE CONFIGURATA!
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  📅 Schedule:
echo     • START: Lun-Ven ore 8:00 (fuso Europe/Rome)
echo     • STOP:  Lun-Ven ore 19:00 (fuso Europe/Rome)
echo.
echo  💰 Risparmio stimato: ~5.40 euro/mese
echo.
echo  ⚠️  NOTA: L'IP pubblico cambierà ogni mattina!
echo     Salvalo nei bookmark quando accedi.
echo.
echo  🎯 Verifica su AWS Console:
echo     • Lambda: EC2-Start-OfficeHours, EC2-Stop-OfficeHours
echo     • EventBridge: EC2-Start-8AM-Weekdays, EC2-Stop-7PM-Weekdays
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  🎉 SETUP COMPLETO! Tutto è automatico ora! 🎉
echo.
pause























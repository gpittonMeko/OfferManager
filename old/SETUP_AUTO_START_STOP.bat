@echo off
cd /d "%~dp0"
title Setup Automazione Start/Stop EC2
cls
color 0B
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║      ⏰ SETUP AUTOMAZIONE START/STOP EC2 8-19 LUN-VEN ⏰     ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Questo script configura l'automazione per:
echo.
echo    • START automatico:  Lun-Ven ore 8:00
echo    • STOP automatico:   Lun-Ven ore 19:00
echo.
echo  💰 RISPARMIO: Da 8 euro/mese a 2.60 euro/mese (67%%)
echo.
echo  ════════════════════════════════════════════════════════════════
echo.

REM Verifica AWS CLI installato
aws --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ AWS CLI non installato!
    echo.
    echo  Installa AWS CLI da:
    echo  https://aws.amazon.com/cli/
    echo.
    echo  Oppure usa OPZIONE 1 nella guida:
    echo  📂 ⏰ AUTOMAZIONE START-STOP 8-19.txt
    echo.
    pause
    exit /b 1
)

echo  ✅ AWS CLI installato
echo.

REM Richiedi Instance ID
set /p INSTANCE_ID="  Inserisci Instance ID (es. i-0123456789abcdef): "
echo.

echo  ════════════════════════════════════════════════════════════════
echo   Creazione funzioni Lambda e regole EventBridge...
echo  ════════════════════════════════════════════════════════════════
echo.

REM Crea directory temporanea
if not exist "temp_lambda" mkdir temp_lambda
cd temp_lambda

echo  [1/6] Creazione ruolo IAM...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-role

echo.
echo  [2/6] Creazione Lambda START...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-start-lambda

echo.
echo  [3/6] Creazione Lambda STOP...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-stop-lambda

echo.
echo  [4/6] Creazione regola EventBridge START (8:00)...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-start-rule

echo.
echo  [5/6] Creazione regola EventBridge STOP (19:00)...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step create-stop-rule

echo.
echo  [6/6] Test configurazione...
python ..\create_lambda_scheduler.py --instance-id %INSTANCE_ID% --step test

cd ..
rmdir /s /q temp_lambda

echo.
echo  ════════════════════════════════════════════════════════════════
echo   ✅ AUTOMAZIONE CONFIGURATA CON SUCCESSO!
echo  ════════════════════════════════════════════════════════════════
echo.
echo  📅 Schedule:
echo     • START: Lun-Ven ore 8:00 (Europe/Rome)
echo     • STOP:  Lun-Ven ore 19:00 (Europe/Rome)
echo.
echo  💰 Risparmio stimato: ~5.40 euro/mese
echo.
echo  ⚠️  NOTA: L'IP pubblico cambierà ogni mattina!
echo     Salvalo nei bookmark quando accedi.
echo.
echo  🎯 Per modificare orari:
echo     AWS Console → EventBridge → Rules
echo.
echo  ════════════════════════════════════════════════════════════════
echo.
pause























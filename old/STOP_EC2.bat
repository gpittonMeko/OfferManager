@echo off
cd /d "%~dp0"
title Stop Istanza EC2
cls
color 0C
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║              ⏹️  STOP ISTANZA EC2 ⏹️                         ║
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
echo  💰 Stoppando l'istanza, NON paghi fino al prossimo avvio!
echo.
set /p CONFERMA="  Vuoi stoppare l'istanza? (S/N): "
if /i not "%CONFERMA%"=="S" (
    echo  Operazione annullata.
    pause
    exit /b 0
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Stop istanza %INSTANCE_ID%...
echo  ═══════════════════════════════════════════════════════════════
echo.

aws ec2 stop-instances --instance-ids %INSTANCE_ID%

if errorlevel 1 (
    echo.
    echo  ❌ Errore durante stop!
    pause
    exit /b 1
)

echo.
echo  ⏳ Attesa stop... (circa 30 secondi)
echo.

REM Aspetta che sia stopped
aws ec2 wait instance-stopped --instance-ids %INSTANCE_ID%

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   ✅ ISTANZA STOPPATA!
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  💰 Costo ora: 0 euro/ora (paghi solo storage ~0.10 euro/mese)
echo.
echo  📱 Per riavviare:
echo     Doppio click su: START_EC2.bat
echo.
echo  ⚠️  NOTA: Al prossimo avvio l'IP pubblico cambierà!
echo.
echo  ═══════════════════════════════════════════════════════════════
pause























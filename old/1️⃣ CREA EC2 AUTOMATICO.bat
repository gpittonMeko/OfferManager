@echo off
cd /d "%~dp0"
title Crea Istanza EC2 Automatica
cls
color 0B
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║        1️⃣  CREA ISTANZA EC2 AUTOMATICA CON AWS CLI 🚀       ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Questo script crea automaticamente:
echo    • Istanza EC2 t2.micro (Free Tier)
echo    • Security Group con porte corrette
echo    • Storage ottimizzato 8GB
echo    • Configurazione economica
echo.
echo  💰 COSTI: GRATIS anno 1, poi ~2.60 euro/mese (con automazione)
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Verifica AWS CLI
aws --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ AWS CLI non installato!
    echo.
    echo  Segui la guida:
    echo  📂 🔧 SETUP AWS CLI - 5 MINUTI.txt
    echo.
    pause
    exit /b 1
)

echo  ✅ AWS CLI configurato
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
set /p CONFERMA="  Vuoi creare l'istanza EC2? (S/N): "
if /i not "%CONFERMA%"=="S" (
    echo  Operazione annullata.
    pause
    exit /b 0
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Creazione in corso...
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Esegui script Python
python crea_ec2_automatico.py

if errorlevel 1 (
    echo.
    echo  ❌ Errore durante la creazione!
    echo.
    echo  Possibili cause:
    echo    • AWS CLI non configurato correttamente
    echo    • Permessi IAM insufficienti
    echo    • Chiave LLM_14 non esiste nella region eu-west-1
    echo.
    echo  Soluzione:
    echo    1. Verifica: aws configure list
    echo    2. Controlla permessi IAM (EC2FullAccess)
    echo    3. Oppure crea istanza manualmente con guida:
    echo       📂 🔥 CREA ISTANZA EC2 - 5 MINUTI.txt
    echo.
    pause
    exit /b 1
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo   ✅ ISTANZA CREATA CON SUCCESSO!
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  📋 Controlla file: ec2_info.txt per i dettagli
echo.
echo  🎯 PROSSIMO STEP:
echo     Doppio click su: 2️⃣ DEPLOY AUTOMATICO.bat
echo.
echo  ═══════════════════════════════════════════════════════════════
pause























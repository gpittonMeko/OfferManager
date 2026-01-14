@echo off
REM Esegue migrazione sul server cloud AWS
echo ================================================================
echo   ESECUZIONE MIGRAZIONE SUL SERVER CLOUD
echo ================================================================
echo.

set EC2_IP=13.53.183.146
set KEY_PATH=C:\Users\user\Documents\LLM_14.pem

echo Caricamento script migrazione...
scp -i "%KEY_PATH%" migrations\add_closed_amount_margin_to_offers.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/migrations/

if %ERRORLEVEL% EQU 0 (
    echo ✓ Script caricato
    echo.
    echo Esecuzione migrazione...
    ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "cd /home/ubuntu/offermanager && python3 migrations/add_closed_amount_margin_to_offers.py"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ Migrazione completata!
    ) else (
        echo ✗ Errore durante la migrazione
    )
) else (
    echo ✗ Errore durante il caricamento
)

echo.
pause

@echo off
echo ================================================================
echo   AGGIORNA OPPORTUNITA' SU AWS - DA CATEGORIZZARE
echo ================================================================
echo.

set EC2_IP=13.53.183.146
set KEY_PATH=C:\Users\user\Documents\LLM_14.pem

echo IP EC2: %EC2_IP%
echo Chiave: %KEY_PATH%
echo.

echo ================================================================
echo   Caricamento script su EC2...
echo ================================================================
echo.

scp -i "%KEY_PATH%" deploy\fix_heat_level_aws.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/

if %ERRORLEVEL% EQU 0 (
    echo ✓ Script caricato con successo
    echo.
    echo ================================================================
    echo   Esecuzione script su AWS...
    echo ================================================================
    echo.
    
    ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "cd /home/ubuntu/offermanager && python3 fix_heat_level_aws.py && sudo systemctl restart offermanager"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ Script eseguito con successo!
    ) else (
        echo ⚠ Errore durante l'esecuzione
    )
) else (
    echo ✗ Errore durante il caricamento
    echo Verifica che:
    echo   1. Il file aggiorna_opportunita_aws.py esista
    echo   2. La chiave .pem sia nel percorso corretto
    echo   3. SCP sia installato e configurato
)

echo.
echo ================================================================
echo   ✅ COMPLETATO!
echo ================================================================
echo.
pause

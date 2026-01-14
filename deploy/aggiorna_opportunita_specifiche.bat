@echo off
echo ================================================================
echo   AGGIORNA OPPORTUNITA' SPECIFICHE SU AWS
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

scp -i "%KEY_PATH%" deploy\aggiorna_opportunita_specifiche_aws.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/

if %ERRORLEVEL% EQU 0 (
    echo ✓ Script caricato con successo
    echo.
    echo ================================================================
    echo   Esecuzione script su AWS...
    echo ================================================================
    echo.
    
    ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "cd /home/ubuntu/offermanager && python3 aggiorna_opportunita_specifiche_aws.py"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ Script eseguito con successo!
    ) else (
        echo ⚠ Errore durante l'esecuzione
    )
) else (
    echo ✗ Errore durante il caricamento
)

echo.
echo ================================================================
echo   Caricamento template HTML aggiornato...
echo ================================================================
echo.

scp -i "%KEY_PATH%" templates\app_mekocrm_completo.html ubuntu@%EC2_IP%:/home/ubuntu/offermanager/templates/

if %ERRORLEVEL% EQU 0 (
    echo ✓ Template caricato con successo
    echo.
    echo ================================================================
    echo   Riavvio servizio...
    echo ================================================================
    echo.
    
    ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "sudo systemctl restart offermanager"
    
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Servizio riavviato!
    )
) else (
    echo ⚠ Errore durante il caricamento del template
)

echo.
echo ================================================================
echo   ✅ COMPLETATO!
echo ================================================================
echo.
pause

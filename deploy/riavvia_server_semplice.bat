@echo off
echo ================================================================
echo   RIAVVIO SERVER CLOUD
echo ================================================================
echo.

set EC2_IP=13.53.183.146
set KEY_PATH=C:\Users\user\Documents\LLM_14.pem

echo IP EC2: %EC2_IP%
echo Chiave: %KEY_PATH%
echo.

echo ================================================================
echo   Caricamento crm_app_completo.py su EC2...
echo ================================================================
echo.

scp -i "%KEY_PATH%" crm_app_completo.py ubuntu@%EC2_IP%:/home/ubuntu/offermanager/

if %ERRORLEVEL% EQU 0 (
    echo ✓ File caricato con successo
    echo.
    echo ================================================================
    echo   Riavvio servizio offermanager...
    echo ================================================================
    echo.
    
    ssh -i "%KEY_PATH%" ubuntu@%EC2_IP% "sudo systemctl restart offermanager"
    
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Servizio riavviato con successo!
    ) else (
        echo ⚠ Errore durante il riavvio
        echo Esegui manualmente:
        echo   ssh -i "%KEY_PATH%" ubuntu@%EC2_IP%
        echo   sudo systemctl restart offermanager
    )
) else (
    echo ✗ Errore durante il caricamento
    echo Verifica che:
    echo   1. Il file crm_app_completo.py esista nella cartella corrente
    echo   2. La chiave .pem sia nel percorso corretto
    echo   3. SCP sia installato e configurato
)

echo.
echo ================================================================
echo   ✅ COMPLETATO!
echo ================================================================
echo.
pause

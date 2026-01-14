@echo off
cd /d "%~dp0"
title Crea EC2 Automatico
cls
echo.
echo ================================================================
echo        CREAZIONE AUTOMATICA ISTANZA EC2
echo ================================================================
echo.
echo Questo script creerà automaticamente un'istanza EC2 su AWS
echo.
echo REQUISITI:
echo   ✅ Account AWS attivo
echo   ✅ AWS CLI installato e configurato
echo   ✅ Key pair "LLM_14" esistente in AWS
echo.
echo ================================================================
echo.
echo Hai configurato AWS CLI? (s/N)
set /p AWS_OK=
echo.

if /i NOT "%AWS_OK%"=="s" (
    echo.
    echo ================================================================
    echo   SETUP AWS CLI
    echo ================================================================
    echo.
    echo 1. Installa AWS CLI:
    echo    https://aws.amazon.com/cli/
    echo.
    echo 2. Configura credenziali:
    echo    aws configure
    echo.
    echo    Ti chiederà:
    echo    - AWS Access Key ID
    echo    - AWS Secret Access Key
    echo    - Region: eu-west-1
    echo.
    echo    Le credenziali le trovi in AWS Console:
    echo    IAM → Users → Security credentials → Create access key
    echo.
    echo ================================================================
    pause
    exit /b
)

echo Creazione istanza EC2 in corso...
echo.
python crea_ec2_automatico.py

if errorlevel 1 (
    echo.
    echo ================================================================
    echo   ERRORE!
    echo ================================================================
    echo.
    echo Usa la creazione manuale:
    echo   Segui: SETUP_AWS_MANUALE.txt
    echo.
)

echo.
pause


@echo off
cd /d "%~dp0"
title Deploy AWS Economico
cls
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║     🚀 DEPLOY OFFERMANAGER SU AWS - SUPER ECONOMICO 💰       ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  💰 COSTI:
echo     • ANNO 1:  GRATIS (Free Tier t2.micro)
echo     • ANNO 2+: ~8 euro/mese (o 0 se stoppi quando non usi)
echo.
echo  ════════════════════════════════════════════════════════════════
echo.
echo  📋 HAI GIÀ CREATO L'ISTANZA EC2?
echo.
echo     1. SÌ - Ho già l'istanza EC2, facciamo deploy
echo     2. NO - Apri guida per crearla (5 minuti)
echo     3. HELP - Gestione costi (stop/start istanza)
echo     4. Esci
echo.
set /p SCELTA="  Scelta (1-4): "
echo.

if "%SCELTA%"=="1" goto DEPLOY
if "%SCELTA%"=="2" goto GUIDA
if "%SCELTA%"=="3" goto COSTI
if "%SCELTA%"=="4" exit

:DEPLOY
cls
echo.
echo  ════════════════════════════════════════════════════════════════
echo   DEPLOY AUTOMATICO
echo  ════════════════════════════════════════════════════════════════
echo.
echo  Recupera l'IP PUBBLICO dalla console AWS:
echo  https://console.aws.amazon.com/ec2
echo.
set /p IP_EC2="  Inserisci IP EC2: "
echo.
echo  ════════════════════════════════════════════════════════════════
echo   Avvio deploy su %IP_EC2%...
echo  ════════════════════════════════════════════════════════════════
echo.
powershell -ExecutionPolicy Bypass -File "deploy_to_aws.ps1" -IpEC2 "%IP_EC2%"
echo.
echo  ════════════════════════════════════════════════════════════════
echo   ✅ COMPLETATO!
echo  ════════════════════════════════════════════════════════════════
echo.
echo   Accedi a: http://%IP_EC2%
echo.
echo   Username: marco
echo   Password: demo123
echo.
echo  💡 SUGGERIMENTO: Quando non usi l'app, STOPPA l'istanza
echo     per non pagare! Usa script "GESTISCI_EC2_COSTI.bat"
echo.
pause
exit

:GUIDA
cls
start "" "GUIDA_DEPLOY_ECONOMICO.txt"
echo.
echo  ════════════════════════════════════════════════════════════════
echo   Guida aperta!
echo  ════════════════════════════════════════════════════════════════
echo.
echo  📖 Leggi la guida e segui i 3 step:
echo.
echo     STEP 1: Crea istanza EC2 (5 minuti)
echo     STEP 2: Verifica chiave SSH
echo     STEP 3: Torna qui e scegli opzione 1
echo.
echo  💡 Configurazione raccomandata:
echo     • Tipo: t2.micro (FREE TIER!)
echo     • Storage: 8 GB (minimo)
echo     • Region: eu-west-1 (Irlanda)
echo.
pause
exit

:COSTI
cls
start "" "GESTISCI_EC2_COSTI.bat"
echo.
echo  ════════════════════════════════════════════════════════════════
echo   Gestione Costi Aperta
echo  ════════════════════════════════════════════════════════════════
echo.
echo  💰 RISPARMIA AL MASSIMO:
echo.
echo     Quando NON usi l'app:
echo       → STOPPA istanza = 0 euro/giorno
echo.
echo     Quando ti serve:
echo       → AVVIA istanza = l'app torna disponibile
echo.
echo  📊 Esempio:
echo     • Uso 5 giorni/settimana = ~5 euro/mese
echo     • Sempre accesa = ~8 euro/mese
echo     • Sempre spenta = ~0.10 euro/mese (solo storage)
echo.
pause
exit







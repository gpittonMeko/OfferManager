@echo off
cd /d "%~dp0"
title Deploy OfferManager su AWS EC2
cls
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║         🚀 DEPLOY OFFERMANAGER SU AWS EC2 🚀                 ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Questo script caricherà automaticamente OfferManager CRM
echo  sulla tua istanza AWS EC2.
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  📋 PREREQUISITI:
echo     ✅ Istanza EC2 creata e RUNNING
echo     ✅ Chiave SSH: C:\Users\user\Documents\LLM_14.pem
echo     ✅ Security Group: SSH (22) + HTTP (80) + Custom (5000)
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  💡 DOVE TROVO L'IP PUBBLICO?
echo     1. Vai su: https://console.aws.amazon.com/ec2
echo     2. Instances → OfferManager-CRM
echo     3. Copia "Public IPv4 address"
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
set /p IP_EC2="  📍 Inserisci IP pubblico EC2: "
echo.
echo  ═══════════════════════════════════════════════════════════════
echo   Avvio deploy su %IP_EC2%...
echo  ═══════════════════════════════════════════════════════════════
echo.
powershell -ExecutionPolicy Bypass -File "deploy_to_aws.ps1" -IpEC2 "%IP_EC2%"
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.
echo  💡 PROSSIMI PASSI:
echo     1. Configura automazione start/stop (risparmio 67%%)
echo        📂 ⏰ AUTOMAZIONE START-STOP 8-19.txt
echo.
echo     2. Salva IP nei bookmark (cambia ogni riavvio!)
echo.
echo     3. Cambia password al primo login!
echo.
echo  ═══════════════════════════════════════════════════════════════
pause


@echo off
cd /d "%~dp0"
title Diagnostica OfferManager
cls
color 0E
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║         🔍 DIAGNOSTICA COMPLETA OFFERMANAGER 🔍              ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Eseguo controlli...
echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [1/10] Python installato?
echo  ═══════════════════════════════════════════════════════════════

python --version 2>nul
if errorlevel 1 (
    echo  ❌ Python NON installato
    echo     Scarica da: https://www.python.org/downloads/
    goto END
) else (
    echo  ✅ Python OK
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [2/10] Flask installato?
echo  ═══════════════════════════════════════════════════════════════

python -c "import flask; print('✅ Flask', flask.__version__)" 2>nul
if errorlevel 1 (
    echo  ❌ Flask NON installato
    echo  📦 Installazione in corso...
    pip install flask
) else (
    echo  OK
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [3/10] Flask-SQLAlchemy installato?
echo  ═══════════════════════════════════════════════════════════════

python -c "import flask_sqlalchemy; print('✅ Flask-SQLAlchemy OK')" 2>nul
if errorlevel 1 (
    echo  ❌ Flask-SQLAlchemy NON installato
    echo  📦 Installazione in corso...
    pip install flask-sqlalchemy
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [4/10] File crm_app.py esiste?
echo  ═══════════════════════════════════════════════════════════════

if exist "crm_app.py" (
    echo  ✅ crm_app.py trovato
) else (
    echo  ❌ crm_app.py NON trovato
    goto END
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [5/10] Directory templates esiste?
echo  ═══════════════════════════════════════════════════════════════

if exist "templates\" (
    echo  ✅ Directory templates OK
    dir /b templates\*.html 2>nul | find /c /v "" > temp_count.txt
    set /p HTML_COUNT=<temp_count.txt
    del temp_count.txt
    echo     Trovati %HTML_COUNT% file HTML
) else (
    echo  ❌ Directory templates NON trovata
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [6/10] Porta 5000 libera?
echo  ═══════════════════════════════════════════════════════════════

netstat -ano | findstr :5000 > temp_port.txt
if exist temp_port.txt (
    for /f %%i in ('findstr /c:"LISTENING" temp_port.txt') do set PORT_USED=1
)
del temp_port.txt 2>nul

if defined PORT_USED (
    echo  ⚠️  Porta 5000 GIÀ in uso
    echo     Chiudo processi sulla porta 5000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
    timeout /t 2 /nobreak >nul
    echo  ✅ Porta liberata
) else (
    echo  ✅ Porta 5000 libera
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [7/10] Test sintassi crm_app.py
echo  ═══════════════════════════════════════════════════════════════

python -m py_compile crm_app.py 2>error.txt
if errorlevel 1 (
    echo  ❌ Errori sintassi in crm_app.py:
    type error.txt
    del error.txt
    goto END
) else (
    echo  ✅ Sintassi corretta
    del error.txt 2>nul
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [8/10] Test import moduli
echo  ═══════════════════════════════════════════════════════════════

python -c "from flask import Flask; from flask_sqlalchemy import SQLAlchemy; print('✅ Import OK')" 2>nul
if errorlevel 1 (
    echo  ❌ Errore import moduli
    goto END
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [9/10] Verifica database
echo  ═══════════════════════════════════════════════════════════════

if exist "instance\offerte_crm.db" (
    echo  ✅ Database esistente trovato
) else (
    echo  ℹ️  Database sarà creato al primo avvio
)

echo.
echo  ═══════════════════════════════════════════════════════════════
echo  [10/10] Avvio test app
echo  ═══════════════════════════════════════════════════════════════

echo  🚀 Avvio app...
echo.
echo  Se vedi errori sotto, premi Ctrl+C e inviameli!
echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

REM Avvia app in foreground per vedere errori
python crm_app.py

:END
echo.
echo  ═══════════════════════════════════════════════════════════════
pause






















@echo off
REM Avvia OfferManager.exe dalla cartella dist
cd /d "%~dp0"
if exist "dist\OfferManager.exe" (
    start "" "dist\OfferManager.exe"
) else (
    cls
    echo.
    echo ================================================================
    echo                    FILE NON TROVATO
    echo ================================================================
    echo.
    echo L'eseguibile non e' stato ancora creato!
    echo.
    echo Doppio click su: "Crea Eseguibile.bat"
    echo.
    echo ================================================================
    pause
)


# Script per organizzare la repository
$repoPath = "C:\Users\user\OneDrive - ME.KO. Srl\Documenti\Cursor\OfferManager"
Set-Location $repoPath

# Crea cartella old se non esiste
if (-not (Test-Path "old")) {
    New-Item -ItemType Directory -Path "old" | Out-Null
}

Write-Host "Spostamento file .txt..."
Get-ChildItem -Path . -Filter "*.txt" -File | Where-Object { $_.Name -notlike "requirements*.txt" } | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento file .md..."
Get-ChildItem -Path . -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" } | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento file batch vecchi..."
$oldBats = @(
    "AVVIA.bat", "AVVIA_DEBUG.bat", "RUN.bat", "START.bat", "GO.bat",
    "PROVA_APP_COMPLETA.bat", "TEST_LOCALE_CRM.bat", "RIAVVIA_CRM.bat",
    "Crea Eseguibile.bat", "Setup Iniziale.bat", "DEPLOY_AUTOMATICO.bat",
    "SETUP_AUTO_START_STOP.bat", "GESTISCI_EC2_COSTI.bat", "STATO_EC2.bat",
    "START_EC2.bat", "STOP_EC2.bat"
)
foreach ($bat in $oldBats) {
    if (Test-Path $bat) {
        Move-Item -Path $bat -Destination "old\" -Force -ErrorAction SilentlyContinue
    }
}

# Sposta anche file batch con emoji (usando Get-ChildItem)
Get-ChildItem -Path . -Filter "*.bat" -File | Where-Object { 
    $_.Name -notin @("▶️ AVVIA CRM COMPLETO.bat", "▶️ AVVIA QUI.bat", "🌐 TESTA WEB APP.bat", "organize_repo.ps1")
} | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento PDF..."
Get-ChildItem -Path . -Filter "*.pdf" -File | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento DOCX..."
Get-ChildItem -Path . -Filter "*.docx" -File | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento altri file..."
if (Test-Path "deploy_aws.sh") { Move-Item -Path "deploy_aws.sh" -Destination "old\" -Force }
if (Test-Path "deploy_to_aws.ps1") { Move-Item -Path "deploy_to_aws.ps1" -Destination "old\" -Force }
if (Test-Path "OfferManager.spec") { Move-Item -Path "OfferManager.spec" -Destination "old\" -Force }
Get-ChildItem -Path . -Filter "temp_*.txt" -File | Move-Item -Destination "old\" -Force -ErrorAction SilentlyContinue

Write-Host "Spostamento file Python di test/demo..."
$testFiles = @("test_functionality.py", "test_import.py", "test_price_loader.py", "demo_products.py", "analyze_past_offers.py", "analyze_ur_excel.py", "carica_listini_reali.py", "count_all_products.py", "create_lambda_scheduler.py", "crea_ec2_automatico.py", "desktop_app_demo.py", "genera_offerta_completa.py", "init_crm_complete.py", "launcher.py", "parse_all_pricelists.py", "start_simple.py")
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "old\" -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Spostamento cartelle build/dist..."
if (Test-Path "build") { Move-Item -Path "build" -Destination "old\" -Force }
if (Test-Path "dist") { Move-Item -Path "dist" -Destination "old\" -Force }

Write-Host "Spostamento file log..."
if (Test-Path "app_server.log") { Move-Item -Path "app_server.log" -Destination "old\" -Force }

Write-Host "Spostamento file Python vecchi..."
if (Test-Path "app_completa.py") { Move-Item -Path "app_completa.py" -Destination "old\" -Force }
if (Test-Path "crm_app.py") { Move-Item -Path "crm_app.py" -Destination "old\" -Force }

Write-Host "✅ Repository organizzata! File spostati in cartella 'old'"

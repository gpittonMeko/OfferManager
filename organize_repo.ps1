# Script per organizzare la repository - Versione migliorata
$repoPath = Get-Location
Set-Location $repoPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PULIZIA REPOSITORY OFFERMANAGER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Crea cartella old se non esiste
if (-not (Test-Path "old")) {
    New-Item -ItemType Directory -Path "old" | Out-Null
    Write-Host "✓ Cartella 'old' creata" -ForegroundColor Green
}

# File batch importanti da mantenere
$keepBats = @(
    "▶️ AVVIA CRM COMPLETO.bat",
    "▶️ AVVIA QUI.bat", 
    "🌐 TESTA WEB APP.bat",
    "🌐 TESTA CRM LOCALE.bat"
)

# File Python importanti da mantenere
$keepPython = @(
    "app.py",
    "crm_app_completo.py",
    "offer_generator.py",
    "pdf_parser.py",
    "docx_handler.py",
    "company_searcher.py",
    "offer_numbering.py",
    "price_loader.py",
    "ur_portal_direct.py",
    "ur_portal_integration.py",
    "ur_sync.py"
)

Write-Host "[1/8] Spostamento file .txt (eccetto requirements)..." -ForegroundColor Yellow
$txtMoved = 0
Get-ChildItem -Path . -Filter "*.txt" -File | Where-Object { 
    $_.Name -notlike "requirements*.txt" -and $_.Name -notlike "README*.txt"
} | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $txtMoved++
}
Write-Host "  ✓ Spostati $txtMoved file .txt" -ForegroundColor Green

Write-Host "[2/8] Spostamento file .md (eccetto README.md)..." -ForegroundColor Yellow
$mdMoved = 0
Get-ChildItem -Path . -Filter "*.md" -File | Where-Object { 
    $_.Name -ne "README.md"
} | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $mdMoved++
}
Write-Host "  ✓ Spostati $mdMoved file .md" -ForegroundColor Green

Write-Host "[3/8] Spostamento file batch vecchi..." -ForegroundColor Yellow
$batMoved = 0
Get-ChildItem -Path . -Filter "*.bat" -File | Where-Object { 
    $_.Name -notin $keepBats
} | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $batMoved++
}
Write-Host "  ✓ Spostati $batMoved file .bat" -ForegroundColor Green

Write-Host "[4/8] Spostamento file PowerShell (eccetto questo script)..." -ForegroundColor Yellow
$psMoved = 0
Get-ChildItem -Path . -Filter "*.ps1" -File | Where-Object { 
    $_.Name -ne "organize_repo.ps1"
} | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $psMoved++
}
Write-Host "  ✓ Spostati $psMoved file .ps1" -ForegroundColor Green

Write-Host "[5/8] Spostamento PDF e DOCX dalla root..." -ForegroundColor Yellow
$pdfMoved = 0
Get-ChildItem -Path . -Filter "*.pdf" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $pdfMoved++
}
$docxMoved = 0
Get-ChildItem -Path . -Filter "*.docx" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $docxMoved++
}
Write-Host "  ✓ Spostati $pdfMoved PDF e $docxMoved DOCX" -ForegroundColor Green

Write-Host "[6/8] Spostamento file Python di test/demo..." -ForegroundColor Yellow
$testFiles = @(
    "test_functionality.py", "test_import.py", "test_price_loader.py", 
    "demo_products.py", "analyze_past_offers.py", "analyze_ur_excel.py", 
    "carica_listini_reali.py", "count_all_products.py", 
    "create_lambda_scheduler.py", "crea_ec2_automatico.py", 
    "desktop_app_demo.py", "genera_offerta_completa.py", 
    "init_crm_complete.py", "launcher.py", "parse_all_pricelists.py", 
    "start_simple.py", "app_completa.py", "crm_app.py"
)
$pyMoved = 0
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "old\" -Force -ErrorAction SilentlyContinue
        $pyMoved++
    }
}
Write-Host "  ✓ Spostati $pyMoved file Python di test/demo" -ForegroundColor Green

Write-Host "[7/8] Spostamento file di deploy e build..." -ForegroundColor Yellow
$deployFiles = @("deploy_aws.sh", "deploy_to_aws.ps1", "OfferManager.spec")
$deployMoved = 0
foreach ($file in $deployFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "old\" -Force -ErrorAction SilentlyContinue
        $deployMoved++
    }
}
if (Test-Path "build") { 
    Move-Item -Path "build" -Destination "old\" -Force -ErrorAction SilentlyContinue
    $deployMoved++
}
if (Test-Path "dist") { 
    Move-Item -Path "dist" -Destination "old\" -Force -ErrorAction SilentlyContinue
    $deployMoved++
}
Write-Host "  ✓ Spostati $deployMoved file/cartelle di deploy" -ForegroundColor Green

Write-Host "[8/8] Spostamento file log e temporanei..." -ForegroundColor Yellow
$logMoved = 0
Get-ChildItem -Path . -Filter "*.log" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $logMoved++
}
Get-ChildItem -Path . -Filter "temp_*.txt" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "old\" -Force -ErrorAction SilentlyContinue
    $logMoved++
}
Write-Host "  ✓ Spostati $logMoved file log/temporanei" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ PULIZIA COMPLETATA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "File mantenuti nella root:" -ForegroundColor Yellow
Write-Host "  • File Python core: $($keepPython.Count) file" -ForegroundColor White
Write-Host "  • File batch principali: $($keepBats.Count) file" -ForegroundColor White
Write-Host "  • requirements.txt, requirements_cloud.txt" -ForegroundColor White
Write-Host "  • README.md" -ForegroundColor White
Write-Host ""
Write-Host "Tutti gli altri file sono stati spostati in: old\" -ForegroundColor Cyan

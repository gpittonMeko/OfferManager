# Script PowerShell per Deploy Automatico su AWS EC2
# OfferManager CRM

param(
    [Parameter(Mandatory=$true)]
    [string]$IpEC2
)

$KeyPath = "C:\Users\user\Documents\LLM_14.pem"
$LocalPath = "C:\Users\user\OneDrive - ME.KO. Srl\Documenti\Cursor\OfferManager"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY OFFERMANAGER CRM SU AWS EC2" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IP EC2: $IpEC2" -ForegroundColor Yellow
Write-Host "Chiave: $KeyPath" -ForegroundColor Yellow
Write-Host ""

# Verifica chiave
if (!(Test-Path $KeyPath)) {
    Write-Host "ERRORE: Chiave non trovata in $KeyPath" -ForegroundColor Red
    exit 1
}

# Fix permessi chiave (Windows)
Write-Host "[1/5] Configurazione permessi chiave..." -ForegroundColor Green
icacls $KeyPath /inheritance:r 2>&1 | Out-Null
icacls $KeyPath /grant:r "$env:USERNAME`:R" 2>&1 | Out-Null

# Crea directory remota
Write-Host "[2/5] Creazione directory su EC2..." -ForegroundColor Green
ssh -i $KeyPath -o "StrictHostKeyChecking=no" ubuntu@$IpEC2 "mkdir -p /home/ubuntu/offermanager"

# Carica file essenziali
Write-Host "[3/5] Caricamento file..." -ForegroundColor Green

$FilesToUpload = @(
    "crm_app.py",
    "offer_generator.py",
    "pdf_parser.py",
    "docx_handler.py",
    "company_searcher.py",
    "offer_numbering.py",
    "demo_products.py",
    "requirements_cloud.txt",
    "deploy_aws.sh"
)

foreach ($file in $FilesToUpload) {
    $source = Join-Path $LocalPath $file
    if (Test-Path $source) {
        Write-Host "  Caricamento $file..." -ForegroundColor Gray
        scp -i $KeyPath $source ubuntu@${IpEC2}:/home/ubuntu/offermanager/
    }
}

# Carica directory templates
Write-Host "  Caricamento templates..." -ForegroundColor Gray
scp -i $KeyPath -r (Join-Path $LocalPath "templates") ubuntu@${IpEC2}:/home/ubuntu/offermanager/

# Esegui deploy script
Write-Host "[4/5] Esecuzione script di deploy..." -ForegroundColor Green
ssh -i $KeyPath ubuntu@$IpEC2 @"
    cd /home/ubuntu/offermanager
    chmod +x deploy_aws.sh
    ./deploy_aws.sh
"@

# Test
Write-Host "[5/5] Verifica deployment..." -ForegroundColor Green
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://${IpEC2}:5000" -TimeoutSec 10
    
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT COMPLETATO CON SUCCESSO!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Accedi a: http://$IpEC2:5000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Login Demo:" -ForegroundColor Cyan
    Write-Host "  Username: marco" -ForegroundColor White
    Write-Host "  Password: demo123" -ForegroundColor White
    Write-Host ""
    
    # Apri browser
    Start-Process "http://${IpEC2}:5000"
    
} catch {
    Write-Host ""
    Write-Host "App deployata, ma non ancora raggiungibile." -ForegroundColor Yellow
    Write-Host "Prova tra qualche minuto: http://${IpEC2}:5000" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Comandi utili:" -ForegroundColor Cyan
Write-Host "  ssh -i $KeyPath ubuntu@$IpEC2" -ForegroundColor White
Write-Host "  sudo systemctl status offermanager" -ForegroundColor White
Write-Host "  sudo journalctl -u offermanager -f" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""


# Script PowerShell per aggiornare file su EC2
# Uso: .\📤 AGGIORNA EC2 - PowerShell.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  AGGIORNA EC2 - File CRM Completo" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica file
$files = @(
    "ur_portal_direct_playwright.py",
    "ur_portal_integration.py",
    "crm_app_completo.py",
    "sync_offers_2025_2026.py",
    "pulisci_nomi_account.py",
    "templates\app_mekocrm_completo.html"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        Write-Host "ERRORE: File non trovato: $file" -ForegroundColor Red
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
}

Write-Host "✓ Tutti i file trovati" -ForegroundColor Green
Write-Host ""

# Chiedi IP EC2
$EC2_IP = Read-Host "Inserisci l'IP pubblico della macchina EC2"
if ([string]::IsNullOrWhiteSpace($EC2_IP)) {
    Write-Host "ERRORE: IP non inserito!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

# Chiedi percorso chiave
$KEY_PATH = Read-Host "Inserisci il percorso completo della chiave .pem (es: C:\Users\user\chiave.pem)"
if ([string]::IsNullOrWhiteSpace($KEY_PATH)) {
    Write-Host "ERRORE: Percorso chiave non inserito!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

if (-not (Test-Path $KEY_PATH)) {
    Write-Host "ERRORE: File chiave non trovato: $KEY_PATH" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Caricamento file su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se SCP è disponibile
$scpAvailable = $false
try {
    $null = Get-Command scp -ErrorAction Stop
    $scpAvailable = $true
} catch {
    Write-Host "⚠ SCP non trovato. Verifica che OpenSSH sia installato." -ForegroundColor Yellow
    Write-Host "  Installa con: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Yellow
}

if (-not $scpAvailable) {
    Write-Host ""
    Write-Host "OPZIONE ALTERNATIVA:" -ForegroundColor Yellow
    Write-Host "Usa WinSCP o carica manualmente i file:" -ForegroundColor Yellow
    Write-Host "  1. ur_portal_direct_playwright.py" -ForegroundColor White
    Write-Host "  2. ur_portal_integration.py" -ForegroundColor White
    Write-Host "  3. crm_app_completo.py" -ForegroundColor White
    Write-Host "  4. sync_offers_2025_2026.py" -ForegroundColor White
    Write-Host "  5. pulisci_nomi_account.py" -ForegroundColor White
    Write-Host "  6. templates\app_mekocrm_completo.html" -ForegroundColor White
    Write-Host ""
    Write-Host "Poi connetti via SSH e riavvia:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
    Read-Host "Premi INVIO per uscire"
    exit 0
}

# Carica file
$fileMap = @{
    "ur_portal_direct_playwright.py" = "/home/ubuntu/offermanager/"
    "ur_portal_integration.py" = "/home/ubuntu/offermanager/"
    "crm_app_completo.py" = "/home/ubuntu/offermanager/"
    "sync_offers_2025_2026.py" = "/home/ubuntu/offermanager/"
    "pulisci_nomi_account.py" = "/home/ubuntu/offermanager/"
    "templates\app_mekocrm_completo.html" = "/home/ubuntu/offermanager/templates/"
}

$index = 1
foreach ($file in $files) {
    $remotePath = $fileMap[$file]
    Write-Host "[$index/$($files.Count)] Caricamento $file..." -ForegroundColor Yellow
    
    $scpCommand = "scp -i `"$KEY_PATH`" `"$file`" ubuntu@${EC2_IP}:${remotePath}"
    
    try {
        Invoke-Expression $scpCommand
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $file caricato" -ForegroundColor Green
        } else {
            Write-Host "✗ Errore durante il caricamento di $file" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Errore: $_" -ForegroundColor Red
    }
    
    $index++
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Riavvio servizio su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Riavvia servizio
$sshCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"sudo systemctl restart offermanager`""
try {
    Invoke-Expression $sshCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Servizio riavviato" -ForegroundColor Green
    } else {
        Write-Host "⚠ Impossibile riavviare automaticamente" -ForegroundColor Yellow
        Write-Host "  Esegui manualmente:" -ForegroundColor Yellow
        Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
        Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
    }
} catch {
    Write-Host "⚠ Errore: $_" -ForegroundColor Yellow
    Write-Host "  Esegui manualmente:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  ✅ AGGIORNAMENTO COMPLETATO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verifica lo stato con:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP `"sudo systemctl status offermanager`"" -ForegroundColor White
Write-Host ""
Write-Host "Oppure apri nel browser:" -ForegroundColor Cyan
Write-Host "  http://$EC2_IP" -ForegroundColor White
Write-Host ""
Read-Host "Premi INVIO per uscire"








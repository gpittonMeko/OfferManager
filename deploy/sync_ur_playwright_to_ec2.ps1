# Script veloce per sincronizzare ur_portal_direct_playwright.py su EC2
# Uso: .\sync_ur_playwright_to_ec2.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  SINCRONIZZA ur_portal_direct_playwright.py su EC2" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica file
$file = "ur_portal_direct_playwright.py"
if (-not (Test-Path $file)) {
    Write-Host "ERRORE: File non trovato: $file" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host "✓ File trovato: $file" -ForegroundColor Green
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
    Write-Host "Usa WinSCP o carica manualmente il file:" -ForegroundColor Yellow
    Write-Host "  $file -> /home/ubuntu/offermanager/$file" -ForegroundColor White
    Write-Host ""
    Write-Host "Poi connetti via SSH e riavvia:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
    Read-Host "Premi INVIO per uscire"
    exit 0
}

# Carica file
Write-Host "Caricamento $file..." -ForegroundColor Yellow

$scpCommand = "scp -i `"$KEY_PATH`" `"$file`" ubuntu@${EC2_IP}:/home/ubuntu/offermanager/"

try {
    Invoke-Expression $scpCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $file caricato con successo!" -ForegroundColor Green
    } else {
        Write-Host "✗ Errore durante il caricamento di $file" -ForegroundColor Red
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
} catch {
    Write-Host "✗ Errore: $_" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
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
Write-Host "  ✅ SINCRONIZZAZIONE COMPLETATA!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Il file ur_portal_direct_playwright.py è stato aggiornato sulla EC2" -ForegroundColor Cyan
Write-Host "con tutte le modifiche per l'estrazione dei leads." -ForegroundColor Cyan
Write-Host ""
Read-Host "Premi INVIO per uscire"


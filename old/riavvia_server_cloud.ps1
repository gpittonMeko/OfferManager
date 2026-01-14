# Script per riavviare il server sulla macchina cloud
# Carica solo crm_app_completo.py modificato e riavvia il servizio

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  RIAVVIO SERVER CLOUD" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Chiedi IP EC2
$EC2_IP = Read-Host "Inserisci l'IP pubblico della macchina EC2"
if ([string]::IsNullOrWhiteSpace($EC2_IP)) {
    Write-Host "ERRORE: IP non inserito!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

# Chiedi percorso chiave
$KEY_PATH = Read-Host "Inserisci il percorso completo della chiave .pem"
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

# Verifica che crm_app_completo.py esista
if (-not (Test-Path "crm_app_completo.py")) {
    Write-Host "ERRORE: File crm_app_completo.py non trovato!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Caricamento crm_app_completo.py su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Carica file
$scpCommand = "scp -i `"$KEY_PATH`" `"crm_app_completo.py`" ubuntu@${EC2_IP}:/home/ubuntu/offermanager/"

try {
    Invoke-Expression $scpCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ File caricato" -ForegroundColor Green
    } else {
        Write-Host "✗ Errore durante il caricamento" -ForegroundColor Red
        Write-Host "  Esegui manualmente:" -ForegroundColor Yellow
        Write-Host "  $scpCommand" -ForegroundColor White
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
} catch {
    Write-Host "✗ Errore: $_" -ForegroundColor Red
    Write-Host "  Esegui manualmente:" -ForegroundColor Yellow
    Write-Host "  $scpCommand" -ForegroundColor White
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Riavvio servizio offermanager..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Riavvia servizio
$sshCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"sudo systemctl restart offermanager`""

try {
    Invoke-Expression $sshCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Servizio riavviato con successo!" -ForegroundColor Green
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
Write-Host "  ✅ RIAVVIO COMPLETATO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verifica lo stato con:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP `"sudo systemctl status offermanager`"" -ForegroundColor White
Write-Host ""
Read-Host "Premi INVIO per uscire"

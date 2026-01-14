# Script per riavviare il server sulla macchina cloud
# Usa credenziali trovate nella repository

$EC2_IP = "13.53.183.146"
$KEY_PATH = "C:\Users\user\Documents\LLM_14.pem"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  RIAVVIO SERVER CLOUD" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IP EC2: $EC2_IP" -ForegroundColor Yellow
Write-Host "Chiave: $KEY_PATH" -ForegroundColor Yellow
Write-Host ""

# Verifica chiave
if (-not (Test-Path $KEY_PATH)) {
    Write-Host "ERRORE: File chiave non trovato: $KEY_PATH" -ForegroundColor Red
    Write-Host "Verifica il percorso della chiave .pem" -ForegroundColor Yellow
    Read-Host "Premi INVIO per uscire"
    exit 1
}

# Verifica file
if (-not (Test-Path "crm_app_completo.py")) {
    Write-Host "ERRORE: File crm_app_completo.py non trovato!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Caricamento crm_app_completo.py su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Carica file usando cmd per evitare problemi di parsing
$scpCmd = "scp -i `"$KEY_PATH`" crm_app_completo.py ubuntu@${EC2_IP}:/home/ubuntu/offermanager/"
$scpResult = cmd /c $scpCmd 2>&1
$scpExitCode = $LASTEXITCODE

if ($scpExitCode -eq 0) {
    Write-Host "✓ File caricato con successo" -ForegroundColor Green
} else {
    Write-Host "✗ Errore durante il caricamento" -ForegroundColor Red
    Write-Host $scpResult -ForegroundColor Red
    Write-Host "  Esegui manualmente:" -ForegroundColor Yellow
    Write-Host "  $scpCmd" -ForegroundColor White
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Riavvio servizio offermanager..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Riavvia servizio usando cmd
$sshCmd = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} sudo systemctl restart offermanager"
$sshResult = cmd /c $sshCmd 2>&1
$sshExitCode = $LASTEXITCODE

if ($sshExitCode -eq 0) {
    Write-Host "✓ Servizio riavviato con successo!" -ForegroundColor Green
} else {
    Write-Host "⚠ Impossibile riavviare automaticamente" -ForegroundColor Yellow
    Write-Host $sshResult -ForegroundColor Yellow
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

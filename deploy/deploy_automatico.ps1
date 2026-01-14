# Script PowerShell per deploy automatico su AWS EC2
# Usa valori di default se disponibili

param(
    [string]$EC2_IP = "",
    [string]$KEY_PATH = "C:\Users\user\Documents\LLM_14.pem"
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATICO SU AWS EC2" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica file
$files = @(
    "crm_app_completo.py",
    "sync_offers_2025_2026.py",
    "pulisci_nomi_account.py",
    "associa_indirizzi_contatti.py",
    "add_user_local_pc_columns.py",
    "templates\app_mekocrm_completo.html"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        Write-Host "ERRORE: File non trovato: $file" -ForegroundColor Red
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
}

Write-Host "Tutti i file trovati" -ForegroundColor Green
Write-Host ""

# Verifica chiave
if (-not (Test-Path $KEY_PATH)) {
    Write-Host "ERRORE: File chiave non trovato: $KEY_PATH" -ForegroundColor Red
    $KEY_PATH = Read-Host "Inserisci il percorso completo della chiave .pem"
    if (-not (Test-Path $KEY_PATH)) {
        Write-Host "ERRORE: File chiave non trovato!" -ForegroundColor Red
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
}

# Chiedi IP se non fornito
if ([string]::IsNullOrWhiteSpace($EC2_IP)) {
    $EC2_IP = Read-Host "Inserisci l IP pubblico della macchina EC2"
    if ([string]::IsNullOrWhiteSpace($EC2_IP)) {
        Write-Host "ERRORE: IP non inserito!" -ForegroundColor Red
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
}

Write-Host ""
Write-Host "Configurazione:" -ForegroundColor Yellow
Write-Host "  IP EC2: $EC2_IP" -ForegroundColor White
Write-Host "  Chiave: $KEY_PATH" -ForegroundColor White
Write-Host ""

# Verifica se SCP e disponibile
$scpAvailable = $false
try {
    $null = Get-Command scp -ErrorAction Stop
    $scpAvailable = $true
} catch {
    Write-Host "SCP non trovato. Verifica che OpenSSH sia installato." -ForegroundColor Yellow
}

if (-not $scpAvailable) {
    Write-Host ""
    Write-Host "OPZIONE ALTERNATIVA:" -ForegroundColor Yellow
    Write-Host "Usa WinSCP o carica manualmente i file:" -ForegroundColor Yellow
    foreach ($file in $files) {
        Write-Host "  - $file" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Poi connetti via SSH e riavvia:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
    Read-Host "Premi INVIO per uscire"
    exit 0
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Caricamento file su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Carica file
$fileMap = @{
    "crm_app_completo.py" = "/home/ubuntu/offermanager/"
    "sync_offers_2025_2026.py" = "/home/ubuntu/offermanager/"
    "pulisci_nomi_account.py" = "/home/ubuntu/offermanager/"
    "associa_indirizzi_contatti.py" = "/home/ubuntu/offermanager/"
    "add_user_local_pc_columns.py" = "/home/ubuntu/offermanager/"
    "templates\app_mekocrm_completo.html" = "/home/ubuntu/offermanager/templates/"
}

$index = 1
$errors = 0
foreach ($file in $files) {
    $remotePath = $fileMap[$file]
    Write-Host "[$index/$($files.Count)] Caricamento $file..." -ForegroundColor Yellow
    
    $scpCommand = "scp -i `"$KEY_PATH`" `"$file`" ubuntu@${EC2_IP}:${remotePath}"
    
    try {
        $output = Invoke-Expression $scpCommand 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "File caricato: $file" -ForegroundColor Green
        } else {
            Write-Host "Errore durante il caricamento di $file" -ForegroundColor Red
            Write-Host $output -ForegroundColor Red
            $errors++
        }
    } catch {
        Write-Host "Errore: $_" -ForegroundColor Red
        $errors++
    }
    
    $index++
    Write-Host ""
}

if ($errors -gt 0) {
    Write-Host "ATTENZIONE: $errors errori durante il caricamento!" -ForegroundColor Yellow
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Riavvio servizio su EC2..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Riavvia servizio
$sshCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"sudo systemctl restart offermanager`""
try {
    $output = Invoke-Expression $sshCommand 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Servizio riavviato" -ForegroundColor Green
    } else {
        Write-Host "Impossibile riavviare automaticamente" -ForegroundColor Yellow
        Write-Host $output -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Esegui manualmente:" -ForegroundColor Yellow
        Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
        Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
    }
} catch {
    Write-Host "Errore: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Esegui manualmente:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  sudo systemctl restart offermanager" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  DEPLOY COMPLETATO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verifica lo stato con:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP `"sudo systemctl status offermanager`"" -ForegroundColor White
Write-Host ""
Write-Host "Oppure apri nel browser:" -ForegroundColor Cyan
Write-Host "  http://$EC2_IP" -ForegroundColor White
Write-Host ""
Read-Host "Premi INVIO per uscire"

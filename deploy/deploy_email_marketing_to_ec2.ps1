# Script PowerShell per aggiornare sistema Email Marketing su EC2
# Uso: .\deploy_email_marketing_to_ec2.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY EMAIL MARKETING su EC2" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Lista file da caricare (Email Marketing + CRM aggiornato)
$files = @(
    "crm_app_completo.py",
    "mailgun_service.py",
    "email_template_loader.py",
    "requirements.txt",
    "templates\app_mekocrm_completo.html",
    "templates\email\base_template.html",
    "templates\email\newsletter_template.html",
    "templates\email\promotional_template.html",
    "templates\email\transactional_template.html",
    "EMAIL_MARKETING_SETUP.md"
)

# Verifica file
Write-Host "Verifica file locali..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        Write-Host "  ✗ File non trovato: $file" -ForegroundColor Red
        $missingFiles += $file
    } else {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERRORE: Alcuni file mancano!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
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

# Verifica SCP
$scpAvailable = $false
try {
    $null = Get-Command scp -ErrorAction Stop
    $scpAvailable = $true
} catch {
    Write-Host "⚠ SCP non trovato. Installa OpenSSH:" -ForegroundColor Yellow
    Write-Host "  Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Oppure usa WinSCP per caricare manualmente i file." -ForegroundColor Yellow
    Read-Host "Premi INVIO per uscire"
    exit 1
}

# Mapping file -> percorso remoto
$fileMap = @{
    "crm_app_completo.py" = "/home/ubuntu/offermanager/"
    "mailgun_service.py" = "/home/ubuntu/offermanager/"
    "email_template_loader.py" = "/home/ubuntu/offermanager/"
    "requirements.txt" = "/home/ubuntu/offermanager/"
    "templates\app_mekocrm_completo.html" = "/home/ubuntu/offermanager/templates/"
    "templates\email\base_template.html" = "/home/ubuntu/offermanager/templates/email/"
    "templates\email\newsletter_template.html" = "/home/ubuntu/offermanager/templates/email/"
    "templates\email\promotional_template.html" = "/home/ubuntu/offermanager/templates/email/"
    "templates\email\transactional_template.html" = "/home/ubuntu/offermanager/templates/email/"
    "EMAIL_MARKETING_SETUP.md" = "/home/ubuntu/offermanager/"
}

# Crea directory templates/email su EC2
Write-Host "[PRE] Creazione directory templates/email su EC2..." -ForegroundColor Yellow
$mkdirCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"mkdir -p /home/ubuntu/offermanager/templates/email`""
try {
    Invoke-Expression $mkdirCommand
    Write-Host "✓ Directory creata" -ForegroundColor Green
} catch {
    Write-Host "⚠ Errore creazione directory: $_" -ForegroundColor Yellow
}
Write-Host ""

# Carica file
$index = 1
$total = $files.Count
foreach ($file in $files) {
    $remotePath = $fileMap[$file]
    Write-Host "[$index/$total] Caricamento $file..." -ForegroundColor Yellow
    
    $scpCommand = "scp -i `"$KEY_PATH`" `"$file`" ubuntu@${EC2_IP}:${remotePath}"
    
    try {
        Invoke-Expression $scpCommand
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $file caricato" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Errore durante il caricamento" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Errore: $_" -ForegroundColor Red
    }
    
    $index++
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Installazione dipendenze Python..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Installa dipendenze Python
$installCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"cd /home/ubuntu/offermanager && pip3 install -r requirements.txt`""
Write-Host "Installazione dipendenze..." -ForegroundColor Yellow
try {
    Invoke-Expression $installCommand
    Write-Host "✓ Dipendenze installate" -ForegroundColor Green
} catch {
    Write-Host "⚠ Errore installazione dipendenze (potrebbe essere normale se già installate)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Inizializzazione database..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Crea tabelle database
$dbCommand = "ssh -i `"$KEY_PATH`" ubuntu@${EC2_IP} `"cd /home/ubuntu/offermanager && python3 -c 'from crm_app_completo import db, app; app.app_context().push(); db.create_all()'`""
Write-Host "Creazione tabelle email marketing..." -ForegroundColor Yellow
try {
    Invoke-Expression $dbCommand
    Write-Host "✓ Tabelle database create/aggiornate" -ForegroundColor Green
} catch {
    Write-Host "⚠ Errore creazione tabelle (potrebbe essere normale se già esistenti)" -ForegroundColor Yellow
    Write-Host "  Le tabelle verranno create automaticamente al primo avvio" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Riavvio servizio..." -ForegroundColor Cyan
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
    }
} catch {
    Write-Host "⚠ Errore riavvio: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY COMPLETATO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE: Configura le variabili d'ambiente Mailgun su EC2:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
Write-Host ""
Write-Host "Poi aggiungi al file /home/ubuntu/offermanager/.env o al systemd service:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  MAILGUN_API_KEY=your-key" -ForegroundColor White
Write-Host "  MAILGUN_DOMAIN=your-domain.mailgun.org" -ForegroundColor White
Write-Host "  MAILGUN_FROM_EMAIL=noreply@yourdomain.com" -ForegroundColor White
Write-Host "  MAILGUN_FROM_NAME=ME.KO. Srl" -ForegroundColor White
Write-Host "  MAILGUN_API_REGION=eu" -ForegroundColor White
Write-Host ""
Write-Host "Verifica lo stato:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP `"sudo systemctl status offermanager`"" -ForegroundColor White
Write-Host ""
Write-Host "Oppure apri nel browser:" -ForegroundColor Cyan
Write-Host "  http://$EC2_IP" -ForegroundColor White
Write-Host ""
Read-Host "Premi INVIO per uscire"










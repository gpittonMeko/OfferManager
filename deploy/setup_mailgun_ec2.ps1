# Script per configurare Mailgun su EC2
param(
    [string]$EC2_IP = "13.53.183.146",
    [string]$KEY_PATH = "C:\Users\user\Documents\LLM_14.pem"
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAZIONE MAILGUN su EC2" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Chiedi credenziali Mailgun
Write-Host "Inserisci le credenziali Mailgun:" -ForegroundColor Yellow
Write-Host ""

$MAILGUN_API_KEY = Read-Host "API Key Privata (key-xxxxx o 67edcffb-98ade982)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_API_KEY)) {
    Write-Host "ERRORE: API Key richiesta!" -ForegroundColor Red
    exit 1
}

$MAILGUN_DOMAIN = Read-Host "Dominio Mailgun (es: sandbox123.mailgun.org o dominio verificato)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_DOMAIN)) {
    Write-Host "ERRORE: Dominio richiesto!" -ForegroundColor Red
    exit 1
}

$MAILGUN_FROM_EMAIL = Read-Host "Email mittente (default: noreply@$($MAILGUN_DOMAIN.Split('.')[0]).com)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_FROM_EMAIL)) {
    $MAILGUN_FROM_EMAIL = "noreply@$($MAILGUN_DOMAIN.Split('.')[0]).com"
}

$MAILGUN_FROM_NAME = Read-Host "Nome mittente (default: ME.KO. Srl)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_FROM_NAME)) {
    $MAILGUN_FROM_NAME = "ME.KO. Srl"
}

$MAILGUN_API_REGION = Read-Host "Regione API (eu/us, default: eu)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_API_REGION)) {
    $MAILGUN_API_REGION = "eu"
}

Write-Host ""
Write-Host "Configurazione:" -ForegroundColor Yellow
Write-Host "  API Key: $($MAILGUN_API_KEY.Substring(0, [Math]::Min(20, $MAILGUN_API_KEY.Length)))..." -ForegroundColor White
Write-Host "  Dominio: $MAILGUN_DOMAIN" -ForegroundColor White
Write-Host "  From Email: $MAILGUN_FROM_EMAIL" -ForegroundColor White
Write-Host "  From Name: $MAILGUN_FROM_NAME" -ForegroundColor White
Write-Host "  Regione: $MAILGUN_API_REGION" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Confermi? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Annullato." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Caricamento configurazione su EC2..." -ForegroundColor Yellow

# Leggi il file systemd service
$serviceContent = ssh -i "`"$KEY_PATH`" ubuntu@${EC2_IP} "sudo cat /etc/systemd/system/offermanager.service"

# Aggiungi variabili d'ambiente se non ci sono già
if ($serviceContent -notmatch "MAILGUN_API_KEY") {
    Write-Host "Aggiornamento file systemd service..." -ForegroundColor Yellow
    
    # Crea backup
    ssh -i "`"$KEY_PATH`" ubuntu@${EC2_IP} "sudo cp /etc/systemd/system/offermanager.service /etc/systemd/system/offermanager.service.backup"
    
    # Aggiungi variabili d'ambiente
    $envVars = @"
Environment="MAILGUN_API_KEY=$MAILGUN_API_KEY"
Environment="MAILGUN_DOMAIN=$MAILGUN_DOMAIN"
Environment="MAILGUN_FROM_EMAIL=$MAILGUN_FROM_EMAIL"
Environment="MAILGUN_FROM_NAME=$MAILGUN_FROM_NAME"
Environment="MAILGUN_API_REGION=$MAILGUN_API_REGION"
"@
    
    # Usa un here-string per modificare il file
    $updateScript = @"
cd /tmp
sudo cp /etc/systemd/system/offermanager.service /etc/systemd/system/offermanager.service.backup
sudo sed -i '/\[Service\]/a Environment="MAILGUN_API_KEY=$MAILGUN_API_KEY"\nEnvironment="MAILGUN_DOMAIN=$MAILGUN_DOMAIN"\nEnvironment="MAILGUN_FROM_EMAIL=$MAILGUN_FROM_EMAIL"\nEnvironment="MAILGUN_FROM_NAME=$MAILGUN_FROM_NAME"\nEnvironment="MAILGUN_API_REGION=$MAILGUN_API_REGION"' /etc/systemd/system/offermanager.service
"@
    
    # Salva script temporaneo
    $updateScript | Out-File -FilePath "update_service_temp.sh" -Encoding ASCII -NoNewline
    
    # Carica e esegui
    scp -i "`"$KEY_PATH`" "update_service_temp.sh" ubuntu@${EC2_IP}:~/update_service.sh
    ssh -i "`"$KEY_PATH`" ubuntu@${EC2_IP} "bash ~/update_service.sh && sudo systemctl daemon-reload"
    
    # Rimuovi file temporaneo
    Remove-Item "update_service_temp.sh" -ErrorAction SilentlyContinue
    
    Write-Host "✓ Configurazione aggiornata" -ForegroundColor Green
} else {
    Write-Host "⚠ Configurazione Mailgun già presente. Aggiornamento manuale richiesto." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Riavvio servizio..." -ForegroundColor Yellow
ssh -i "`"$KEY_PATH`" ubuntu@${EC2_IP} "sudo systemctl restart offermanager"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  ✅ CONFIGURAZIONE COMPLETATA!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verifica lo stato:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP `"sudo systemctl status offermanager`"" -ForegroundColor White
Write-Host ""
Read-Host "Premi INVIO per uscire"








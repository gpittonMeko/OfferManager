# Script PowerShell per configurare Mailgun automaticamente su EC2
param(
    [string]$EC2_IP = "13.53.183.146",
    [string]$KEY_PATH = "C:\Users\user\Documents\LLM_14.pem"
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAZIONE MAILGUN AUTOMATICA" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Per trovare le credenziali:" -ForegroundColor Yellow
Write-Host "  1. API Key: https://app.mailgun.com/app/api-keys" -ForegroundColor White
Write-Host "     - Clicca su Key ID: 67edcffb-98ade982" -ForegroundColor Gray
Write-Host "     - Clicca 'Reveal' per vedere la chiave privata" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Domain: https://app.mailgun.com/app/sending/domains" -ForegroundColor White
Write-Host "     - Copia il dominio verificato" -ForegroundColor Gray
Write-Host ""

# Chiedi credenziali
$MAILGUN_API_KEY = Read-Host "Inserisci la CHIAVE API PRIVATA Mailgun (key-...)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_API_KEY)) {
    Write-Host "ERRORE: API Key richiesta!" -ForegroundColor Red
    exit 1
}

$MAILGUN_DOMAIN = Read-Host "Inserisci il DOMINIO Mailgun (es: sandbox123.mailgun.org)"
if ([string]::IsNullOrWhiteSpace($MAILGUN_DOMAIN)) {
    Write-Host "ERRORE: Dominio richiesto!" -ForegroundColor Red
    exit 1
}

$MAILGUN_FROM_EMAIL = Read-Host "Email mittente (default: noreply@meko.it) [Premi INVIO per default]"
if ([string]::IsNullOrWhiteSpace($MAILGUN_FROM_EMAIL)) {
    $MAILGUN_FROM_EMAIL = "noreply@meko.it"
}

$MAILGUN_FROM_NAME = Read-Host "Nome mittente (default: ME.KO. Srl) [Premi INVIO per default]"
if ([string]::IsNullOrWhiteSpace($MAILGUN_FROM_NAME)) {
    $MAILGUN_FROM_NAME = "ME.KO. Srl"
}

$MAILGUN_API_REGION = Read-Host "Regione API (eu/us, default: eu) [Premi INVIO per default]"
if ([string]::IsNullOrWhiteSpace($MAILGUN_API_REGION)) {
    $MAILGUN_API_REGION = "eu"
}

Write-Host ""
Write-Host "Configurazione:" -ForegroundColor Yellow
Write-Host "  API Key: $($MAILGUN_API_KEY.Substring(0, [Math]::Min(20, $MAILGUN_API_KEY.Length)))..." -ForegroundColor White
Write-Host "  Domain: $MAILGUN_DOMAIN" -ForegroundColor White
Write-Host "  From Email: $MAILGUN_FROM_EMAIL" -ForegroundColor White
Write-Host "  From Name: $MAILGUN_FROM_NAME" -ForegroundColor White
Write-Host "  Region: $MAILGUN_API_REGION" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Confermi? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Annullato." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Configurazione in corso su EC2..." -ForegroundColor Yellow
Write-Host ""

# Escape delle virgolette per il comando SSH
$API_KEY_ESCAPED = $MAILGUN_API_KEY -replace "'", "'\"'\"'"
$DOMAIN_ESCAPED = $MAILGUN_DOMAIN -replace "'", "'\"'\"'"
$FROM_EMAIL_ESCAPED = $MAILGUN_FROM_EMAIL -replace "'", "'\"'\"'"
$FROM_NAME_ESCAPED = $MAILGUN_FROM_NAME -replace "'", "'\"'\"'"

# Esegui configurazione remota
$command = "~/configure_mailgun_auto.sh '$API_KEY_ESCAPED' '$DOMAIN_ESCAPED' '$FROM_EMAIL_ESCAPED' '$FROM_NAME_ESCAPED' '$MAILGUN_API_REGION'"

Write-Host "Esecuzione comando su EC2..." -ForegroundColor Yellow
ssh -i "`"$KEY_PATH`" ubuntu@${EC2_IP} $command

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  ✅ CONFIGURAZIONE COMPLETATA CON SUCCESSO!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Il sistema Email Marketing è ora configurato!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Prossimi passi:" -ForegroundColor Yellow
    Write-Host "  1. Accedi al CRM: http://$EC2_IP:8000" -ForegroundColor White
    Write-Host "  2. Vai su '📧 Email Marketing' nel menu" -ForegroundColor White
    Write-Host "  3. Crea la tua prima lista email" -ForegroundColor White
    Write-Host "  4. Carica i template: POST /api/email/templates/init-defaults" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠ Errore durante la configurazione. Verifica manualmente:" -ForegroundColor Yellow
    Write-Host "  ssh -i `"$KEY_PATH`" ubuntu@$EC2_IP" -ForegroundColor White
    Write-Host "  ~/configure_mailgun_auto.sh ..." -ForegroundColor White
    Write-Host ""
}

Read-Host "Premi INVIO per uscire"








#!/bin/bash
# Script automatico per configurare Mailgun su EC2

# Parametri
MAILGUN_API_KEY="${1}"
MAILGUN_DOMAIN="${2}"
MAILGUN_FROM_EMAIL="${3:-noreply@meko.it}"
MAILGUN_FROM_NAME="${4:-ME.KO. Srl}"
MAILGUN_API_REGION="${5:-eu}"

if [ -z "$MAILGUN_API_KEY" ] || [ -z "$MAILGUN_DOMAIN" ]; then
    echo "ERRORE: API Key e Domain sono obbligatori!"
    echo "Uso: $0 <API_KEY> <DOMAIN> [FROM_EMAIL] [FROM_NAME] [REGION]"
    exit 1
fi

echo "================================================================"
echo "  CONFIGURAZIONE MAILGUN AUTOMATICA"
echo "================================================================"
echo ""
echo "API Key: ${MAILGUN_API_KEY:0:20}..."
echo "Domain: $MAILGUN_DOMAIN"
echo "From Email: $MAILGUN_FROM_EMAIL"
echo "From Name: $MAILGUN_FROM_NAME"
echo "Region: $MAILGUN_API_REGION"
echo ""

# Backup
echo "Backup configurazione..."
sudo cp /etc/systemd/system/offermanager.service /etc/systemd/system/offermanager.service.backup

# Rimuovi vecchie configurazioni Mailgun se esistono
sudo sed -i '/MAILGUN_/d' /etc/systemd/system/offermanager.service

# Aggiungi nuove variabili d'ambiente dopo [Service]
sudo sed -i "/\[Service\]/a\\
Environment=\"MAILGUN_API_KEY=$MAILGUN_API_KEY\"\\
Environment=\"MAILGUN_DOMAIN=$MAILGUN_DOMAIN\"\\
Environment=\"MAILGUN_FROM_EMAIL=$MAILGUN_FROM_EMAIL\"\\
Environment=\"MAILGUN_FROM_NAME=$MAILGUN_FROM_NAME\"\\
Environment=\"MAILGUN_API_REGION=$MAILGUN_API_REGION\"" /etc/systemd/system/offermanager.service

echo "✓ Variabili d'ambiente aggiunte"

# Ricarica systemd
echo "Ricaricamento systemd..."
sudo systemctl daemon-reload

# Riavvia servizio
echo "Riavvio servizio..."
sudo systemctl restart offermanager

# Attendi un secondo
sleep 2

# Verifica stato
echo ""
echo "Verifica stato servizio:"
sudo systemctl status offermanager --no-pager | head -10

echo ""
echo "================================================================"
echo "  ✅ CONFIGURAZIONE COMPLETATA!"
echo "================================================================"
echo ""
echo "Per testare, accedi a: http://$(curl -s ifconfig.me):8000"
echo ""








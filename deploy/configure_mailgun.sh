#!/bin/bash
# Script per configurare Mailgun su EC2

echo "================================================================"
echo "  CONFIGURAZIONE MAILGUN"
echo "================================================================"
echo ""

# Chiedi credenziali
read -p "Mailgun API Key (key-xxxxx): " MAILGUN_API_KEY
read -p "Mailgun Domain (es: sandbox123.mailgun.org): " MAILGUN_DOMAIN
read -p "From Email (default: noreply@meko.it): " MAILGUN_FROM_EMAIL
MAILGUN_FROM_EMAIL=${MAILGUN_FROM_EMAIL:-noreply@meko.it}
read -p "From Name (default: ME.KO. Srl): " MAILGUN_FROM_NAME
MAILGUN_FROM_NAME=${MAILGUN_FROM_NAME:-ME.KO. Srl}
read -p "API Region (eu/us, default: eu): " MAILGUN_API_REGION
MAILGUN_API_REGION=${MAILGUN_API_REGION:-eu}

echo ""
echo "Aggiungo variabili d'ambiente al servizio systemd..."

# Backup
sudo cp /etc/systemd/system/offermanager.service /etc/systemd/system/offermanager.service.backup

# Crea file temporaneo con le nuove variabili
sudo tee /tmp/mailgun_env.txt > /dev/null <<EOF
Environment="MAILGUN_API_KEY=$MAILGUN_API_KEY"
Environment="MAILGUN_DOMAIN=$MAILGUN_DOMAIN"
Environment="MAILGUN_FROM_EMAIL=$MAILGUN_FROM_EMAIL"
Environment="MAILGUN_FROM_NAME=$MAILGUN_FROM_NAME"
Environment="MAILGUN_API_REGION=$MAILGUN_API_REGION"
EOF

# Aggiungi dopo [Service]
sudo sed -i '/\[Service\]/r /tmp/mailgun_env.txt' /etc/systemd/system/offermanager.service

# Rimuovi file temp
rm /tmp/mailgun_env.txt

echo "✓ Configurazione aggiornata"
echo ""
echo "Ricaricamento systemd..."
sudo systemctl daemon-reload

echo "Riavvio servizio..."
sudo systemctl restart offermanager

echo ""
echo "================================================================"
echo "  ✅ CONFIGURAZIONE COMPLETATA!"
echo "================================================================"
echo ""
echo "Verifica lo stato:"
echo "  sudo systemctl status offermanager"
echo ""








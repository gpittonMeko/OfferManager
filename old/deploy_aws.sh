#!/bin/bash
# Script di deployment per AWS EC2 - Ottimizzato per t2.micro

echo "============================================================"
echo "  OfferManager - Deploy su AWS EC2 (Free Tier)"
echo "============================================================"
echo ""

# Aggiorna sistema (silenzioso per velocità)
echo "[1/7] Aggiornamento sistema..."
sudo apt update -qq
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq

# Installa Python e dipendenze
echo ""
echo "[2/7] Installazione Python..."
sudo apt install -y python3 python3-pip python3-venv nginx

# I file sono già in /home/ubuntu/offermanager
echo ""
echo "[3/7] Verifica file caricati..."
cd /home/ubuntu/offermanager
if [ ! -f "requirements_cloud.txt" ]; then
    echo "ERRORE: File non trovati! Carica i file prima."
    exit 1
fi
echo "✓ File presenti"

# Crea ambiente virtuale
echo ""
echo "[4/7] Setup ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install --quiet -r requirements_cloud.txt

# Configura Nginx
echo ""
echo "[5/7] Configurazione Nginx..."
sudo tee /etc/nginx/sites-available/offermanager > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/offermanager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Crea systemd service (1 worker per t2.micro = risparmio RAM)
echo ""
echo "[6/7] Creazione servizio systemd..."
sudo tee /etc/systemd/system/offermanager.service > /dev/null <<EOF
[Unit]
Description=OfferManager CRM
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/offermanager
Environment="PATH=/home/ubuntu/offermanager/venv/bin"
ExecStart=/home/ubuntu/offermanager/venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 crm_app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable offermanager
sudo systemctl start offermanager

echo ""
echo "[7/7] Verifica servizio..."
sleep 3
sudo systemctl status offermanager --no-pager

echo ""
echo "============================================================"
echo "  ✅ DEPLOYMENT COMPLETATO!"
echo "============================================================"
echo ""
PUBLIC_IP=$(curl -s ifconfig.me)
echo "🌐 App raggiungibile su: http://$PUBLIC_IP"
echo ""
echo "👤 Login:"
echo "   Username: marco"
echo "   Password: demo123"
echo ""
echo "💰 RISPARMIO COSTI:"
echo "   • t2.micro Free Tier: GRATIS primo anno"
echo "   • Dopo: ~8€/mese"
echo "   • STOP istanza quando non usi = 0€"
echo ""
echo "📊 Comandi utili:"
echo "  sudo systemctl status offermanager    # Stato"
echo "  sudo systemctl restart offermanager   # Riavvia"
echo "  sudo journalctl -u offermanager -f    # Log"
echo ""


# 🌐 Deploy OfferManager su AWS EC2

## Setup Rapido (10 minuti)

### 1. Crea Istanza EC2

1. **Accedi ad AWS Console**: https://console.aws.amazon.com/ec2
2. **Launch Instance**
3. **Configurazione**:
   - Nome: `OfferManager`
   - AMI: **Ubuntu Server 22.04 LTS**
   - Instance type: **t2.micro** (Free tier eligible)
   - Key pair: Crea o usa esistente
   - Security Group: 
     - ✅ SSH (22) - Il tuo IP
     - ✅ HTTP (80) - 0.0.0.0/0
     - ✅ HTTPS (443) - 0.0.0.0/0
4. **Launch**

### 2. Connetti via SSH

```bash
ssh -i "tua-chiave.pem" ubuntu@<IP-PUBBLICO-EC2>
```

### 3. Carica File

**Opzione A: SCP da Windows**
```bash
scp -i "tua-chiave.pem" -r * ubuntu@<IP-EC2>:/home/ubuntu/offermanager/
```

**Opzione B: Git** (se hai repo)
```bash
git clone <tuo-repo> /home/ubuntu/offermanager
```

**Opzione C: Manuale**
Usa FileZilla/WinSCP con la chiave .pem

### 4. Esegui Deploy

```bash
cd /home/ubuntu/offermanager
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### 5. Accedi

Apri browser: `http://<IP-PUBBLICO-EC2>`

---

## 🎯 Deployment Manuale (Passo-Passo)

### Connetti a EC2
```bash
ssh -i "chiave.pem" ubuntu@<IP-EC2>
```

### Installa Dipendenze
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
```

### Setup App
```bash
# Crea directory
sudo mkdir -p /var/www/offermanager
sudo chown -R $USER:$USER /var/www/offermanager
cd /var/www/offermanager

# Carica file (usa scp o git)
# Poi:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements_cloud.txt
```

### Configura Nginx
```bash
sudo nano /etc/nginx/sites-available/offermanager
```

Inserisci:
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Attiva:
```bash
sudo ln -s /etc/nginx/sites-available/offermanager /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Avvia App
```bash
source venv/bin/activate
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

---

## 🔄 Servizio Automatico (Systemd)

### Crea servizio
```bash
sudo nano /etc/systemd/system/offermanager.service
```

Contenuto:
```ini
[Unit]
Description=OfferManager Web App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/offermanager
Environment="PATH=/var/www/offermanager/venv/bin"
ExecStart=/var/www/offermanager/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

### Attiva servizio
```bash
sudo systemctl daemon-reload
sudo systemctl enable offermanager
sudo systemctl start offermanager
sudo systemctl status offermanager
```

---

## 🔐 HTTPS con SSL (Opzionale)

### Installa Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Configura dominio (se hai)
```bash
sudo certbot --nginx -d tuodominio.com
```

---

## 📊 Gestione

### Comandi Utili
```bash
# Status
sudo systemctl status offermanager

# Riavvia
sudo systemctl restart offermanager

# Stop
sudo systemctl stop offermanager

# Logs
sudo journalctl -u offermanager -f

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 💰 Costi AWS

**t2.micro (Free Tier)**:
- Primo anno: GRATIS (750 ore/mese)
- Dopo: ~$8/mese

**Ottimizzazioni**:
- Usa Reserved Instance: -40% costo
- Stop quando non usi: $0

---

## 🚀 Deploy Veloce con Script

Ho creato `deploy_aws.sh` che fa tutto automaticamente!

```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

---

## 📱 Accesso

Dopo il deploy, accessibile da:
- 💻 Computer: `http://IP-EC2`
- 📱 Smartphone: `http://IP-EC2`
- 🖥️ Tablet: `http://IP-EC2`

**Da tutta l'azienda!**

---

## ✅ Vantaggi Cloud

✅ Accessibile da ovunque  
✅ Non serve installare nulla sui PC  
✅ Aggiornamenti centralizzati  
✅ Backup automatici (snapshot EC2)  
✅ Costi bassi (~$8/mese o gratis primo anno)  
✅ Scalabile (se serve più potenza)  

---

## 🔧 Configurazione Post-Deploy

### Cambio Directory Offerte

Modifica `app.py` riga 17:
```python
generator = OfferGenerator(offers_directory="/mnt/efs/offerte")
```

Poi riavvia:
```bash
sudo systemctl restart offermanager
```

### Mount EFS (Storage condiviso AWS)

Per storage persistente:
```bash
sudo apt install -y nfs-common
sudo mkdir /mnt/efs
sudo mount -t nfs4 <EFS-DNS>:/ /mnt/efs
```

---

**Vuoi procedere con AWS?** Ti aiuto passo-passo! 🚀


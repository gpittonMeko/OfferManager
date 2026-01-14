# 🚀 Deploy Completo OfferManager CRM su AWS

## Setup AWS EC2 con la tua chiave

### 1. Verifica Chiave
La tua chiave è: `C:\Users\user\Documents\LLM_14.pem`

### 2. Crea Istanza EC2

**Console AWS**:
1. Vai su: https://console.aws.amazon.com/ec2
2. **Launch Instance**
3. Configurazione:
   ```
   Nome: OfferManager-CRM
   AMI: Ubuntu Server 22.04 LTS (Free tier)
   Instance: t2.micro
   Key pair: Usa LLM_14 (se già esiste) o creane una nuova
   Security Group:
      - SSH (22): Il tuo IP
      - HTTP (80): 0.0.0.0/0
      - Custom TCP (5000): 0.0.0.0/0 [per test]
   ```
4. **Launch!**

### 3. Connetti con la Tua Chiave

**Windows (PowerShell)**:
```powershell
# Trova l'IP pubblico dalla console AWS
$IP = "METTI_QUI_IP_PUBBLICO"

# Connetti
ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@$IP
```

**Se dice "permissions troppo aperte"**:
```powershell
icacls "C:\Users\user\Documents\LLM_14.pem" /inheritance:r
icacls "C:\Users\user\Documents\LLM_14.pem" /grant:r "%username%:R"
```

### 4. Carica File su EC2

**Opzione A: WinSCP (Grafico - Raccomandato)**
1. Scarica: https://winscp.net/
2. Nuovo sito:
   - Protocollo: SFTP
   - Host: IP_PUBBLICO_EC2
   - Username: ubuntu
   - Password: (vuoto)
   - Advanced → SSH → Authentication → Private key: `C:\Users\user\Documents\LLM_14.pem`
3. Connetti e trascina i file

**Opzione B: SCP da PowerShell**
```powershell
cd "C:\Users\user\OneDrive - ME.KO. Srl\Documenti\Cursor\OfferManager"

scp -i "C:\Users\user\Documents\LLM_14.pem" crm_app.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" offer_generator.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" pdf_parser.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" docx_handler.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" company_searcher.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" offer_numbering.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" demo_products.py ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" requirements_cloud.txt ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" deploy_aws.sh ubuntu@$IP:/home/ubuntu/
scp -i "C:\Users\user\Documents\LLM_14.pem" -r templates ubuntu@$IP:/home/ubuntu/
```

### 5. Deploy

**Nel terminale SSH**:
```bash
cd /home/ubuntu
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### 6. Accedi

Apri browser: `http://IP_PUBBLICO_EC2`

Login demo:
- Username: `marco`
- Password: `demo123`

---

## 🎯 Deploy Manuale Passo-Passo

### Connetti
```bash
ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@IP_EC2
```

### Installa Dipendenze
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

### Setup App
```bash
mkdir -p /home/ubuntu/offermanager
cd /home/ubuntu/offermanager

# Carica file (vedi sopra con WinSCP)

# Crea ambiente virtuale
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_cloud.txt
```

### Avvia App
```bash
python3 crm_app.py
```

Apri browser: `http://IP_EC2:5000`

---

## 🔄 Servizio Permanente

```bash
sudo nano /etc/systemd/system/offermanager.service
```

Inserisci:
```ini
[Unit]
Description=OfferManager CRM
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/offermanager
Environment="PATH=/home/ubuntu/offermanager/venv/bin"
ExecStart=/home/ubuntu/offermanager/venv/bin/gunicorn -w 2 -b 0.0.0.0:80 crm_app:app

[Install]
WantedBy=multi-user.target
```

Attiva:
```bash
sudo systemctl daemon-reload
sudo systemctl enable offermanager
sudo systemctl start offermanager
```

Ora accessibile su: `http://IP_EC2` (porta 80)

---

## 📊 Funzionalità Dashboard

### Per Ogni Commerciale:
✅ Inserimento offerte con categorie (MIR/UR/Unitree/Componenti/Servizi)
✅ Tracciamento valore totale
✅ Quantità prodotti
✅ Cliente e note
✅ Stati (bozza/inviata/accettata/rifiutata)
✅ Probabilità chiusura

### Analytics:
✅ Grafici per mese/settimana/giorno
✅ Visualizzazione per categoria
✅ Aggregato o separato
✅ Timeline valori
✅ Distribuzione categorie (pie chart)

### Team View:
✅ Performance tutti i commerciali
✅ Confronto valori
✅ Totale team

---

## 💰 Costi AWS

**t2.micro**: Gratis primo anno, poi ~€8/mese
**Storage**: ~€0.10/GB/mese
**Traffico**: Primo GB gratis

**Totale stimato**: €0 (anno 1), €10/mese (dopo)

---

## 🔐 Utenti Demo

| Username | Password | Ruolo |
|----------|----------|-------|
| admin | admin123 | Amministratore |
| marco | demo123 | Commerciale |
| laura | demo123 | Commerciale |
| giuseppe | demo123 | Commerciale |

Cambia password dopo primo accesso!

---

**Vuoi che proceda con il deploy?** Ti guido passo-passo! 🚀


# 📁 Istruzioni per Sincronizzare i File Offerte su AWS EC2

## ⚠️ Problema
Il server AWS EC2 è un sistema Linux remoto che **NON ha accesso diretto** al drive `K:\` del tuo PC locale Windows.

## ✅ Soluzioni

### Opzione 1: Sincronizzare i File (Raccomandato)

Usa lo script `deploy/copy_offers_to_ec2.py` per copiare i file dal drive K: al server AWS:

```powershell
# Dal PC locale Windows
cd "C:\Users\user\OneDrive - ME.KO. Srl\Documenti\Cursor\OfferManager"
python deploy/copy_offers_to_ec2.py
```

Questo script:
- Copia tutti i file da `K:\OFFERTE - K\OFFERTE 2025 - K` su EC2
- Li mette in `/home/ubuntu/offermanager/offerte_2025_backup`
- Puoi eseguirlo periodicamente per mantenere i file aggiornati

### Opzione 2: Montare il Drive K: su AWS (Avanzato)

Se il PC locale è raggiungibile dalla rete, puoi montare il drive K: sul server AWS:

```bash
# Sul server AWS EC2
sudo apt install cifs-utils
sudo mkdir -p /mnt/k

# Monta il drive K: (sostituisci con IP del tuo PC e credenziali)
sudo mount -t cifs //192.168.10.240/commerciale /mnt/k -o username=tuo_utente,password=tua_password,uid=1000,gid=1000
```

Poi configura le variabili d'ambiente:
```bash
export OFFERS_2025_FOLDER="/mnt/k/OFFERTE - K/OFFERTE 2025 - K"
export OFFERS_2026_FOLDER="/mnt/k/OFFERTE - K/OFFERTE 2026 - K"
```

### Opzione 3: Configurare Percorso Personalizzato

Se hai già copiato i file manualmente, configura le variabili d'ambiente sul server:

```bash
# SSH sul server AWS
ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@13.53.183.146

# Aggiungi al file ~/.bashrc
echo 'export OFFERS_2025_FOLDER="/percorso/alle/tue/offerte/2025"' >> ~/.bashrc
echo 'export OFFERS_2026_FOLDER="/percorso/alle/tue/offerte/2026"' >> ~/.bashrc

# Riavvia il servizio
sudo systemctl restart offermanager
```

## 🔍 Verifica

Dopo aver configurato, clicca sul pulsante **"📁 File Offerte"** su un'opportunità nel CRM. 
Se non trova i file, controlla i log di debug che mostrano quali cartelle sono state verificate.

## 📝 Note

- Il pulsante "📁 File Offerte" si trova nella tabella delle opportunità, nella colonna "Azioni"
- La ricerca cerca automaticamente in vari percorsi comuni
- I log di debug mostrano esattamente quali cartelle sono state verificate

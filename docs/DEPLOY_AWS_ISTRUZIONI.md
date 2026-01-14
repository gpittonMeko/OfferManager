# Istruzioni Deploy su AWS EC2

## File da Deployare

1. `crm_app_completo.py` - Endpoint pulizia nomi e supporto limit
2. `sync_offers_2025_2026.py` - Script sincronizzazione offerte
3. `pulisci_nomi_account.py` - Script pulizia nomi account
4. `templates/app_mekocrm_completo.html` - Mappa 3D e modifiche UI

## Metodo 1: Script PowerShell (Consigliato)

Esegui:
```powershell
.\deploy_to_aws.ps1
```

Lo script ti chiederà:
- IP della macchina EC2
- Percorso della chiave .pem

Poi caricherà automaticamente i file e riavvierà il servizio.

## Metodo 2: Comandi Manuali

### 1. Carica i file via SCP:

```bash
scp -i "percorso/chiave.pem" crm_app_completo.py ubuntu@IP_EC2:/home/ubuntu/offermanager/
scp -i "percorso/chiave.pem" sync_offers_2025_2026.py ubuntu@IP_EC2:/home/ubuntu/offermanager/
scp -i "percorso/chiave.pem" pulisci_nomi_account.py ubuntu@IP_EC2:/home/ubuntu/offermanager/
scp -i "percorso/chiave.pem" templates/app_mekocrm_completo.html ubuntu@IP_EC2:/home/ubuntu/offermanager/templates/
```

### 2. Connettiti via SSH e riavvia:

```bash
ssh -i "percorso/chiave.pem" ubuntu@IP_EC2
sudo systemctl restart offermanager
sudo systemctl status offermanager
```

## Metodo 3: Esegui Pulizia Nomi Account

Dopo il deploy, connettiti via SSH ed esegui:

```bash
ssh -i "percorso/chiave.pem" ubuntu@IP_EC2
cd /home/ubuntu/offermanager
python3 pulisci_nomi_account.py
```

Oppure usa il pulsante "🧹 Pulisci Nomi Account" nella pagina Mappa del CRM.

## Verifica

1. Apri il browser: `http://IP_EC2`
2. Vai su "🗺️ Mappa Contatti" - dovresti vedere la mappa 3D
3. Vai su "Opportunità" - dovresti vedere il pulsante "🔄 Sincronizza Offerte"
4. Verifica che Accounts e Leads mostrino 200 record

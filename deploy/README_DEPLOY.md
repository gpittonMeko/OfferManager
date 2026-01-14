# 🚀 GUIDA DEPLOY E SVILUPPO

## 📋 STRUTTURA REPOSITORY

```
OfferManager/
├── crm_app_completo.py          # ⭐ APP PRINCIPALE (per AWS Cloud)
├── sync_offers_from_folder.py   # Script sincronizzazione offerte
├── pulisci_nomi_account.py      # Script pulizia account
│
├── deploy/                       # Script per deploy su AWS
│   ├── riavvia_server_semplice.bat  # ⭐ RIAVVIA SERVER CLOUD (usa questo!)
│   ├── deploy_automatico.ps1
│   └── deploy_to_aws.ps1
│
├── migrations/                   # Script migrazione database
├── scripts/                      # Script utilità varie
├── utils/                        # Utility e helper
├── docs/                         # Documentazione
│
├── templates/                    # Template HTML
├── static/                       # File statici
└── instance/                     # Database locale (non committare!)
```

## 🌐 DEPLOY SU AWS CLOUD

### Riavvio Rapido Server
**Doppio click su:** `deploy/riavvia_server_semplice.bat`

Questo script:
1. Carica `crm_app_completo.py` sulla macchina EC2
2. Riavvia il servizio `offermanager`
3. Usa credenziali preconfigurate:
   - IP: `13.53.183.146`
   - Chiave: `C:\Users\user\Documents\LLM_14.pem`

### Deploy Completo
```powershell
cd deploy
.\deploy_automatico.ps1
```

## 💻 SVILUPPO LOCALE

### Avvio Server Locale
```bash
python crm_app_completo.py
```

Il server si avvia su: `http://localhost:8000`

**ATTENZIONE:** 
- Il file `crm_app_completo.py` è configurato per AWS Cloud
- Per sviluppo locale, modifica la porta se necessario
- Il database locale è in `instance/mekocrm.db`

### Database Locale vs Cloud
- **Locale**: `instance/mekocrm.db` (SQLite)
- **Cloud**: Database su EC2 (SQLite o altro)

## 📝 FILE IMPORTANTI

### File Principali (NON SPOSTARE)
- `crm_app_completo.py` - Applicazione principale Flask
- `sync_offers_from_folder.py` - Sincronizzazione offerte
- `pulisci_nomi_account.py` - Pulizia nomi account
- `templates/app_mekocrm_completo.html` - Template principale

### Script Deploy (in `deploy/`)
- `riavvia_server_semplice.bat` - ⭐ **USA QUESTO per riavviare**
- `deploy_automatico.ps1` - Deploy completo
- `deploy_to_aws.ps1` - Deploy manuale

## ⚠️ REGOLE IMPORTANTI

1. **NON modificare** file in `deploy/` senza motivo
2. **NON committare** file in `instance/` (database locale)
3. **SEMPRE testare** localmente prima di fare deploy
4. **SEMPRE usare** `deploy/riavvia_server_semplice.bat` per riavviare il server cloud

## 🔧 TROUBLESHOOTING

### Server non si riavvia
1. Verifica che la chiave `.pem` esista: `C:\Users\user\Documents\LLM_14.pem`
2. Verifica connessione SSH: `ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@13.53.183.146`
3. Controlla stato servizio: `ssh ... "sudo systemctl status offermanager"`

### File non si carica
1. Verifica che `crm_app_completo.py` esista nella root
2. Verifica permessi chiave `.pem` (deve essere leggibile)
3. Controlla log SSH per errori

## 📞 SUPPORTO

Per problemi:
1. Controlla `docs/` per documentazione specifica
2. Verifica log su EC2: `ssh ... "sudo journalctl -u offermanager -n 50"`

# Sincronizzazione Portali CRM

## Portali Sincronizzati

1. **Portale Universal Robots** (`/api/ur/sync`)
   - Sincronizza opportunità e leads dal portale UR
   - Eseguito tramite Playwright

2. **Portale Offerte** (`/api/offers/sync`)
   - Sincronizza offerte dalle cartelle Windows
   - Crea/aggiorna opportunità basate sui file PDF/DOCX

3. **Portale Wix Studio** (`/api/wix/sync`)
   - Importa contatti dal form Wix come opportunità
   - Crea attività "Chiamare" per ogni contatto
   - Imposta stato "fredda_speranza" (5% probabilità)

## Sincronizzazione Automatica Giornaliera

La sincronizzazione viene eseguita automaticamente ogni giorno alle **2:00 AM** tramite cron job.

### Configurazione

```bash
cd /home/ubuntu/offermanager
bash scripts/setup_daily_sync.sh
```

### Verifica

```bash
# Verifica cron job
crontab -l

# Test manuale
python3 scripts/sync_all_portals.py

# Visualizza log
tail -f logs/daily_sync.log
```

## Sincronizzazione Manuale

### Tutti i portali insieme
```bash
POST /api/sync/all
```

### Singoli portali
```bash
POST /api/ur/sync      # Portale UR
POST /api/offers/sync  # Offerte
POST /api/wix/sync     # Wix Studio
```

## Importazione Wix Studio

### Preparazione dati

1. Esporta i dati dal form Wix Studio
2. Crea file JSON con formato:
```json
[
  {
    "name": "Nome Cognome",
    "email": "email@example.com",
    "phone": "+39 123 456 7890",
    "product": "Prodotto di interesse",
    "message": "Messaggio del cliente",
    "created_date": "2026-01-13T12:00:00Z"
  }
]
```

3. Salva in `data/wix_submissions.json`

### Importazione

```bash
python3 utils/wix_forms_import.py data/wix_submissions.json
```

## Note

- Le opportunità da Wix vengono create con:
  - Stage: "Qualification"
  - Heat Level: "fredda_speranza" (5% probabilità)
  - Attività: "Chiamare cliente"
  - Supplier Category: determinata automaticamente dal prodotto

- Le opportunità duplicate (stessa email + stesso prodotto) vengono saltate

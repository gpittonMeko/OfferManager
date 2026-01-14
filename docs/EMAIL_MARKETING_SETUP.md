# 📧 Email Marketing Setup - ME.KO. CRM

## Configurazione Completa Sistema Email Marketing

Questo documento descrive come configurare e utilizzare il sistema di Email Marketing integrato nel CRM, simile a Mailchimp ma integrato nel tuo CRM.

---

## 🚀 Configurazione Iniziale

### 1. Variabili d'Ambiente

Crea un file `.env` nella root del progetto con le seguenti variabili:

```env
# Mailgun Configuration
MAILGUN_API_KEY=your-mailgun-api-key-here
MAILGUN_DOMAIN=your-domain.mailgun.org
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
MAILGUN_FROM_NAME=ME.KO. Srl
MAILGUN_API_REGION=eu
# Options: eu or us (default: eu)
```

**Dove trovare le credenziali Mailgun:**
1. Accedi al tuo account Mailgun (https://app.mailgun.com)
2. Vai su **Settings** → **API Keys**
3. Copia la **Private API key**
4. Il dominio lo trovi in **Sending** → **Domains**

### 2. Caricamento Variabili d'Ambiente

Per caricare le variabili d'ambiente, puoi:

**Opzione A - Windows PowerShell:**
```powershell
$env:MAILGUN_API_KEY="your-key"
$env:MAILGUN_DOMAIN="your-domain.mailgun.org"
$env:MAILGUN_FROM_EMAIL="noreply@yourdomain.com"
$env:MAILGUN_FROM_NAME="ME.KO. Srl"
$env:MAILGUN_API_REGION="eu"
```

**Opzione B - File .env (richiede python-dotenv):**
```bash
pip install python-dotenv
```

Poi aggiungi all'inizio di `crm_app_completo.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📦 Struttura del Sistema

### Modelli Database

Il sistema include i seguenti modelli:

1. **EmailList** - Liste di destinatari
2. **EmailListSubscription** - Iscrizioni alle liste
3. **EmailTemplate** - Template email HTML
4. **EmailCampaign** - Campagne email
5. **EmailCampaignSend** - Singoli invii tracciati

### API Endpoints Disponibili

#### Liste Email
- `GET /api/email/lists` - Lista tutte le liste
- `POST /api/email/lists` - Crea nuova lista
- `GET /api/email/lists/<id>` - Dettagli lista
- `PUT /api/email/lists/<id>` - Aggiorna lista
- `DELETE /api/email/lists/<id>` - Elimina lista
- `POST /api/email/lists/<id>/subscribe` - Iscrivi contatti/leads

#### Template Email
- `GET /api/email/templates` - Lista template
- `POST /api/email/templates` - Crea template
- `GET /api/email/templates/<id>` - Dettagli template
- `PUT /api/email/templates/<id>` - Aggiorna template
- `DELETE /api/email/templates/<id>` - Elimina template
- `POST /api/email/templates/init-defaults` - Carica template predefiniti

#### Campagne Email
- `GET /api/email/campaigns` - Lista campagne
- `POST /api/email/campaigns` - Crea campagna
- `GET /api/email/campaigns/<id>` - Dettagli campagna
- `PUT /api/email/campaigns/<id>` - Aggiorna campagna
- `DELETE /api/email/campaigns/<id>` - Elimina campagna
- `POST /api/email/campaigns/<id>/send` - Invia campagna

#### Test Email
- `POST /api/email/test` - Invia email di test

---

## 🎨 Template Email Predefiniti

Il sistema include 3 template predefiniti:

1. **Newsletter** - Per newsletter periodiche
2. **Promotional** - Per offerte promozionali
3. **Transactional** - Per email transazionali

### Caricare Template Predefiniti

Dopo aver configurato Mailgun, esegui questa chiamata API:

```javascript
fetch('/api/email/templates/init-defaults', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})
.then(res => res.json())
.then(data => console.log('Template creati:', data));
```

---

## 📝 Utilizzo Base

### 1. Creare una Lista Email

```javascript
const response = await fetch('/api/email/lists', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Newsletter Clienti',
        description: 'Lista clienti per newsletter mensile'
    })
});
```

### 2. Iscrivi Contatti a una Lista

```javascript
await fetch('/api/email/lists/1/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        contact_ids: [1, 2, 3],  // IDs contatti dal CRM
        lead_ids: [4, 5],         // IDs leads dal CRM
        emails: [                 // Email manuali
            { email: 'test@example.com', name: 'Test User' }
        ]
    })
});
```

### 3. Creare una Campagna

```javascript
await fetch('/api/email/campaigns', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Newsletter Gennaio 2025',
        subject: 'Novità dal mondo della robotica',
        html_content: '<html>...contenuto HTML...</html>',
        list_id: 1,
        template_id: 1  // Opzionale
    })
});
```

### 4. Inviare una Campagna

```javascript
await fetch('/api/email/campaigns/1/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
});
```

### 5. Test Email

```javascript
await fetch('/api/email/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        to_email: 'tuo-email@example.com',
        subject: 'Test Email',
        html_content: '<p>Ciao, questa è una email di test!</p>'
    })
});
```

---

## 🎯 Personalizzazione Template

I template supportano variabili personalizzate:

- `%nome%` o `%nome_completo%` - Nome completo destinatario
- `%first_name%` - Nome
- `%last_name%` - Cognome

Puoi aggiungere variabili personalizzate nella campagna usando `%variabile%`.

---

## 📊 Statistiche Campagne

Ogni campagna traccia:
- **total_recipients** - Totale destinatari
- **total_sent** - Email inviate
- **total_delivered** - Email consegnate
- **total_opened** - Email aperte
- **total_clicked** - Click su link
- **total_bounced** - Email rimbalzate
- **total_unsubscribed** - Disiscrizioni

---

## 🔧 Inizializzazione Database

Il sistema crea automaticamente le tabelle quando esegui:

```python
python crm_app_completo.py
```

Se necessario, puoi forzare la creazione:

```python
from crm_app_completo import db, app
with app.app_context():
    db.create_all()
```

---

## 🐛 Troubleshooting

### Errore "MAILGUN_API_KEY non configurato"
- Verifica che le variabili d'ambiente siano impostate correttamente
- Riavvia l'applicazione dopo aver impostato le variabili

### Email non vengono inviate
- Verifica che il dominio Mailgun sia verificato
- Controlla i log Mailgun per errori
- Verifica che gli indirizzi email siano validi

### Template non si caricano
- Verifica che la cartella `templates/email/` esista
- Controlla i permessi dei file

---

## 📚 File Creati

- `mailgun_service.py` - Servizio Mailgun
- `email_template_loader.py` - Caricatore template
- `templates/email/*.html` - Template email HTML
- Modelli database aggiunti a `crm_app_completo.py`
- API routes aggiunte a `crm_app_completo.py`

---

## 🎉 Prossimi Passi

1. ✅ Configura le variabili d'ambiente Mailgun
2. ✅ Avvia l'applicazione
3. ✅ Carica i template predefiniti (`/api/email/templates/init-defaults`)
4. ✅ Crea la tua prima lista email
5. ✅ Iscrivi contatti/leads alla lista
6. ✅ Crea e invia la tua prima campagna!

---

**Supporto:** Per problemi o domande, consulta la documentazione Mailgun: https://documentation.mailgun.com/










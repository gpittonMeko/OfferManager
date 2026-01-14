# 📧 Guida Rapida Email Marketing - ME.KO. CRM

## ✅ Sistema Configurato e Pronto!

Il sistema di Email Marketing è completamente configurato e pronto all'uso.

---

## 🚀 COME INIZIARE

### 1. Accedi al CRM
```
http://13.53.183.146:8000
oppure
http://crm.infomekosrl.it:8000
```

### 2. Vai su Email Marketing
Clicca su **"📧 Email Marketing"** nel menu laterale sinistro.

### 3. Carica i Template Predefiniti

Apri la console del browser (premi **F12**) e incolla:

```javascript
fetch('/api/email/templates/init-defaults', {method: 'POST'})
  .then(r => r.json())
  .then(data => {
    console.log('✅ Template caricati:', data);
    alert('Template caricati con successo!');
  });
```

Questo caricherà 3 template predefiniti:
- **Newsletter** - Per newsletter periodiche
- **Promotional** - Per offerte promozionali  
- **Transactional** - Per email transazionali

---

## 📋 CREARE UNA LISTA EMAIL

### Metodo 1: Via Interfaccia Web (quando sarà disponibile)

### Metodo 2: Via API (Console Browser)

```javascript
// Crea una nuova lista
fetch('/api/email/lists', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Clienti Attivi',
    description: 'Lista clienti per newsletter mensile'
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Lista creata:', data);
  alert('Lista creata con ID: ' + data.list_id);
});
```

---

## 👥 ISCRIVI CONTATTI A UNA LISTA

```javascript
// Iscrivi contatti/leads alla lista (ID lista = 1)
fetch('/api/email/lists/1/subscribe', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    contact_ids: [1, 2, 3],  // IDs contatti dal CRM
    lead_ids: [4, 5],         // IDs leads dal CRM
    emails: [                 // Email manuali
      {email: 'test@example.com', name: 'Test User'}
    ]
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Iscritti:', data);
  alert('Iscritti ' + data.count + ' contatti!');
});
```

---

## 📧 CREARE UNA CAMPAGNA EMAIL

```javascript
// Crea una nuova campagna
fetch('/api/email/campaigns', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Newsletter Gennaio 2025',
    subject: 'Novità dal mondo della robotica',
    html_content: '<html><body><h1>Ciao %nome%</h1><p>Contenuto newsletter...</p></body></html>',
    list_id: 1,  // ID della lista creata
    template_id: 1  // Opzionale: ID template
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Campagna creata:', data);
  alert('Campagna creata con ID: ' + data.campaign_id);
});
```

---

## ✉️ INVIARE UNA CAMPAGNA

```javascript
// Invia campagna (ID campagna = 1)
fetch('/api/email/campaigns/1/send', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => {
  console.log('✅ Campagna inviata:', data);
  alert('Inviate ' + data.stats.sent + ' email su ' + data.stats.total);
});
```

---

## 🧪 TEST EMAIL

```javascript
// Invia email di test
fetch('/api/email/test', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    to_email: 'tua-email@example.com',
    subject: 'Test Email ME.KO.',
    html_content: '<html><body><h1>Test</h1><p>Questa è un\'email di test!</p></body></html>'
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Email test:', data);
  alert(data.message || data.error);
});
```

---

## 📊 STATISTICHE CAMPAGNE

```javascript
// Vedi statistiche campagna
fetch('/api/email/campaigns/1')
.then(r => r.json())
.then(data => {
  console.log('Statistiche:', data.campaign);
  console.log('Inviate:', data.campaign.total_sent);
  console.log('Aperte:', data.campaign.total_opened);
  console.log('Click:', data.campaign.total_clicked);
});
```

---

## 🎨 VARIABILI PERSONALIZZATE

Nei template HTML puoi usare queste variabili:
- `%nome%` o `%nome_completo%` - Nome completo destinatario
- `%first_name%` - Nome
- `%last_name%` - Cognome

Esempio:
```html
<h1>Ciao %nome%</h1>
<p>Gentile %first_name%,</p>
```

---

## ⚙️ CONFIGURAZIONE ATTUALE

- **Dominio Mailgun**: `infomekosrl.it`
- **Email Mittente**: `noreply@infomekosrl.it`
- **Nome Mittente**: `ME.KO. Srl`
- **Regione**: `EU`
- **DNS**: Configurato (MX, SPF, DKIM)

---

## 🔧 API DISPONIBILI

### Liste Email
- `GET /api/email/lists` - Lista tutte le liste
- `POST /api/email/lists` - Crea nuova lista
- `GET /api/email/lists/<id>` - Dettagli lista
- `PUT /api/email/lists/<id>` - Aggiorna lista
- `POST /api/email/lists/<id>/subscribe` - Iscrivi contatti

### Template
- `GET /api/email/templates` - Lista template
- `POST /api/email/templates` - Crea template
- `POST /api/email/templates/init-defaults` - Carica template predefiniti

### Campagne
- `GET /api/email/campaigns` - Lista campagne
- `POST /api/email/campaigns` - Crea campagna
- `POST /api/email/campaigns/<id>/send` - Invia campagna

### Test
- `POST /api/email/test` - Invia email di test

---

## ❓ PROBLEMI COMUNI

**Email non vengono inviate**
- Verifica che il dominio sia verificato su Mailgun
- Controlla i log: `sudo journalctl -u offermanager -f`

**Errore "MAILGUN_API_KEY non configurato"**
- Verifica configurazione: `sudo systemctl show offermanager | grep MAILGUN`

**Template non si caricano**
- Verifica directory: `ls -la /home/ubuntu/offermanager/templates/email/`

---

**🎉 Buon Email Marketing!**








# 🎯 Guida Rapida: Cosa Fare Ora su Mailgun

## 📍 DOVE ANDARE NEL DASHBOARD MAILGUN

### STEP 1: Vai nella Sezione "Domains"

Nel menu laterale sinistro, cerca e clicca su:
```
📧 Send → Domains
```

OPPURE

Nel menu principale in alto, clicca su:
```
Send → (poi cerca) Domains
```

### STEP 2: Cerca il Dominio `infomekosrl.it`

1. Nella pagina "Domains" vedrai una lista di domini
2. Cerca `infomekosrl.it` nella lista
3. **Se NON lo vedi**, devi aggiungerlo:
   - Clicca su **"Add New Domain"** o **"Add Domain"**
   - Inserisci: `infomekosrl.it`
   - Seleziona regione: **EU** (Europa)
   - Clicca su **"Add Domain"**

### STEP 3: Verifica il Dominio

1. Clicca sul dominio `infomekosrl.it` (o sul pulsante "Verify" accanto)
2. Vedrai una schermata con:
   - Stato del dominio (Verified/Unverified)
   - Lista dei record DNS richiesti
   - I record da configurare nel DNS

### STEP 4: Controlla i Record DNS Richiesti

Mailgun ti mostrerà qualcosa tipo:

```
Required DNS Records:

1. TXT Record
   Name: infomekosrl.it
   Value: "v=spf1 include:mailgun.org ~all"

2. MX Records
   Name: infomekosrl.it
   Value: mxa.mailgun.org (priority 10)
   Value: mxb.mailgun.org (priority 10)

3. CNAME Record
   Name: email.infomekosrl.it
   Value: mailgun.org

4. TXT Record (DKIM)
   Name: [qualcosa tipo] mailo._domainkey.infomekosrl.it
   Value: [chiave lunga copiata da Mailgun]
```

### STEP 5: Confronta con i Tuoi Record DNS

1. **Copia i record DKIM** mostrati da Mailgun
2. Confrontali con quelli che hai nel pannello Register.it
3. **Se mancano o sono diversi**, aggiungili/modificali

### STEP 6: Clicca "Verify DNS Settings"

1. Dopo aver aggiunto/modificato i record DNS
2. Aspetta 15-30 minuti per la propagazione
3. Torna su Mailgun
4. Clicca il pulsante **"Verify DNS Settings"** o **"Verify"**
5. Se tutto è corretto, vedrai ✅ **"Verified"** o **"Active"**

## 🔍 ROUTA ALTERNATIVA SE NON TROVI "DOMAINS"

1. Clicca su **"Send"** nel menu principale
2. Poi cerca nella lista:
   - **"Sending"** 
   - **"Domains"**
   - **"Domain Settings"**

## ⚠️ COSA FARE SE IL DOMINIO NON C'È

Se `infomekosrl.it` non appare nella lista:

1. Clicca su **"Add New Domain"** (pulsante in alto a destra)
2. Inserisci: `infomekosrl.it`
3. Seleziona regione: **EU** (perché sei in Europa)
4. Clicca **"Add Domain"**
5. Mailgun ti mostrerà i record DNS da configurare

## 📝 CHECKLIST RAPIDA

- [ ] Aperto "Send" → "Domains"
- [ ] Trovato/aggiunto `infomekosrl.it`
- [ ] Copiato i record DKIM mostrati da Mailgun
- [ ] Confrontato con record DNS su Register.it
- [ ] Aggiunto/modificato record DNS mancanti
- [ ] Atteso 15-30 minuti
- [ ] Cliccato "Verify DNS Settings" su Mailgun
- [ ] Verificato che risulti "Verified" ✅

## 🎯 COSA VERIFICARE

Nel pannello del dominio su Mailgun vedrai:
- **State**: deve essere "Active" o "Verified" ✅
- **Sending**: deve essere abilitato
- **Receiving**: opzionale (per ricevere email)

Se vedi errori o avvisi rossi, clicca su di essi per vedere i dettagli.








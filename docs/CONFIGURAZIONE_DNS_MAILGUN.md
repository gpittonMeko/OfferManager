# Configurazione DNS per Mailgun - infomekosrl.it

## 📋 Record DNS Attuali

Dal tuo pannello Register.it vedo che hai già configurato:

✅ **MX Records** (già presenti):
- `infomekosrl.it.` MX `10 mxa.mailgun.org.`
- `infomekosrl.it.` MX `10 mxb.mailgun.org.`

✅ **SPF Record** (già presente):
- `infomekosrl.it.` TXT `"v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all"`

✅ **CNAME per Tracking**:
- `email.infomekosrl.it.` CNAME `mailgun.org.`

⚠️ **DKIM Records** (DA VERIFICARE):
- `k1._domainkey.infomekosrl.it.` TXT (chiave DKIM attuale)

## ⚠️ PROBLEMA: Record MX Duplicato

Vedo che hai **due record MX** per `infomekosrl.it`:
1. `mail.register.it.` (vecchio - da rimuovere se vuoi usare solo Mailgun)
2. `mxa.mailgun.org.` e `mxb.mailgun.org.` (Mailgun)

### Soluzione:

**OPZIONE 1: Usa solo Mailgun (consigliato)**
1. **RIMUOVI** il record MX vecchio:
   - Elimina: `infomekosrl.it.` MX `10 mail.register.it.`
   
2. **Mantieni solo i record Mailgun**:
   - `infomekosrl.it.` MX `10 mxa.mailgun.org.`
   - `infomekosrl.it.` MX `10 mxb.mailgun.org.`

**OPZIONE 2: Mantieni entrambi (non consigliato)**
- Aumenta la priorità del record Mailgun (es. priority 5)
- Lascia `mail.register.it.` con priority 10

## 🔍 Verifica su Mailgun Dashboard

Devi verificare sul dashboard Mailgun (https://app.mailgun.com):

1. **Vai su "Sending" → "Domains"**
2. **Clicca su `infomekosrl.it`**
3. **Controlla lo stato di verifica**:
   - ✅ Se è "Verified" → tutto ok
   - ❌ Se è "Unverified" → clicca su "Verify DNS Settings"

4. **Controlla i record DKIM specifici**:
   - Mailgun ti mostrerà i record TXT DKIM specifici da aggiungere
   - Tipo: `mailo._domainkey.infomekosrl.it.` o simile
   - Sostituisci i record DKIM attuali con quelli di Mailgun

## 📝 Record da Aggiungere/Modificare

### 1. Record DKIM (da Mailgun Dashboard)
```
Nome: mailo._domainkey.infomekosrl.it.
Tipo: TXT
Valore: [copiato da Mailgun Dashboard]
TTL: 900
```

### 2. Verifica che SPF includa Mailgun (già presente ✅)
```
Nome: infomekosrl.it.
Tipo: TXT
Valore: "v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all"
```

### 3. Verifica MX Records (già presenti ✅)
```
Nome: infomekosrl.it.
Tipo: MX
Valore: 10 mxa.mailgun.org.
```

```
Nome: infomekosrl.it.
Tipo: MX
Valore: 10 mxb.mailgun.org.
```

## 🎯 Passi da Seguire

1. **Vai su Mailgun Dashboard**: https://app.mailgun.com/app/sending/domains
2. **Seleziona `infomekosrl.it`**
3. **Clicca su "Verify DNS Settings"** se non è verificato
4. **Copia i record DKIM** mostrati da Mailgun
5. **Aggiungi/modifica i record DKIM** nel pannello Register.it
6. **Rimuovi il record MX vecchio** `mail.register.it.` se vuoi usare solo Mailgun
7. **Attendi la propagazione DNS** (15-30 minuti)
8. **Ritorna su Mailgun e clicca "Verify"**

## ⚠️ IMPORTANTE

- Non eliminare tutti i record DNS insieme
- Modifica un record alla volta
- Attendi 15-30 minuti dopo ogni modifica per la propagazione
- Verifica sempre su Mailgun che il dominio risulti "Verified"

## 🔧 Se l'errore "Forbidden" persiste

Dopo aver verificato il dominio:
1. Controlla che l'API key sia attiva su Mailgun
2. Verifica che il dominio sia nello stato "Active"
3. Controlla i log su Mailgun per vedere errori specifici








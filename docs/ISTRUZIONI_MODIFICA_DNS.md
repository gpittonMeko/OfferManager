# 🔧 Istruzioni Modifica DNS per Mailgun

## ❌ PROBLEMA IDENTIFICATO

Hai **record MX duplicati** che possono causare problemi:

1. ✅ **MX Mailgun** (CORRETTI - da mantenere):
   - `infomekosrl.it.` MX `10 mxa.mailgun.org.`
   - `infomekosrl.it.` MX `10 mxb.mailgun.org.`

2. ❌ **MX Vecchio** (DA RIMUOVERE):
   - `infomekosrl.it.` MX `10 mail.register.it.`

## ✅ COSA FARE NEL PANNELLO REGISTER.IT

### STEP 1: Rimuovi il Record MX Vecchio

1. Vai nella sezione **"Zona DNS (gestione avanzata)"**
2. Trova la riga con:
   ```
   Nome: infomekosrl.it.
   TTL: 900
   Tipo: MX
   Valore: 10 mail.register.it.
   ```
3. **ELIMINA** questa riga (clicca su elimina/cestino)
4. **CONFERMA** l'eliminazione

### STEP 2: Verifica che questi record siano presenti

Assicurati che questi record siano presenti (dovrebbero già esserci):

#### Record MX (per Mailgun):
```
Nome: infomekosrl.it.
Tipo: MX
Valore: 10 mxa.mailgun.org.
TTL: 900
```

```
Nome: infomekosrl.it.
Tipo: MX
Valore: 10 mxb.mailgun.org.
TTL: 900
```

#### Record SPF (dovrebbe già essere presente):
```
Nome: infomekosrl.it.
Tipo: TXT
Valore: "v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all"
TTL: 900
```

#### Record CNAME per Tracking (dovrebbe già essere presente):
```
Nome: email.infomekosrl.it.
Tipo: CNAME
Valore: mailgun.org.
TTL: 900
```

### STEP 3: Verifica su Mailgun Dashboard

1. Vai su: https://app.mailgun.com/app/sending/domains
2. Clicca sul dominio `infomekosrl.it`
3. Clicca su **"Verify DNS Settings"** o **"Verify"**
4. Mailgun ti mostrerà se ci sono problemi

### STEP 4: Verifica Record DKIM

Mailgun potrebbe richiedere record DKIM specifici. Se non sono verificati:

1. Nel dashboard Mailgun, vai su **"Sending" → "Domains" → `infomekosrl.it`**
2. Cerca la sezione **"DNS Records"** o **"DKIM Keys"**
3. Copia il record DKIM mostrato (solitamente tipo `mailo._domainkey.infomekosrl.it.`)
4. Aggiungilo/modificalo nel pannello Register.it

## ⏱️ TEMPI DI PROPAGAZIONE

- Dopo ogni modifica DNS, attendi **15-30 minuti**
- Poi verifica su Mailgun che il dominio risulti **"Verified"** ✅

## 🎯 RIEPILOGO AZIONI IMMEDIATE

1. ✅ **Rimuovi** il record MX `mail.register.it.`
2. ✅ **Verifica** che i record MX Mailgun siano presenti
3. ✅ **Attendi** 15-30 minuti
4. ✅ **Verifica** sul dashboard Mailgun che il dominio sia verificato
5. ✅ **Testa** l'invio email

## ⚠️ ATTENZIONE

- Non eliminare tutti i record insieme
- Modifica un record alla volta
- Salva sempre dopo ogni modifica








# 🔧 Modifiche DNS Richieste per Mailgun

## 📋 Record Richiesti da Mailgun (visti nel dashboard)

### ✅ Sending Records (per inviare email)

1. **TXT Record - DKIM**:
   ```
   Nome: s1._domainkey.infomekosrl.it.
   Tipo: TXT
   Valore: k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCyv+MPiEj5VfoD1q5AthXKSf0z2aL6n0Zh/wMxZi0EuP7mSFGXcTxx2nc0iTWkFoL67oGKu+GKx86t+L7GT8ctuTMldcURKKOYdFCCdgeDpnSv+++xaRQCo3G6k8IjgsEPRdPyoSDybo0MonISGg8FEm/gEdZ5rB6SZMw4W33HTwIDAQAB
   TTL: 900
   ```

2. **TXT Record - SPF**:
   ```
   Nome: infomekosrl.it.
   Tipo: TXT
   Valore: v=spf1 include:mailgun.org ~all
   TTL: 900
   ```

### ✅ Receiving Records (per ricevere email - MX)

1. **MX Record 1**:
   ```
   Nome: infomekosrl.it.
   Tipo: MX
   Valore: mxa.eu.mailgun.org.
   Priorità: 10
   TTL: 900
   ```

2. **MX Record 2**:
   ```
   Nome: infomekosrl.it.
   Tipo: MX
   Valore: mxb.eu.mailgun.org.
   Priorità: 10
   TTL: 900
   ```

### ✅ Tracking Records (per tracciare aperture e click)

1. **CNAME Record**:
   ```
   Nome: email.infomekosrl.it.
   Tipo: CNAME
   Valore: eu.mailgun.org.
   TTL: 900
   ```

---

## 🔍 CONFRONTO CON I TUOI RECORD ATUALI

### ❌ DA AGGIUNGERE:

1. **TXT Record DKIM** - `s1._domainkey.infomekosrl.it.`
   - ❌ **NON PRESENTE** - da aggiungere

### ⚠️ DA MODIFICARE:

1. **MX Records** - Devi cambiare i server Mailgun:
   - ❌ Attuale: `mxa.mailgun.org.` e `mxb.mailgun.org.`
   - ✅ Richiesto: `mxa.eu.mailgun.org.` e `mxb.eu.mailgun.org.`
   - **Nota**: Mancano `.eu` nei nomi server!

2. **CNAME Tracking** - Da modificare:
   - ❌ Attuale: `email.infomekosrl.it.` → `mailgun.org.`
   - ✅ Richiesto: `email.infomekosrl.it.` → `eu.mailgun.org.`
   - **Nota**: Deve puntare a `eu.mailgun.org.` (con `.eu`)!

### ✅ GIÀ CORRETTI:

1. **SPF Record** - `infomekosrl.it.` con `v=spf1 include:mailgun.org ~all`
   - ✅ Già presente e corretto

### ❌ DA RIMUOVERE:

1. **MX Record Vecchio**:
   - ❌ `infomekosrl.it.` MX `10 mail.register.it.` → **ELIMINA**

---

## 📝 ISTRUZIONI PASSO PASSO

### STEP 1: Aggiungi Record DKIM

Nel pannello Register.it:

1. Vai in **"Zona DNS (gestione avanzata)"**
2. Clicca **"Aggiungi Record"** o **"New Record"**
3. Compila:
   - **Nome**: `s1._domainkey.infomekosrl.it.`
   - **Tipo**: `TXT`
   - **Valore**: `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCyv+MPiEj5VfoD1q5AthXKSf0z2aL6n0Zh/wMxZi0EuP7mSFGXcTxx2nc0iTWkFoL67oGKu+GKx86t+L7GT8ctuTMldcURKKOYdFCCdgeDpnSv+++xaRQCo3G6k8IjgsEPRdPyoSDybo0MonISGg8FEm/gEdZ5rB6SZMw4W33HTwIDAQAB`
   - **TTL**: `900`
4. **Salva**

### STEP 2: Modifica Record MX

Trova i due record MX che puntano a Mailgun:

1. **Record MX 1**:
   - Trova: `infomekosrl.it.` MX `10 mxa.mailgun.org.`
   - **Modifica** il valore in: `mxa.eu.mailgun.org.`
   - Salva

2. **Record MX 2**:
   - Trova: `infomekosrl.it.` MX `10 mxb.mailgun.org.`
   - **Modifica** il valore in: `mxb.eu.mailgun.org.`
   - Salva

### STEP 3: Rimuovi Record MX Vecchio

1. Trova: `infomekosrl.it.` MX `10 mail.register.it.`
2. **Elimina** questo record
3. Conferma eliminazione

### STEP 4: Modifica CNAME Tracking

1. Trova: `email.infomekosrl.it.` CNAME `mailgun.org.`
2. **Modifica** il valore in: `eu.mailgun.org.`
3. Salva

---

## ⏱️ TEMPI

- Dopo ogni modifica, attendi **15-30 minuti**
- Poi torna su Mailgun e clicca **"Verify DNS Settings"**

---

## ✅ VERIFICA FINALE

Dopo tutte le modifiche, su Mailgun dovresti vedere tutti i record con lo status **✅ verde** o **"Verified"**.








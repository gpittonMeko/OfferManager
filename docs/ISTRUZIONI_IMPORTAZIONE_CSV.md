# 📥 Come Importare il File CSV Corretto su Register.it

## 📋 File Pronto

Ho creato il file: **`Elenco_record_dns_infomekosrl.it_CORRETTO.csv`**

## 🔧 Modifiche Applicate

### ❌ RIMOSSO:
- `infomekosrl.it.` MX `10 mail.register.it.`

### ⚠️ MODIFICATO:
1. `mxa.mailgun.org.` → `mxa.eu.mailgun.org.`
2. `mxb.mailgun.org.` → `mxb.eu.mailgun.org.`
3. `email.infomekosrl.it.` CNAME `mailgun.org.` → `eu.mailgun.org.`

### ✅ AGGIUNTO:
- Nuovo record DKIM: `s1._domainkey.infomekosrl.it.` TXT

## 📝 COME IMPORTARE SU REGISTER.IT

### Metodo 1: Importazione CSV (se supportato)

1. Vai nel pannello Register.it
2. Vai su **"Configurazione DNS" → "Zona DNS"**
3. Cerca un pulsante **"Importa CSV"** o **"Carica File"**
4. Carica il file: `Elenco_record_dns_infomekosrl.it_CORRETTO.csv`
5. Verifica che i record siano corretti
6. **Salva**

### Metodo 2: Modifica Manuale (consigliato)

Se l'importazione CSV non è disponibile, modifica manualmente:

#### STEP 1: Rimuovi Record MX Vecchio
- Trova: `infomekosrl.it.` MX `10 mail.register.it.`
- **ELIMINA** questa riga

#### STEP 2: Modifica Record MX Mailgun
- Trova: `infomekosrl.it.` MX `10 mxa.mailgun.org.`
- Cambia il valore in: `mxa.eu.mailgun.org.`
- Trova: `infomekosrl.it.` MX `10 mxb.mailgun.org.`
- Cambia il valore in: `mxb.eu.mailgun.org.`

#### STEP 3: Modifica CNAME Tracking
- Trova: `email.infomekosrl.it.` CNAME `mailgun.org.`
- Cambia il valore in: `eu.mailgun.org.`

#### STEP 4: Aggiungi Record DKIM
- Clicca **"Aggiungi Record"**
- Nome: `s1._domainkey.infomekosrl.it.`
- Tipo: `TXT`
- Valore: `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCyv+MPiEj5VfoD1q5AthXKSf0z2aL6n0Zh/wMxZi0EuP7mSFGXcTxx2nc0iTWkFoL67oGKu+GKx86t+L7GT8ctuTMldcURKKOYdFCCdgeDpnSv+++xaRQCo3G6k8IjgsEPRdPyoSDybo0MonISGg8FEm/gEdZ5rB6SZMw4W33HTwIDAQAB`
- TTL: `900`
- **Salva**

## ⏱️ Dopo l'Importazione

1. **Attendi 15-30 minuti** per la propagazione DNS
2. Torna su **Mailgun Dashboard**
3. Clicca su **"Verify DNS Settings"**
4. Verifica che tutti i record risultino ✅ **"Verified"**

## ✅ Checklist Finale

- [ ] Record MX vecchio rimosso
- [ ] Record MX Mailgun aggiornati (con .eu)
- [ ] CNAME tracking aggiornato (con .eu)
- [ ] Record DKIM `s1._domainkey` aggiunto
- [ ] Atteso 15-30 minuti
- [ ] Verificato su Mailgun che tutto sia "Verified"








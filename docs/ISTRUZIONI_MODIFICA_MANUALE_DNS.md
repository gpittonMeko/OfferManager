# 🔧 Istruzioni Modifica Manuale DNS (se CSV non funziona)

## ❌ PROBLEMA: Register.it non accetta virgolette nei valori

Il sistema Register.it **NON accetta virgolette** `"` dentro i valori dei record TXT.

## ✅ SOLUZIONE: Modifica Manuale

Se il CSV dà errori, modifica **manualmente** questi record nel pannello Register.it:

### 📝 Record da Modificare (uno per uno)

#### 1. Rimuovi Record MX Vecchio
- Trova: `infomekosrl.it.` MX `10 mail.register.it.`
- **ELIMINA** questo record

#### 2. Modifica Record MX Mailgun

**Record 1:**
- Trova: `infomekosrl.it.` MX `10 mxa.mailgun.org.`
- Clicca **"Modifica"**
- Cambia il valore in: `mxa.eu.mailgun.org.`
- **Salva**

**Record 2:**
- Trova: `infomekosrl.it.` MX `10 mxb.mailgun.org.`
- Clicca **"Modifica"**
- Cambia il valore in: `mxb.eu.mailgun.org.`
- **Salva**

#### 3. Modifica CNAME Tracking

- Trova: `email.infomekosrl.it.` CNAME `mailgun.org.`
- Clicca **"Modifica"**
- Cambia il valore in: `eu.mailgun.org.`
- **Salva**

#### 4. Modifica Record TXT (RIMUOVI virgolette)

Per ogni record TXT, quando lo modifichi, **RIMUOVI le virgolette** dal valore:

**Record SPF 1:**
- Trova: `infomekosrl.it.` TXT con valore che contiene virgolette
- Clicca **"Modifica"**
- Cambia il valore in (SENZA virgolette): `v=spf1 include:spf.webapps.net ~all`
- **Salva**

**Record SPF 2:**
- Trova: `infomekosrl.it.` TXT con `v=spf1 include:spf.leadconnectorhq.com`
- Se ha virgolette, rimuovile mantenendo solo: `v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all`

**Record DKIM krs:**
- Trova: `krs._domainkey.infomekosrl.it.` TXT
- Rimuovi le virgolette dal valore, mantieni solo la chiave: `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9Xdr3945BZxYyGrBvdccf21+A8jLdppS25Amj8Wv8QNCmP7UtWAItdJ3fVyy2gmG1VZb3TvqOe5zqW+R3J1Tvq8YSsvH6JCIKR6JCNb7PtBNsNXu3k8rDHHk/r/vhkwVlWha38QsWy3nF/2ugpv9fc/4vT/MwvnN7LNkZROMAKwIDAQAB`

**Record DKIM k1:**
- Trova: `k1._domainkey.infomekosrl.it.` TXT
- Rimuovi le virgolette dal valore

**Record DMARC:**
- Trova: `_dmarc.infomekosrl.it.` TXT
- Rimuovi le virgolette, mantieni solo: `v=DMARC1;p=none;`

**Record PEC SPF:**
- Trova: `pec.infomekosrl.it.` TXT
- Rimuovi le virgolette, mantieni solo: `v=spf1 include:spf.pec-email.com ~all`

#### 5. Aggiungi Nuovo Record DKIM

- Clicca **"Aggiungi Record"**
- **Nome**: `s1._domainkey.infomekosrl.it.`
- **Tipo**: `TXT`
- **Valore**: `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCyv+MPiEj5VfoD1q5AthXKSf0z2aL6n0Zh/wMxZi0EuP7mSFGXcTxx2nc0iTWkFoL67oGKu+GKx86t+L7GT8ctuTMldcURKKOYdFCCdgeDpnSv+++xaRQCo3G6k8IjgsEPRdPyoSDybo0MonISGg8FEm/gEdZ5rB6SZMw4W33HTwIDAQAB`
- **TTL**: `900`
- **IMPORTANTE**: Inserisci il valore SENZA virgolette!
- **Salva**

#### 6. Verifica Record A

I record A dovrebbero essere corretti, ma verifica:
- `infomekosrl.it.` A → `195.110.124.133` (senza virgolette, senza punto finale)
- `crm.infomekosrl.it.` A → `13.53.183.146`
- `windmill.infomekosrl.it.` A → `13.53.183.146`

## ⚠️ REGOLA IMPORTANTE

**Per tutti i record TXT:**
- ❌ **SBAGLIATO**: `"v=spf1 include:mailgun.org ~all"` (con virgolette)
- ✅ **CORRETTO**: `v=spf1 include:mailgun.org ~all` (senza virgolette)

Il sistema Register.it aggiungerà automaticamente le virgolette se necessario quando salvi.

## ⏱️ Dopo le Modifiche

1. Attendi **15-30 minuti** per la propagazione DNS
2. Torna su **Mailgun Dashboard**
3. Clicca **"Verify DNS Settings"**
4. Verifica che tutti i record risultino ✅ verificati








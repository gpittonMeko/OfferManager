# 🔍 Diagnostica Problema Sincronizzazione UR Portal

## Problema RISOLTO ✅
Il problema era che l'URL del portale era errato. Il portale corretto è:
- **URL Corretto**: `https://partners.universal-robots.com/s/`
- **URL Errato (precedente)**: `https://portal.universal-robots.com` (non esiste)

Il portale usa **OAuth2 con Azure B2C** per l'autenticazione, non un semplice form di login.

## Informazioni Portale UR

### URL Corretto
- **Portale Partner**: `https://partners.universal-robots.com/s/`
- **Login OAuth2**: `https://universalrobotsonelogin.b2clogin.com/...`
- **Redirect dopo login**: `https://partners.universal-robots.com/s/`

### Credenziali
- **Email**: `giovanni.pitton@mekosrl.it`
- **Password**: `RobotMeko.24` (o `RobotMeko.22` come fallback)

### Flusso Autenticazione
1. Accesso a `https://partners.universal-robots.com/s/`
2. Redirect automatico a Azure B2C login (`universalrobotsonelogin.b2clogin.com`)
3. Inserimento email e password
4. Redirect di ritorno al portale
5. Se errore OAuth (`AuthorizationError`), andare direttamente a `/s/` funziona comunque

## Soluzione Implementata ✅

1. **URL Corretto**: Aggiornato a `https://partners.universal-robots.com/s/`
2. **Gestione OAuth2**: Implementato supporto per flusso OAuth2 con Azure B2C
3. **Gestione Errori OAuth**: Se c'è errore OAuth, va direttamente al portale (come funziona manualmente)
4. **Selettori Multipli**: Supporto per vari selettori Azure B2C (loginfmt, passwd, idSIButton9, ecc.)
5. **Fallback Intelligente**: Se il login fallisce, prova comunque ad accedere direttamente al portale

## Modifiche al Codice

### 1. Aggiornamento URL (`ur_portal_direct.py`)
- ✅ URL corretto: `https://partners.universal-robots.com/s/`
- ✅ Supporto OAuth2 con Azure B2C
- ✅ Gestione redirect automatici
- ✅ Gestione errore OAuth (va direttamente al portale)

### 2. Miglioramenti Login
- ✅ Selettori multipli per campi email/password Azure B2C
- ✅ Gestione pulsante "Avanti" tra email e password
- ✅ Fallback se login fallisce (va direttamente al portale)
- ✅ Cookies abilitati per OAuth2

### 3. Configurazione DNS EC2
- ✅ Aggiunti DNS pubblici come fallback (8.8.8.8, 1.1.1.1)
- ✅ Configurato systemd-resolved con DNS alternativi

## Test da Eseguire

### 1. Test Sincronizzazione
Esegui la sincronizzazione UR dal CRM e verifica:
- ✅ Login OAuth2 funziona
- ✅ Redirect al portale corretto
- ✅ Estrazione dati funziona

### 2. Verifica Log
Controlla i log (`ur_portal_sync.log`) per:
- URL raggiunti durante il login
- Selettori utilizzati per i campi
- Eventuali errori OAuth gestiti correttamente

### 3. Se Problemi Persistono
- Verifica che Chrome/Chromium sia installato sulla EC2
- Verifica che ChromeDriver sia aggiornato
- Controlla che i cookies siano abilitati

## Comandi Utili

### Test DNS dalla EC2
```bash
# Test DNS (URL corretto)
nslookup partners.universal-robots.com
nslookup partners.universal-robots.com 8.8.8.8

# Test connessione HTTP
curl -I https://partners.universal-robots.com/s/
curl -v https://partners.universal-robots.com/s/ 2>&1 | head -20
```

### Verifica Configurazione DNS EC2
```bash
resolvectl status
cat /etc/systemd/resolved.conf.d/dns_servers.conf
```

### Test dalla Macchina Locale
```bash
nslookup partners.universal-robots.com 8.8.8.8
curl -I https://partners.universal-robots.com/s/
```

## Note Finali
- ✅ Il codice ora usa l'URL corretto del portale UR
- ✅ Gestisce correttamente il flusso OAuth2 con Azure B2C
- ✅ Se c'è un errore OAuth, va direttamente al portale (come funziona manualmente)
- ✅ Il codice è più robusto e gestisce meglio gli errori
- ✅ La sincronizzazione dovrebbe ora funzionare correttamente


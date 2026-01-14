# 🗺️ Configurazione Google Maps API

## Problema: InvalidKeyMapError

Se vedi l'errore `InvalidKeyMapError`, significa che la chiave API di Google Maps non è valida o non è configurata correttamente.

## Soluzione: Configurare una Chiave API Valida

### 1. Crea una Chiave API su Google Cloud

1. Vai su [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita le seguenti API:
   - **Maps JavaScript API** (per la mappa interattiva)
   - **Geocoding API** (per convertire indirizzi in coordinate)
4. Vai su **Credentials** → **Create Credentials** → **API Key**
5. Copia la chiave API generata

### 2. Configura la Chiave sul Server EC2

**Opzione A: Variabile d'Ambiente (Consigliato)**

Connettiti al server EC2:
```bash
ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@13.53.183.146
```

Aggiungi la variabile d'ambiente al servizio systemd:
```bash
sudo nano /etc/systemd/system/offermanager.service
```

Aggiungi nella sezione `[Service]`:
```ini
Environment="GOOGLE_MAPS_API_KEY=LA_TUA_CHIAVE_API_QUI"
```

Ricarica e riavvia:
```bash
sudo systemctl daemon-reload
sudo systemctl restart offermanager
```

**Opzione B: File .env**

Crea/modifica il file `.env` nella directory del progetto:
```bash
cd /home/ubuntu/offermanager
nano .env
```

Aggiungi:
```
GOOGLE_MAPS_API_KEY=LA_TUA_CHIAVE_API_QUI
```

### 3. Verifica la Configurazione

1. Apri il browser su: `http://13.53.183.146`
2. Vai su "🗺️ Mappa Contatti"
3. La mappa dovrebbe caricarsi correttamente senza errori

## Restrizioni della Chiave API (Opzionale ma Consigliato)

Per sicurezza, configura le restrizioni della chiave API:

1. Vai su [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Clicca sulla tua chiave API
3. Nella sezione **Application restrictions**:
   - Seleziona "HTTP referrers (web sites)"
   - Aggiungi: `http://13.53.183.146/*` e `https://13.53.183.146/*`
4. Nella sezione **API restrictions**:
   - Seleziona "Restrict key"
   - Seleziona solo: "Maps JavaScript API" e "Geocoding API"
5. Salva

## Costi

Google Maps API offre un **free tier** generoso:
- **$200 di credito gratuito al mese**
- Dopo il free tier: ~$7 per 1000 richieste Maps JavaScript API
- Dopo il free tier: ~$5 per 1000 richieste Geocoding API

Per un uso normale del CRM, il free tier dovrebbe essere sufficiente.

## Troubleshooting

### Errore persiste dopo la configurazione

1. Verifica che la variabile d'ambiente sia stata caricata:
   ```bash
   sudo systemctl show offermanager | grep GOOGLE_MAPS_API_KEY
   ```

2. Verifica i log del servizio:
   ```bash
   sudo journalctl -u offermanager -f
   ```

3. Riavvia il servizio:
   ```bash
   sudo systemctl restart offermanager
   ```

### La mappa non si carica

1. Controlla la console del browser (F12) per errori JavaScript
2. Verifica che le API siano abilitate su Google Cloud Console
3. Controlla che la chiave API non abbia restrizioni troppo severe

# Pulizia Nomi Account

## Problema
I nomi degli account contengono caratteri strani come `~$` all'inizio (file temporanei Windows) e altri caratteri non validi.

## Soluzione

### Script di Pulizia
Esegui sul server cloud:
```bash
cd /home/ubuntu/offermanager
python3 pulisci_nomi_account.py
```

### Cosa fa lo script:
1. Rimuove prefissi `~$` dai nomi
2. Rimuove caratteri speciali non standard
3. Normalizza spazi multipli
4. Capitalizza correttamente i nomi
5. Evita duplicati (se un nome pulito esiste già, salta l'aggiornamento)

### Esempi di pulizia:
- `~$022 BWS SRL UR20` → `022 BWS SRL UR20`
- `~$060 UNIVERSITA' DEGLI STUDI DI BRESCIA UNITREE G1 EDU U6` → `060 Universita' Degli Studi Di Brescia Unitree G1 Edu U6`
- `~$191 TOD SYSTEM SRL UNITREE GO2 PRO` → `191 Tod System SRL Unitree GO2 PRO`

### Prevenzione Futura
Lo script `sync_offers_2025_2026.py` ora pulisce automaticamente i nomi durante la sincronizzazione, quindi questo problema non dovrebbe più verificarsi.

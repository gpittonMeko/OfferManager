# Riepilogo Sincronizzazione Portali

## Portali Sincronizzati

### 1. Portale Universal Robots (`/api/ur/sync`)
- **Fonte**: partners.universal-robots.com
- **Dati**: Opportunità e Leads dal portale UR
- **Metodo**: Playwright automation
- **Frequenza**: Giornaliera (2:00 AM)

### 2. Portale Offerte (`/api/offers/sync`)
- **Fonte**: Cartelle Windows (K:\OFFERTE - K)
- **Dati**: File PDF/DOCX nelle cartelle offerte
- **Metodo**: Scansione filesystem
- **Frequenza**: Giornaliera (2:00 AM)

### 3. Portale Wix Studio (`/api/wix/sync`)
- **Fonte**: manage.wix.com (form contatti)
- **Dati**: 104 submissions dal form Wix
- **Metodo**: Playwright scraping + import JSON
- **Frequenza**: Giornaliera (2:00 AM)
- **Stato**: ✅ 34 contatti importati come Opportunità

### 4. Database Marittimo (ROV)
- **Fonte**: Script `aggiungi_contatti_marittimi.py`
- **Dati**: 326+ contatti marittimi (Marine, Università, Cantieri)
- **Metodo**: Conversione Lead → Opportunità
- **Frequenza**: Giornaliera (2:00 AM)
- **Stato**: ✅ 326 Lead convertiti in Opportunità

### 5. VoxMail (Liste Email Marketing)
- **Fonte**: Database CRM interno (tabelle `email_lists`, `email_list_contacts`)
- **Dati**: Contatti organizzati in liste per campagne
- **Metodo**: Verifica stato liste
- **Frequenza**: Giornaliera (2:00 AM)

## Statistiche Attuali

- **Opportunità totali**: ~400+
- **Opportunità "fredda_speranza"**: 225+
- **Lead marittimi convertiti**: 326
- **Contatti Wix importati**: 34 (su 104 totali)

## Prossimi Passi

1. ✅ **Completare importazione Wix**: Scrapare tutti i 104 contatti
2. ✅ **Convertire Lead marittimi**: Completato (326 convertiti)
3. ⏳ **Verificare sincronizzazione automatica**: Test completo

## Comandi Utili

```bash
# Sincronizzazione manuale completa
POST /api/sync/all

# Sincronizzazione singoli portali
POST /api/ur/sync      # Universal Robots
POST /api/offers/sync  # Offerte cartelle
POST /api/wix/sync     # Wix Studio

# Conversione Lead marittimi
python3 scripts/converti_lead_marittimi_opportunita.py

# Scraping Wix Studio
python3 utils/wix_forms_scraper.py

# Verifica importazioni
python3 scripts/verifica_importazione_wix.py
```

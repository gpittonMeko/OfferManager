# MekoCRM - Sistema Completo

## File Creati

1. **crm_app_completo.py** - Applicazione Flask principale con struttura Salesforce-like
   - Modelli: User, Lead, Account, Contact, Opportunity, OpportunityLineItem, Product, PriceBookEntry, OfferDocument
   - API routes complete per tutte le entità
   - Dashboard analytics

2. **price_loader.py** - Caricamento listini da file ufficiali
   - Supporta UR Excel, MiR PDF, Unitree PDF, ROEQ PDF
   - Estrae tutti i livelli di prezzo (bronze, silver, gold, ur_acquisto, ur_si, mir_distributor, etc.)

3. **analyze_past_offers.py** - Analisi offerte PDF passate
   - Analizza cartella `C:\Users\user\Documents\Offerte`
   - Estrae prodotti, totali, date, clienti
   - Importa nel CRM come Opportunities e OfferDocuments

4. **ur_portal_integration.py** - Integrazione portale UR
   - Sincronizza leads, opportunities, accounts dal portale UR
   - Utilizza progetto esistente "UR Twenty integration"

5. **init_crm_complete.py** - Script di inizializzazione
   - Carica listini
   - Importa offerte passate
   - Sincronizza UR portal

## Setup

1. **Installa dipendenze:**
```bash
pip install flask flask-sqlalchemy werkzeug pdfplumber pandas openpyxl
```

2. **Inizializza database:**
```bash
python init_crm_complete.py
```

3. **Avvia CRM:**
```bash
python crm_app_completo.py
```

4. **Accedi:**
- URL: http://localhost:8000
- Username: admin / Password: admin123
- Username: demo / Password: demo123

## API Endpoints

### Dashboard
- `GET /api/dashboard/summary` - Metriche dashboard

### Leads
- `GET /api/leads` - Lista leads
- `POST /api/leads` - Crea lead
- `POST /api/leads/<id>/convert` - Converti lead in account/opportunity

### Accounts
- `GET /api/accounts` - Lista accounts
- `POST /api/accounts` - Crea account

### Opportunities
- `GET /api/opportunities` - Lista opportunities
- `POST /api/opportunities` - Crea opportunity

### Products
- `GET /api/products` - Lista prodotti con tutti i livelli prezzo
- `PUT /api/products/<id>/prices` - Modifica prezzo prodotto

### Pricebook
- `POST /api/pricebook/sync` - Sincronizza listini

### Offers
- `GET /api/offers` - Lista offerte
- `POST /api/offers/import-past` - Importa offerte passate

### UR Portal
- `POST /api/ur/sync` - Sincronizza portale UR

### Analytics
- `GET /api/analytics/pipeline?period=month` - Analytics pipeline per categoria e periodo

## Struttura Database

- **User**: Utenti/commerciali
- **Lead**: Prospect da convertire
- **Account**: Aziende clienti
- **Contact**: Contatti degli account
- **Opportunity**: Opportunità di vendita
- **OpportunityLineItem**: Prodotti nelle opportunity
- **Product**: Catalogo prodotti
- **PriceBookEntry**: Prezzi per livello (bronze, silver, gold, ur_acquisto, etc.)
- **OfferDocument**: Documenti offerta generati

## Note

- I listini vengono caricati da `C:\Users\user\Documents\Listini`
- Le offerte passate vengono analizzate da `C:\Users\user\Documents\Offerte`
- Il portale UR richiede il progetto "UR Twenty integration" nella directory parent
- Tutti i prezzi sono flessibili e possono essere modificati manualmente
- La struttura è portabile e facilmente estendibile










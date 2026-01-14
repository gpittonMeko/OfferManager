# GUIDA DATABASE - MEKOCRM

## ⚠️ IMPORTANTE: LEGGERE PRIMA DI MODIFICARE QUALSIASI COSA

### ⚠️ COME FUNZIONA FLASK CON SQLITE:

**CONFIGURAZIONE ORIGINALE**: `sqlite:///mekocrm.db`

Quando Flask vede `sqlite:///mekocrm.db` (senza percorso assoluto), cerca automaticamente nella cartella `instance/`!

Quindi:
- Configurazione: `sqlite:///mekocrm.db`
- File reale: `instance/mekocrm.db`
- **NON MODIFICARE QUESTA CONFIGURAZIONE!**

### Database Principale
**PERCORSO REALE**: `instance/mekocrm.db`  
**CONFIGURAZIONE**: `sqlite:///mekocrm.db` (in `crm_app_completo.py`)  
**DIMENSIONE**: ~2.1MB  
**CONTENUTO**: 
- ✅ 201 Opportunità
- ✅ 200 Accounts
- ✅ 1902 Leads
- ✅ 180 Prodotti
- ✅ 15 Utenti
- ✅ Tutti i dati reali del CRM

### ⚠️ NON TOCCARE QUESTI FILE:
- `instance/mekocrm.db` - **DATABASE PRINCIPALE CON TUTTI I DATI**
- `instance/offer_manager_crm.db` - Database backup/alternativo

### Database di Test/Vuoti (possono essere ricreati):
- `crm.db` - Database vuoto di test
- `mekocrm.db` - Database vuoto nella root

---

## PROCEDURA PER MODIFICHE AL DATABASE

### 1. SEMPRE VERIFICARE PRIMA QUALI DATI CI SONO:
```bash
python3 verifica_database_reale.py
```

### 2. SEMPRE FARE BACKUP PRIMA DI MODIFICHE:
```bash
cp instance/mekocrm.db instance/mekocrm.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. VERIFICARE QUALE DATABASE USA L'APPLICAZIONE:
Controllare in `crm_app_completo.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mekocrm.db'
```

**IMPORTANTE**: Con questa configurazione, Flask cerca automaticamente in `instance/mekocrm.db`
**NON cambiare questa configurazione a meno che non sia assolutamente necessario!**

### 4. SE SERVE AGGIUNGERE COLONNE:
- Usare script di migrazione separati
- Testare prima su database di test
- Verificare che i dati esistenti non vengano persi

---

## STRUTTURA TABELLE IMPORTANTI

### Tabella `users`:
- id, username, password, email
- first_name, last_name (aggiunte dopo)
- role, created_at, updated_at

### Tabella `opportunities`:
- id, name, stage, amount, probability
- close_date, opportunity_type, description
- supplier_category, folder_path, heat_level
- owner_id, account_id, contact_id, lead_id
- created_at, updated_at

### Tabella `offers`:
- id, number, amount, status
- pdf_path, docx_path
- opportunity_id, created_at

---

## COMANDI UTILI

### Verificare dati:
```bash
python3 verifica_dati.py
```

### Verificare quale database contiene dati:
```bash
python3 verifica_database_reale.py
```

### Backup database:
```bash
cp instance/mekocrm.db instance/mekocrm.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Ripristinare backup:
```bash
cp instance/mekocrm.db.backup.YYYYMMDD_HHMMSS instance/mekocrm.db
```

---

## REGOLE D'ORO

1. ✅ **SEMPRE** verificare quale database contiene i dati prima di modificare
2. ✅ **SEMPRE** fare backup prima di modifiche strutturali
3. ✅ **MAI** modificare `instance/mekocrm.db` senza backup
4. ✅ **MAI** cambiare il percorso del database senza verificare prima
5. ✅ **SEMPRE** testare modifiche su database di test prima

---

## TROUBLESHOOTING

### Errore "no such table: users"
- Verificare che il percorso del database sia corretto
- Verificare che il database esista: `ls -lh instance/mekocrm.db`
- Verificare che contenga dati: `python3 verifica_database_reale.py`

### Errore "no such column"
- Il database ha struttura vecchia
- Usare script di migrazione per aggiungere colonne
- **NON** ricreare il database (si perdono i dati!)

### Database vuoto
- Verificare di non aver cambiato il percorso per sbaglio
- Ripristinare da backup se disponibile
- Controllare log per vedere quale database viene usato

---

**ULTIMA MODIFICA**: 2026-01-09  
**DATABASE ATTIVO**: `instance/mekocrm.db`

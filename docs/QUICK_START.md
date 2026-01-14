# ⚡ QUICK START

## 🚀 RIAVVIA SERVER CLOUD (1 CLICK)

**Doppio click su:** `deploy\riavvia_server_semplice.bat`

Questo è TUTTO quello che devi fare per riavviare il server con le ultime modifiche!

---

## 📁 STRUTTURA CHIARA

```
OfferManager/
│
├── ⭐ FILE PRINCIPALI (NON SPOSTARE)
│   ├── crm_app_completo.py          → App principale Flask
│   ├── sync_offers_from_folder.py   → Sincronizza offerte
│   └── pulisci_nomi_account.py      → Pulizia account
│
├── 📦 deploy/                        → Script per AWS Cloud
│   └── riavvia_server_semplice.bat  → ⭐ USA QUESTO!
│
├── 🔧 migrations/                    → Script migrazione DB
├── 📜 scripts/                       → Script utilità
├── 🛠️ utils/                         → Utility e helper
├── 📚 docs/                          → Documentazione
│
├── templates/                        → Template HTML
└── instance/                         → Database locale (ignorato da git)
```

---

## ⚠️ REGOLE D'ORO

1. **NON modificare** file in `deploy/` senza motivo
2. **NON committare** file in `instance/` (database locale)
3. **SEMPRE usare** `deploy\riavvia_server_semplice.bat` per riavviare
4. **SEMPRE testare** localmente prima di fare deploy

---

## 🔍 SVILUPPO LOCALE

```bash
python crm_app_completo.py
```

Server locale: `http://localhost:8000`

---

## 🌐 DEPLOY CLOUD

1. Modifica `crm_app_completo.py`
2. Doppio click su `deploy\riavvia_server_semplice.bat`
3. Fatto! ✅

---

## 📞 PROBLEMI?

1. Verifica che la chiave `.pem` esista: `C:\Users\user\Documents\LLM_14.pem`
2. Controlla connessione: `ssh -i "C:\Users\user\Documents\LLM_14.pem" ubuntu@13.53.183.146`
3. Leggi `docs/README_DEPLOY.md` per dettagli

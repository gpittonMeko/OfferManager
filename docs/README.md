# OfferManager - Configuratore Intelligente di Offerte

Sistema intelligente per la generazione automatica di offerte commerciali basato su listini PDF.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Funzionalità

- 📄 **Parser PDF Intelligente**: Estrae automaticamente prodotti, prezzi e descrizioni dai listini
- 📝 **Generazione DOCX Professionale**: Crea offerte in formato Word con formattazione professionale
- 🤖 **Linguaggio Naturale**: Comprende richieste come *"fammi un'offerta con due unitree g1 u6 prezzo bronze"*
- 🔍 **Ricerca Online**: Trova automaticamente le intestazioni aziendali (P.IVA, indirizzo, contatti)
- 📅 **Date Automatiche**: Aggiorna automaticamente date e validità dell'offerta
- 💰 **Calcolo Totali**: Calcola automaticamente totali, subtotali e applica i listini corretti
- 📊 **Multi-Listino**: Supporta più listini contemporaneamente (Umanoidi, Quadrupedi, ecc.)
- ⚙️ **Configurabile**: Personalizza intestazioni, termini e condizioni, validità

## 📋 Requisiti

- Python 3.8 o superiore
- Sistema operativo: Windows, macOS, Linux

## 🚀 Installazione

1. **Clona o scarica il progetto**

2. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Prepara i tuoi listini**:
   - Metti i file PDF dei listini nella directory del progetto
   - Opzionalmente, aggiungi un template DOCX personalizzato

## 💻 Utilizzo

### Modalità 1: Interfaccia Interattiva (Raccomandata per principianti)

Esegui semplicemente:

```bash
python offer_manager.py
```

Ti apparirà un menu con opzioni:
```
╔══════════════════════════════════════════════════════════════╗
║           📋 OFFER MANAGER - Configuratore Offerte          ║
╚══════════════════════════════════════════════════════════════╝

  1. 🤖 Crea offerta (modalità linguaggio naturale)
  2. 📋 Visualizza prodotti disponibili
  3. 🔍 Cerca prodotto nel listino
  4. ⚙️  Configura impostazioni
  5. 📄 Esempio di utilizzo
  0. ❌ Esci
```

### Modalità 2: Uso Programmatico (Per sviluppatori)

```python
from offer_generator import OfferGenerator

# Inizializza il generatore
gen = OfferGenerator()

# Carica i listini PDF
gen.load_pricelists([
    "08102025_ListinoUmanoidi_Partner.pdf",
    "08102025_ListinoQuadrupedi_Partner.pdf"
])

# Genera un'offerta con linguaggio naturale
doc_handler, offer_info = gen.create_offer(
    request="fammi un'offerta con due unitree g1 u6 prezzo bronze",
    company_name="Acme Corporation"
)

# Salva l'offerta
gen.save_offer(doc_handler, "offerta_acme.docx")

print(f"✅ Offerta {offer_info['offer_number']} creata!")
print(f"💰 Totale: €{offer_info['total']:,.2f}")
```

### Modalità 3: Esempi Pronti

Esplora esempi di utilizzo:

```bash
python example_usage.py
```

## 📖 Esempi di Richieste

### Sintassi Base
```
[quantità] [nome prodotto] prezzo [livello]
```

### Esempi Pratici

| Richiesta | Risultato |
|-----------|-----------|
| `fammi un'offerta con due unitree g1 u6 prezzo bronze` | 2x Unitree G1 U6 a prezzo Bronze |
| `offerta con un go2 edu silver e tre b2 gold` | 1x GO2 EDU (Silver) + 3x B2 (Gold) |
| `3 robot h1 prezzo bronze` | 3x H1 a prezzo Bronze |
| `offerta unitree go2 pro silver` | 1x GO2 Pro a prezzo Silver |

### Livelli di Prezzo

| Livello | Alias | Descrizione |
|---------|-------|-------------|
| 🥉 **Bronze** | bronzo | Prezzo base per partner |
| 🥈 **Silver** | argento | Prezzo intermedio |
| 🥇 **Gold** | oro | Prezzo premium |

## 📁 Struttura del Progetto

```
OfferManager/
├── 📄 offer_manager.py         # Script principale (interfaccia interattiva)
├── 🤖 offer_generator.py       # Motore di generazione offerte
├── 📋 pdf_parser.py            # Parser per listini PDF
├── 📝 docx_handler.py          # Gestore documenti Word
├── 🔍 company_searcher.py      # Ricerca info aziende online
├── 📚 example_usage.py         # Esempi di utilizzo
├── 📦 requirements.txt         # Dipendenze Python
├── 📖 README.md                # Documentazione principale
├── 📘 USAGE.md                 # Guida dettagliata all'uso
└── 🚫 .gitignore               # File da escludere
```

## 🔧 Configurazione

### Personalizza le Info del Fornitore

Dal menu interattivo (opzione 4) oppure via codice:

```python
gen.set_supplier_info({
    'name': 'ME.KO. Srl',
    'address': 'Via Example 123, 00100 Roma (RM)',
    'vat': '12345678901',
    'email': 'info@meko.it',
    'phone': '+39 06 1234567'
})
```

### Usa un Template Personalizzato

```python
gen = OfferGenerator(template_path="mio_template.docx")
```

## 🎯 Caratteristiche del Documento Generato

Le offerte includono automaticamente:

✅ **Intestazione Fornitore** (nome, indirizzo, P.IVA, contatti)  
✅ **Numero Offerta Univoco** (formato: K####-YY)  
✅ **Data e Validità** (default 30 giorni, personalizzabile)  
✅ **Informazioni Cliente** (con ricerca automatica online)  
✅ **Tabella Prodotti Dettagliata** (codice, descrizione, q.tà, prezzi)  
✅ **Totali e Subtotali** (calcolo automatico)  
✅ **Note e Condizioni** (consegna, IVA, ecc.)  
✅ **Termini e Condizioni** (pagamento, garanzia, supporto)  
✅ **Sezione Firme** (fornitore e cliente)  

## 🛠️ Risoluzione Problemi

### Problema: "Nessun prodotto trovato"
**Soluzione**: Verifica che i PDF dei listini siano nella directory corretta e non protetti da password.

### Problema: "Prodotto non trovato nel listino"
**Soluzione**: Usa l'opzione di ricerca (menu → 3) per vedere i nomi esatti dei prodotti disponibili.

### Problema: "Errore nel parsing del PDF"
**Soluzione**: Assicurati che i PDF contengano testo estraibile (non solo immagini).

Per maggiori dettagli, consulta [USAGE.md](USAGE.md).

## 📚 Documentazione

- **[README.md](README.md)** - Panoramica e installazione (questo file)
- **[USAGE.md](USAGE.md)** - Guida dettagliata all'uso
- **[example_usage.py](example_usage.py)** - Esempi di codice

## 🤝 Contributi

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti!

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT.

## 👨‍💻 Autore

Creato per ME.KO. Srl

---

**Nota**: Questo è un sistema intelligente che migliora con l'uso. Se riscontri imprecisioni nel riconoscimento dei prodotti o nelle interpretazioni delle richieste, contattami per miglioramenti.


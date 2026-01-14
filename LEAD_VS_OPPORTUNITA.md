# Lead vs Opportunità - Guida

## Differenza tra Lead e Opportunità

### Lead
- **Cos'è**: Un contatto potenziale non ancora qualificato
- **Quando usare**: Quando ricevi un contatto generico senza informazioni specifiche sul prodotto/interesse
- **Stato**: Non ancora qualificato, bisogno di più informazioni
- **Esempio**: "Qualcuno ha lasciato il numero su un volantino"

### Opportunità
- **Cos'è**: Un contatto qualificato con interesse specifico per un prodotto/servizio
- **Quando usare**: Quando il contatto ha espresso interesse per un prodotto specifico
- **Stato**: Qualificato, pronto per essere seguito
- **Esempio**: "Cliente interessato a Unitree G1 per applicazione industriale"

## Per i contatti Wix Studio

**Scelta: Importare direttamente come Opportunità** ✅

**Motivi:**
1. ✅ Hanno già espresso interesse per un prodotto specifico (campo "product")
2. ✅ Hanno lasciato un messaggio dettagliato (campo "message")
3. ✅ Sono già qualificati (hanno compilato il form)
4. ✅ Non serve il passaggio intermedio Lead

**Configurazione:**
- Stage: "Qualification"
- Heat Level: "fredda_speranza" (5% probabilità)
- Attività: "Chiamare cliente"
- Supplier Category: determinata automaticamente dal prodotto

## Conversione Lead → Opportunità

Se hai già dei Lead e vuoi convertirli in Opportunità:

1. Vai alla lista Lead nel CRM
2. Clicca su "Converti" per il Lead che vuoi convertire
3. Il sistema crea automaticamente:
   - Account (azienda)
   - Contact (contatto)
   - Opportunity (opportunità)

**Endpoint API:**
```
POST /api/leads/<lead_id>/convert
```

## Importazione Wix

**Metodo consigliato:**
```bash
# Importa direttamente come Opportunità
python3 utils/wix_forms_import.py data/wix_submissions.json
```

**Risultato:**
- ✅ Account creato/aggiornato
- ✅ Contact creato/aggiornato  
- ✅ Opportunity creata con attività "Chiamare"
- ✅ Heat Level: "fredda_speranza"
- ✅ Supplier Category: determinata automaticamente

## Vantaggi importazione diretta come Opportunità

1. **Più veloce**: Un solo passaggio invece di due (Lead → Opportunità)
2. **Più completo**: Tutte le informazioni vengono inserite subito
3. **Meno confusione**: Non hai Lead che aspettano conversione
4. **Più organizzato**: Tutte le opportunità sono già pronte per essere seguite

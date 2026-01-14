# Istruzioni per Importare Contatti da Outlook

## Prerequisiti

1. **Outlook deve essere installato e configurato** sul tuo computer Windows
2. **Outlook deve essere aperto** quando esegui lo script
3. Installa la dipendenza necessaria:
   ```bash
   pip install pywin32
   ```

## Come Usare

1. **Assicurati che Outlook sia aperto** sul tuo computer
2. **Esegui lo script**:
   ```bash
   python importa_contatti_outlook.py
   ```

## Cosa Fa lo Script

1. **Si connette a Outlook** e accede alla cartella Contatti
2. **Estrae tutti i contatti** con le loro informazioni:
   - Nome e Cognome
   - Email
   - Telefono (business o mobile)
   - Titolo lavorativo
   - Dipartimento
   - Nome azienda

3. **Cerca di associare ogni contatto a un Account** nel database usando:
   - **Match per dominio email**: Se l'email è `mario@azienda.com` e c'è un account con website `www.azienda.com`, vengono associati
   - **Match per nome azienda**: Se il contatto ha "Azienda SRL" come company e c'è un account "Azienda SRL", vengono associati
   - **Match fuzzy**: Confronta il dominio email con il nome dell'account (es. `info@azienda.com` -> account "Azienda")

4. **Crea o aggiorna i contatti** nel database:
   - Se il contatto esiste già (stessa email), viene aggiornato con i nuovi dati
   - Se il contatto non esiste, viene creato nuovo
   - Ogni contatto viene associato all'account trovato (se disponibile)

## Note Importanti

- **Ogni account può avere più contatti** (relazione uno-a-many)
- I contatti senza email vengono saltati
- I contatti senza account corrispondente vengono importati comunque, ma senza account associato
- Lo script usa l'utente di default del database come owner dei nuovi contatti

## Risoluzione Problemi

### Errore: "win32com non installato"
```bash
pip install pywin32
```

### Errore: "Outlook non trovato"
- Assicurati che Outlook sia installato
- Apri Outlook prima di eseguire lo script
- Verifica che Outlook sia configurato correttamente

### Nessun account associato
- Verifica che gli account nel database abbiano:
  - Nome azienda corretto
  - Website con dominio corrispondente alle email dei contatti
- Puoi associare manualmente i contatti agli account dopo l'importazione

# Istruzioni per Convertire PST a CSV e Importare Contatti

Questo metodo NON richiede Outlook e funziona con qualsiasi versione di Outlook.

## Prerequisiti

1. **WSL (Windows Subsystem for Linux) installato**
2. **Ubuntu installato in WSL**
3. **readpst installato in Ubuntu**

## Setup Iniziale (solo la prima volta)

### 1. Installa WSL e Ubuntu

Apri PowerShell come Amministratore e esegui:
```powershell
wsl --install
```

Riavvia il computer.

### 2. Installa Ubuntu dalla Microsoft Store

1. Apri Microsoft Store
2. Cerca "Ubuntu"
3. Installa l'ultima versione
4. Apri Ubuntu e configura username/password

### 3. Imposta Ubuntu come distribuzione predefinita

```powershell
wsl -s Ubuntu
```

### 4. Installa readpst in Ubuntu

Apri Ubuntu (WSL) e esegui:
```bash
sudo apt update
sudo apt upgrade
sudo apt install libpst-dev
sudo apt install pst-utils
```

### 5. Installa Python e librerie in Ubuntu

```bash
sudo apt install python3
sudo apt install python3-pip
pip3 install pandas
```

## Utilizzo

### 1. Copia il file PST nella directory home di Ubuntu

Il percorso è: `\\wsl$\Ubuntu\home\<tuo_username>\`

Oppure naviga da Esplora File: Linux > Ubuntu > home > <tuo_username>

### 2. Esegui lo script Python

```bash
python converti_pst_a_csv.py "C:\Users\user\OneDrive - ME.KO. Srl\Documenti\mail_inviata.pst"
```

Lo script:
1. Converte PST a MBOX usando `readpst` tramite WSL
2. Converte MBOX a CSV usando Python
3. Importa i contatti dal CSV nel database

## Output

- File MBOX: `pst_conversion/mbox_output/`
- File CSV: `pst_conversion/contatti_email.csv`
- Contatti importati nel database CRM

## Note

- Il processo può richiedere alcuni minuti per file PST grandi
- Assicurati che WSL sia attivo prima di eseguire lo script
- Il file PST può essere ovunque sul sistema Windows

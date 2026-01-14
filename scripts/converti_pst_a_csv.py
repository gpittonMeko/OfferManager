#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte file PST a CSV usando readpst (WSL/Ubuntu) e poi importa contatti
Questo script NON richiede Outlook

Uso:
    python3 converti_pst_a_csv.py "/mnt/c/Users/user/OneDrive - ME.KO. Srl/Documenti/mail_inviata.pst"
    
    oppure da Windows:
    python converti_pst_a_csv.py "C:/Users/user/OneDrive - ME.KO. Srl/Documenti/mail_inviata.pst"
"""
import sys
import os
import subprocess
from pathlib import Path
import re

# Rileva se siamo in WSL o Windows
IS_WSL = os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower()

# Percorso del progetto CRM (da Windows)
CRM_PROJECT_PATH = r"C:\Users\user\OneDrive - ME.KO. Srl\Documenti\Cursor\OfferManager"

# Se siamo in WSL, converti il percorso Windows in percorso WSL
if IS_WSL:
    if CRM_PROJECT_PATH[1] == ':':
        drive_letter = CRM_PROJECT_PATH[0].lower()
        path_part = CRM_PROJECT_PATH[2:].replace('\\', '/')
        CRM_PROJECT_PATH = f"/mnt/{drive_letter}{path_part}"

sys.path.insert(0, CRM_PROJECT_PATH)

try:
    from crm_app_completo import app, db, Account, Contact, User
except ImportError as e:
    print(f"❌ Errore importando moduli CRM: {e}")
    print(f"   Assicurati che il percorso del progetto sia corretto: {CRM_PROJECT_PATH}")
    sys.exit(1)

def parse_email_address(email_string):
    """Estrae email e nome da una stringa tipo 'Nome Cognome <email@domain.com>'"""
    if not email_string:
        return None, None
    
    # Pattern per "Nome Cognome <email@domain.com>" o solo "email@domain.com"
    match = re.match(r'^(.+?)\s*<(.+?)>$', email_string)
    if match:
        name = match.group(1).strip().strip('"\'')
        email = match.group(2).strip()
        return email, name
    
    # Se contiene solo email
    if '@' in email_string:
        email = email_string.strip().strip('<>"\'')
        return email, None
    
    return None, None

def extract_domain(email):
    """Estrae il dominio da un indirizzo email"""
    if not email or '@' not in email:
        return None
    return email.split('@')[1].lower()

def find_account_for_email(email, accounts):
    """Trova l'account più probabile per un'email"""
    if not email:
        return None
    
    from difflib import SequenceMatcher
    
    best_match = None
    best_score = 0.0
    
    email_domain = extract_domain(email)
    
    for account in accounts:
        score = 0.0
        
        # Match per dominio email vs website
        if email_domain and account.website:
            account_domain = extract_domain(account.website.replace('http://', '').replace('https://', '').replace('www.', ''))
            if account_domain and email_domain == account_domain:
                score = 1.0
            elif account_domain and email_domain and account_domain in email_domain:
                score = 0.8
        
        # Match per dominio email vs nome account
        if email_domain and account.name:
            domain_base = email_domain.split('.')[0]
            name_words = account.name.lower().split()
            if domain_base in name_words or any(word in domain_base for word in name_words if len(word) > 3):
                score = max(score, 0.7)
        
        if score > best_score and score >= 0.6:
            best_score = score
            best_match = account
    
    return best_match if best_score >= 0.6 else None

def windows_to_wsl_path(windows_path):
    """Converte un percorso Windows in percorso WSL"""
    path = windows_path.replace('\\', '/')
    if len(path) > 1 and path[1] == ':':
        drive_letter = path[0].lower()
        return f"/mnt/{drive_letter}{path[2:]}"
    return path

def convert_pst_to_mbox(pst_file_path, output_dir):
    """Converte PST a MBOX usando readpst (WSL/Ubuntu)"""
    print("=" * 80)
    print("CONVERSIONE PST A MBOX")
    print("=" * 80)
    print()
    
    print(f"📁 File PST: {pst_file_path}")
    print(f"📂 Directory output: {output_dir}")
    print()
    
    # Converti percorso se necessario
    if IS_WSL:
        # Se siamo già in WSL, converti percorso Windows in WSL
        pst_path = windows_to_wsl_path(pst_file_path) if ':' in pst_file_path else pst_file_path
        output_path = windows_to_wsl_path(output_dir) if ':' in output_dir else output_dir
    else:
        # Se siamo in Windows, converti per chiamare WSL
        pst_path = windows_to_wsl_path(pst_file_path)
        output_path = windows_to_wsl_path(output_dir)
    
    print(f"📁 Percorso PST: {pst_path}")
    print(f"📂 Percorso output: {output_path}")
    print()
    
    # Verifica che il file esista
    if not os.path.exists(pst_path):
        print(f"❌ Errore: File PST non trovato: {pst_path}")
        return None
    
    # Verifica dimensione file
    try:
        file_size = os.path.getsize(pst_path)
        print(f"📊 Dimensione file PST: {file_size / (1024*1024):.2f} MB")
        if file_size == 0:
            print("❌ Errore: Il file PST è vuoto!")
            return None
    except Exception as e:
        print(f"⚠️  Impossibile leggere la dimensione del file: {e}")
    
    # Crea directory output se non esiste
    os.makedirs(output_path, exist_ok=True)
    
    # Copia il file PST in una posizione temporanea senza spazi per evitare problemi
    # MA solo se non esiste già (per non sprecare spazio)
    import tempfile
    import shutil
    
    temp_pst_dir = os.path.join(os.path.dirname(output_path), 'temp_pst')
    os.makedirs(temp_pst_dir, exist_ok=True)
    temp_pst_file = os.path.join(temp_pst_dir, 'mail_inviata.pst')
    
    # Verifica se il file temporaneo esiste già e ha la stessa dimensione
    if os.path.exists(temp_pst_file):
        try:
            original_size = os.path.getsize(pst_path)
            temp_size = os.path.getsize(temp_pst_file)
            if original_size == temp_size:
                print(f"✅ File PST temporaneo già esistente (riuso, risparmio {original_size / (1024*1024):.2f} MB): {temp_pst_file}")
                pst_to_use = temp_pst_file
            else:
                print(f"📋 File PST temporaneo esistente ma dimensione diversa ({temp_size / (1024*1024):.2f} MB vs {original_size / (1024*1024):.2f} MB), ricopio...")
                shutil.copy2(pst_path, temp_pst_file)
                print(f"✅ File copiato: {temp_pst_file}")
                pst_to_use = temp_pst_file
        except Exception as e:
            print(f"⚠️  Errore verificando file temporaneo, ricopio: {e}")
            try:
                shutil.copy2(pst_path, temp_pst_file)
                print(f"✅ File copiato: {temp_pst_file}")
                pst_to_use = temp_pst_file
            except Exception as e2:
                print(f"⚠️  Impossibile copiare il file, uso il percorso originale: {e2}")
                pst_to_use = pst_path
    else:
        print(f"📋 Copiando PST in posizione temporanea (senza spazi)...")
        print(f"   Questo richiederà alcuni minuti per un file di {file_size / (1024*1024):.2f} MB...")
        try:
            shutil.copy2(pst_path, temp_pst_file)
            print(f"✅ File copiato: {temp_pst_file}")
            pst_to_use = temp_pst_file
        except Exception as e:
            print(f"⚠️  Impossibile copiare il file, uso il percorso originale: {e}")
            pst_to_use = pst_path
    
    # Esegui readpst con progresso
    print("🔄 Conversione PST a MBOX con readpst...")
    try:
        if IS_WSL:
            # Siamo già in WSL, chiama direttamente readpst con opzioni più permissive
            # -r = ricorsivo, -D = debug, -S = salta errori
            # RIMOSSO -M perché crea un file per ogni email invece di un singolo mbox
            cmd = ['readpst', '-r', '-D', '-S', '-o', output_path, pst_to_use]
        else:
            # Siamo in Windows, chiama tramite WSL
            cmd = ['wsl', 'readpst', '-r', '-D', '-S', '-o', output_path, pst_to_use]
        
        print(f"   Comando: {' '.join(cmd)}")
        print()
        
        # Avvia il processo
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Usa tqdm per mostrare progresso
        try:
            from tqdm import tqdm
            
            # Crea una barra di progresso indeterminata
            with tqdm(total=100, desc="   Convertendo PST", unit="%", bar_format='{l_bar}{bar}| {elapsed}<{remaining}') as pbar:
                import time
                start_time = time.time()
                elapsed = 0
                
                # Monitora il processo
                while process.poll() is None:
                    time.sleep(0.5)
                    elapsed = time.time() - start_time
                    # Aggiorna progresso basato sul tempo (stimato 5 minuti max)
                    estimated_total = 300  # 5 minuti
                    progress = min(95, int((elapsed / estimated_total) * 100))
                    pbar.n = progress
                    pbar.refresh()
                
                # Completa la barra
                pbar.n = 100
                pbar.refresh()
        except ImportError:
            # Se tqdm non è installato, mostra solo un messaggio
            print("   Conversione in corso... (installa tqdm per vedere il progresso: pip3 install tqdm)")
            process.wait()
        
        # Ottieni output
        stdout, _ = process.communicate()
        
        # NON pulire il file temporaneo - lo teniamo per riutilizzarlo in futuro
        # (risparmia spazio e tempo nelle esecuzioni successive)
        
        if process.returncode == 0:
            print("\n✅ Conversione completata!")
            if stdout:
                # Mostra solo le ultime righe dell'output per non intasare
                lines = stdout.strip().split('\n')
                if len(lines) > 10:
                    print("   ...")
                    for line in lines[-10:]:
                        print(f"   {line}")
                else:
                    print(stdout)
            return output_path if IS_WSL else output_dir
        else:
            print(f"\n❌ Errore nella conversione:")
            if stdout:
                print(stdout)
            print("\n💡 Suggerimenti:")
            print("   - Verifica che il file PST non sia corrotto")
            print("   - Assicurati che il file non sia aperto in Outlook")
            print("   - Prova a esportare il PST da Outlook in un formato più recente")
            return None
            
    except subprocess.TimeoutExpired:
        print("\n❌ Timeout: la conversione ha impiegato troppo tempo")
        return None
    except FileNotFoundError:
        print("\n❌ Errore: readpst non trovato!")
        print("   Installa con: sudo apt install pst-utils")
        return None
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return None

def convert_mbox_to_csv(mbox_file_path_or_dir, csv_file_path):
    """Converte MBOX a CSV - supporta sia un singolo file MBOX che una directory con più file MBOX"""
    print()
    print("=" * 80)
    print("CONVERSIONE MBOX A CSV")
    print("=" * 80)
    print()
    
    import mailbox
    
    print(f"📁 Input MBOX: {mbox_file_path_or_dir}")
    print(f"📄 File CSV output: {csv_file_path}")
    print()
    
    # Se è una directory, trova tutti i file MBOX
    mbox_files = []
    if os.path.isdir(mbox_file_path_or_dir):
        print(f"📂 Directory trovata, cerco tutti i file MBOX...")
        # Cerca nella cartella "Posta inviata" o "Sent Items"
        sent_folders = ['Posta inviata', 'Sent Items', 'Posta in uscita', 'Outbox']
        for sent_folder in sent_folders:
            sent_path = os.path.join(mbox_file_path_or_dir, sent_folder)
            if os.path.exists(sent_path):
                # Trova tutti i file numerici (sono i file MBOX individuali creati da readpst)
                # Escludi file con estensioni di immagini/allegati
                excluded_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar'}
                for file in os.listdir(sent_path):
                    file_path = os.path.join(sent_path, file)
                    if os.path.isfile(file_path) and not file.startswith('.'):
                        # Controlla se il file ha un'estensione esclusa
                        _, ext = os.path.splitext(file.lower())
                        if ext not in excluded_extensions:
                            mbox_files.append(file_path)
                if mbox_files:
                    print(f"✅ Trovati {len(mbox_files)} file potenziali email in: {sent_folder}")
                    break
        
        # Se non trovato, cerca ricorsivamente
        if not mbox_files:
            for root, dirs, files in os.walk(mbox_file_path_or_dir):
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            mbox_files.append(file_path)
            print(f"✅ Trovati {len(mbox_files)} file MBOX totali")
    else:
        # È un singolo file
        if os.path.exists(mbox_file_path_or_dir):
            mbox_files = [mbox_file_path_or_dir]
        else:
            print(f"❌ Errore: File MBOX non trovato: {mbox_file_path_or_dir}")
            return None
    
    if not mbox_files:
        print(f"❌ Errore: Nessun file MBOX trovato in: {mbox_file_path_or_dir}")
        return None
    
    try:
        import csv
        import email
        all_recipients = {}  # email -> {name, count}
        email_count = 0
        
        print(f"📧 Lettura email da {len(mbox_files)} file MBOX...")
        
        # Usa tqdm per mostrare progresso
        try:
            from tqdm import tqdm
            file_iterator = tqdm(mbox_files, desc="   Processando file MBOX", unit=" file")
        except ImportError:
            file_iterator = mbox_files
        
        for mbox_file in file_iterator:
            try:
                messages = []
                
                # Prova a leggere come mbox (file contenente più email)
                try:
                    mbox = mailbox.mbox(mbox_file)
                    messages = list(mbox)
                except:
                    # Se fallisce, potrebbe essere un file email singolo
                    try:
                        with open(mbox_file, 'rb') as f:
                            msg = email.message_from_bytes(f.read())
                            messages = [msg]
                    except:
                        # Prova come testo
                        try:
                            with open(mbox_file, 'r', encoding='utf-8', errors='ignore') as f:
                                msg = email.message_from_string(f.read())
                                messages = [msg]
                        except:
                            continue  # Salta questo file se non riesce a leggerlo
                
                # Processa tutti i messaggi trovati in questo file
                for message in messages:
                    try:
                        # Verifica che sia un messaggio email valido (deve avere almeno un campo header)
                        if not hasattr(message, 'get') or not message.get('From'):
                            continue
                        
                        email_count += 1
                        
                        # Estrai destinatari dal campo "To"
                        to_field = message.get('To', '') or ''
                        if to_field:
                            # Gestisci anche header multipli
                            if isinstance(to_field, list):
                                to_field = ', '.join(str(f) for f in to_field)
                            for email_str in re.split(r'[,;]', str(to_field)):
                                email_str = email_str.strip()
                                if email_str:
                                    email_addr, name = parse_email_address(email_str)
                                    if email_addr and '@' in email_addr:
                                        email_lower = email_addr.lower()
                                        if email_lower not in all_recipients:
                                            all_recipients[email_lower] = {
                                                'email': email_addr,
                                                'name': name or '',
                                                'count': 0
                                            }
                                        all_recipients[email_lower]['count'] += 1
                        
                        # Estrai destinatari dal campo "CC"
                        cc_field = message.get('CC', '') or ''
                        if cc_field:
                            if isinstance(cc_field, list):
                                cc_field = ', '.join(str(f) for f in cc_field)
                            for email_str in re.split(r'[,;]', str(cc_field)):
                                email_str = email_str.strip()
                                if email_str:
                                    email_addr, name = parse_email_address(email_str)
                                    if email_addr and '@' in email_addr:
                                        email_lower = email_addr.lower()
                                        if email_lower not in all_recipients:
                                            all_recipients[email_lower] = {
                                                'email': email_addr,
                                                'name': name or '',
                                                'count': 0
                                            }
                                        all_recipients[email_lower]['count'] += 1
                    except Exception as e:
                        # Salta questo messaggio se c'è un errore
                        continue
                    
            except Exception as e:
                # Salta questo file se c'è un errore
                continue
        
        print(f"\n✅ Email processate: {email_count}")
        print(f"✅ Destinatari unici trovati: {len(all_recipients)}")
        print()
        
        # Scrivi CSV
        print(f"📝 Scrittura CSV...")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Email', 'Nome', 'Numero Email'])
            
            for email_lower, data in all_recipients.items():
                writer.writerow([data['email'], data['name'], data['count']])
        
        print(f"✅ CSV creato: {csv_file_path}")
        return csv_file_path
        
    except Exception as e:
        print(f"❌ Errore convertendo MBOX a CSV: {e}")
        import traceback
        traceback.print_exc()
        return None

def import_contacts_from_csv(csv_file_path):
    """Importa contatti dal CSV nel database"""
    print()
    print("=" * 80)
    print("IMPORTAZIONE CONTATTI DA CSV")
    print("=" * 80)
    print()
    
    with app.app_context():
        # Ottieni utente default
        default_user = User.query.first()
        if not default_user:
            print("❌ Errore: Nessun utente trovato nel database!")
            return
        
        print(f"👤 Utente di default: {default_user.username}")
        
        # Carica account
        accounts = Account.query.all()
        print(f"📊 Account trovati: {len(accounts)}")
        print()
        
        import csv
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        print(f"📥 Importazione contatti da CSV...")
        
        # Conta righe totali per progresso
        total_rows = sum(1 for _ in open(csv_file_path, 'r', encoding='utf-8')) - 1  # -1 per header
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Usa tqdm per mostrare progresso
            try:
                from tqdm import tqdm
                iterator = tqdm(reader, desc="   Importando contatti", unit=" contatti", total=total_rows)
            except ImportError:
                iterator = reader
            
            for i, row in enumerate(iterator, 1):
                try:
                    email = row.get('Email', '').strip()
                    name = row.get('Nome', '').strip()
                    email_count = int(row.get('Numero Email', 0))
                    
                    if not email:
                        skipped_count += 1
                        continue
                    
                    # Estrai nome e cognome
                    first_name = ''
                    last_name = ''
                    if name:
                        name_parts = name.split(' ', 1)
                        if len(name_parts) == 2:
                            first_name = name_parts[0]
                            last_name = name_parts[1]
                        else:
                            first_name = name_parts[0]
                    
                    # Cerca account
                    account = find_account_for_email(email, accounts)
                    
                    # Cerca contatto esistente
                    existing_contact = Contact.query.filter_by(email=email).first()
                    
                    if existing_contact:
                        updated = False
                        if not existing_contact.first_name and first_name:
                            existing_contact.first_name = first_name
                            updated = True
                        if not existing_contact.last_name and last_name:
                            existing_contact.last_name = last_name
                            updated = True
                        if account and not existing_contact.account_id:
                            existing_contact.account_id = account.id
                            updated = True
                        
                        if updated:
                            db.session.add(existing_contact)
                            updated_count += 1
                            if updated_count <= 10:
                                print(f"   ✅ Aggiornato: {first_name} {last_name} ({email})")
                    else:
                        new_contact = Contact(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            account_id=account.id if account else None,
                            owner_id=default_user.id
                        )
                        db.session.add(new_contact)
                        imported_count += 1
                        if imported_count <= 10:
                            print(f"   ➕ Importato: {first_name} {last_name} ({email})")
                    
                    if (imported_count + updated_count) % 100 == 0:
                        db.session.commit()
                        
                except Exception as e:
                    skipped_count += 1
                    if skipped_count <= 10:
                        print(f"   ⚠️  Errore riga {i}: {e}")
                    continue
        
        db.session.commit()
        
        print()
        print("=" * 80)
        print("RIEPILOGO")
        print("=" * 80)
        print(f"✅ Contatti importati: {imported_count}")
        print(f"🔄 Contatti aggiornati: {updated_count}")
        print(f"⏭️  Contatti saltati: {skipped_count}")
        print()
        print("✅ Completato!")

def main():
    """Funzione principale"""
    # Percorso default PST
    if IS_WSL:
        pst_file = "/mnt/c/Users/user/OneDrive - ME.KO. Srl/Documenti/mail_inviata.pst"
    else:
        pst_file = r"C:\Users\user\OneDrive - ME.KO. Srl\Documenti\mail_inviata.pst"
    
    if len(sys.argv) > 1:
        pst_file = sys.argv[1]
        # Converti percorso Windows in WSL se necessario
        if IS_WSL and ':' in pst_file:
            pst_file = windows_to_wsl_path(pst_file)
    
    # Directory di lavoro (nella home di Ubuntu se siamo in WSL, altrimenti nella directory dello script)
    if IS_WSL:
        work_dir = os.path.join(os.path.expanduser('~'), 'pst_conversion')
    else:
        work_dir = os.path.join(os.path.dirname(__file__), 'pst_conversion')
    
    os.makedirs(work_dir, exist_ok=True)
    
    csv_file = os.path.join(work_dir, 'contatti_email.csv')
    output_dir = os.path.join(work_dir, 'mbox_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Se il CSV esiste già, importa direttamente senza riconvertire
    if os.path.exists(csv_file):
        print("=" * 80)
        print("CSV GIÀ ESISTENTE - IMPORT DIRETTO")
        print("=" * 80)
        print()
        print(f"📄 File CSV trovato: {csv_file}")
        print("   Importazione diretta senza riconversione...")
        print()
        import_contacts_from_csv(csv_file)
        return
    
    # Cerca se il file MBOX esiste già (per evitare di riconvertire)
    mbox_file = None
    sent_folders = ['Posta inviata', 'Sent Items', 'Posta in uscita', 'Outbox']
    for sent_folder in sent_folders:
        sent_path = os.path.join(output_dir, sent_folder)
        if os.path.exists(sent_path):
            mbox_path = os.path.join(sent_path, 'mbox')
            if os.path.exists(mbox_path):
                mbox_file = mbox_path
                break
    
    # Se non trovato, cerca ricorsivamente
    if not mbox_file:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file == 'mbox' or file.endswith('.mbox'):
                    mbox_file = os.path.join(root, file)
                    break
            if mbox_file:
                break
    
    # Se il MBOX esiste già, salta la conversione PST->MBOX
    if mbox_file and os.path.exists(mbox_file):
        print("=" * 80)
        print("MBOX GIÀ ESISTENTE - CONVERSIONE MBOX->CSV")
        print("=" * 80)
        print()
        print(f"📄 File MBOX trovato: {mbox_file}")
        print("   Salto conversione PST->MBOX, procedo direttamente a MBOX->CSV...")
        print()
    else:
        # Se arriviamo qui, dobbiamo convertire PST->MBOX
        print("=" * 80)
        print("CONVERSIONE NECESSARIA")
        print("=" * 80)
        print()
        print("⚠️  MBOX non trovato, avvio conversione PST -> MBOX...")
        print()
        
        # Step 1: Converti PST a MBOX
        mbox_output = convert_pst_to_mbox(pst_file, output_dir)
        if not mbox_output:
            print("❌ Errore nella conversione PST a MBOX")
            return
        
            # Step 2: Verifica se ci sono file nella directory (readpst crea file individuali)
        print(f"\n🔍 Verificando struttura in: {output_dir}")
        
        # Cerca nella cartella "Posta inviata" per vedere se ci sono file
        found_files = False
        for sent_folder in sent_folders:
            sent_path = os.path.join(output_dir, sent_folder)
            if os.path.exists(sent_path):
                files_in_sent = [f for f in os.listdir(sent_path) if os.path.isfile(os.path.join(sent_path, f)) and not f.startswith('.')]
                if files_in_sent:
                    print(f"✅ Trovati {len(files_in_sent)} file in: {sent_folder}")
                    found_files = True
                    break
        
        if not found_files:
            print("⚠️  Nessun file trovato nella cartella 'Posta inviata'")
            print("   Cerca ricorsivamente...")
            total_files = 0
            for root, dirs, files in os.walk(output_dir):
                file_count = len([f for f in files if not f.startswith('.')])
                total_files += file_count
            if total_files > 0:
                print(f"✅ Trovati {total_files} file totali nella struttura")
                found_files = True
        
        if not found_files:
            print("❌ Errore: Nessun file trovato nella directory MBOX")
            print(f"   Directory: {output_dir}")
            return
    
    # Step 3: Converti MBOX a CSV - passa sempre la directory
    csv_file = os.path.join(work_dir, 'contatti_email.csv')
    csv_result = convert_mbox_to_csv(output_dir, csv_file)
    if not csv_result:
        print("❌ Errore nella conversione MBOX a CSV")
        return
    
    # Step 4: Importa contatti dal CSV
    import_contacts_from_csv(csv_file)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

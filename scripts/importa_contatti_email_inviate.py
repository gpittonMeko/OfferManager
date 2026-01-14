#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti dalle email inviate in un file PST e li associa agli account nel database
Estrae i destinatari delle email e li crea come contatti
"""
import sys
import os
from pathlib import Path
from difflib import SequenceMatcher
import re

sys.path.insert(0, str(Path(__file__).parent))

try:
    import win32com.client
    import pythoncom
except ImportError:
    print("Errore: win32com non installato.")
    print("   Installa con: pip install pywin32")
    sys.exit(1)

from crm_app_completo import app, db, Account, Contact, User

def similarity(a, b):
    """Calcola similarità tra due stringhe (0-1)"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def extract_domain(email):
    """Estrae il dominio da un indirizzo email"""
    if not email or '@' not in email:
        return None
    return email.split('@')[1].lower()

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

def find_account_for_email(email, accounts):
    """
    Trova l'account più probabile per un'email
    Usa diversi criteri di matching
    """
    if not email:
        return None
    
    best_match = None
    best_score = 0.0
    
    # Estrai dominio email
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

def import_contacts_from_sent_emails(pst_file_path):
    """Importa contatti dalle email inviate in un file PST"""
    with app.app_context():
        print("=" * 80)
        print("IMPORTAZIONE CONTATTI DA EMAIL INVIATE (PST)")
        print("=" * 80)
        print()
        
        # Verifica che il file esista
        if not os.path.exists(pst_file_path):
            print(f"Errore: File PST non trovato: {pst_file_path}")
            return
        
        print(f"File PST: {pst_file_path}")
        print()
        
        # Ottieni il primo utente come owner di default
        default_user = User.query.first()
        if not default_user:
            print("Errore: Nessun utente trovato nel database!")
            return
        
        print(f"Utente di default: {default_user.username} ({default_user.first_name} {default_user.last_name})")
        print()
        
        # Carica tutti gli account
        accounts = Account.query.all()
        print(f"Account trovati nel database: {len(accounts)}")
        print()
        
        if len(accounts) == 0:
            print("Nessun account nel database. I contatti verranno importati senza account associato.")
        else:
            print("Account disponibili:")
            for acc in accounts[:10]:
                print(f"   - {acc.name} (ID: {acc.id})")
            if len(accounts) > 10:
                print(f"   ... e altri {len(accounts) - 10}")
        print()
        
        # Connetti a Outlook (usa istanza già aperta se possibile)
        print("Connessione a Outlook...")
        print("IMPORTANTE: Se appare una modale di login, COMPLETA IL LOGIN!")
        print("   Lo script aspetterà che tu finisca.")
        print()
        
        try:
            # Prova SOLO GetActiveObject per usare l'istanza già aperta di Outlook NUOVO
            # NON usare Dispatch che apre Outlook Classic
            outlook = None
            
            print("Cerco l'istanza di Outlook NUOVO già aperta...")
            print("IMPORTANTE: Assicurati che Outlook NUOVO sia già aperto!")
            print("   (NON Outlook Classic)")
            print()
            
            # Prova più volte GetActiveObject con un piccolo delay
            import time
            import subprocess
            
            # Verifica quale processo Outlook è in esecuzione
            print("Verifico quale Outlook è in esecuzione...")
            outlook_process_found = False
            try:
                # Cerca sia OUTLOOK.EXE che possibili nomi per Outlook nuovo
                result = subprocess.run(['tasklist', '/V'], capture_output=True, text=True, timeout=5)
                result_lower = result.stdout.lower()
                
                # Cerca vari nomi di processo Outlook
                outlook_names = ['outlook.exe', 'outlook', 'olk.exe', 'olk']
                found_name = None
                for name in outlook_names:
                    if name in result_lower:
                        found_name = name
                        print(f"✅ Processo Outlook trovato: {name}")
                        outlook_process_found = True
                        break
                
                if not outlook_process_found:
                    print("⚠️  Nessun processo Outlook trovato con tasklist")
                    print("   Verifica che Outlook sia effettivamente aperto")
            except Exception as e:
                print(f"⚠️  Errore verificando processi: {e}")
            
            # Prova diversi metodi per ottenere Outlook
            outlook = None
            
            # Metodo 1: GetActiveObject standard
            for attempt in range(10):
                try:
                    outlook = win32com.client.GetActiveObject("Outlook.Application")
                    
                    # Verifica che sia Outlook nuovo (non Classic)
                    try:
                        version = outlook.Version
                        print(f"✅ Outlook trovato! Versione: {version}")
                        # Outlook nuovo di solito ha versioni >= 16.0
                        version_major = float(version.split('.')[0])
                        if version_major >= 16:
                            print(f"✅ Sembra essere Outlook nuovo/moderno (v{version})")
                        else:
                            print(f"⚠️  Versione vecchia ({version}), potrebbe essere Classic")
                            print(f"   Se è Classic, chiudilo e apri Outlook NUOVO")
                    except:
                        pass
                    
                    print(f"✅ Outlook già aperto trovato con GetActiveObject! (tentativo {attempt + 1})")
                    break
                except:
                    if attempt < 9:
                        if attempt == 0:
                            print(f"Aspetto che Outlook si registri come COM object...")
                        elif attempt == 5:
                            print(f"Ancora in attesa...")
                        time.sleep(1)
            
            # Metodo 2: Se GetActiveObject fallisce, prova Dispatch comunque
            # Outlook nuovo potrebbe non registrarsi come COM object attivo,
            # ma Dispatch potrebbe comunque usare l'istanza esistente
            if not outlook:
                print("\n⚠️  GetActiveObject fallito")
                print("   Outlook nuovo potrebbe non registrarsi come COM object attivo")
                print("   Provo Dispatch (potrebbe usare l'istanza esistente)...")
                print("   Se appare una modale, completa il login!")
                
                import time
                time.sleep(2)  # Aspetta un po' prima di provare Dispatch
                
                try:
                    # Prova prima con il CLSID di Outlook nuovo (se disponibile)
                    # Outlook nuovo potrebbe avere un CLSID diverso
                    outlook = None
                    
                    # Metodo 1: Prova con il nome standard (potrebbe aprire Classic)
                    try:
                        outlook = win32com.client.Dispatch("Outlook.Application")
                        # Verifica subito la versione
                        try:
                            version = outlook.Version
                            version_major = float(version.split('.')[0])
                            if version_major < 16:
                                print(f"⚠️  Versione trovata: {version} - sembra essere Classic!")
                                print(f"   Chiudo questa istanza e provo un altro metodo...")
                                outlook = None
                                # Chiudi l'istanza Classic
                                try:
                                    outlook.Quit()
                                except:
                                    pass
                                outlook = None
                            else:
                                print(f"✅ Versione Outlook: {version} - sembra essere nuovo!")
                        except:
                            pass
                    except:
                        pass
                    
                    # Se non abbiamo trovato Outlook nuovo, prova altri metodi
                    if not outlook:
                        print("   Provo altri metodi per trovare Outlook nuovo...")
                        # Metodo 2: Prova con DispatchEx che potrebbe essere più selettivo
                        try:
                            outlook = win32com.client.DispatchEx("Outlook.Application")
                            print("✅ Outlook aperto tramite DispatchEx")
                        except:
                            # Metodo 3: Prova a cercare tra i processi e usare quello corretto
                            print("   Metodo alternativo fallito")
                            outlook = None
                    
                    if outlook:
                        # Aspetta che eventuali modali vengano gestite
                        time.sleep(3)
                        
                        # Verifica la versione finale
                        try:
                            version = outlook.Version
                            print(f"   Versione Outlook finale: {version}")
                            version_major = float(version.split('.')[0])
                            if version_major >= 16:
                                print(f"   ✅ Confermato: Outlook nuovo/moderno")
                            else:
                                print(f"   ⚠️  ATTENZIONE: Sembra essere Outlook Classic!")
                                print(f"   Chiudi Outlook Classic e apri Outlook NUOVO, poi riprova")
                        except:
                            pass
                except Exception as e:
                    print(f"   ❌ Dispatch fallito: {e}")
                    print("\n❌ ERRORE: Non riesco a trovare o aprire Outlook!")
                    print("   Per favore:")
                    print("   1. Assicurati che Outlook NUOVO sia aperto")
                    print("   2. Fai login se necessario")
                    print("   3. Aspetta qualche secondo che si carichi completamente")
                    print("   4. Poi esegui di nuovo questo script")
                    return
            
            if not outlook:
                print("\n❌ ERRORE: Outlook non disponibile")
                return
            
            if not outlook:
                print("Errore: Outlook non disponibile")
                return
            
            # Ottieni il namespace MAPI dall'istanza già aperta
            namespace = outlook.GetNamespace("MAPI")
            print("✅ Namespace MAPI ottenuto da Outlook NUOVO")
            
            # NON chiamare Logon() - usa il profilo già autenticato
            print("✅ Uso profilo già autenticato")
            
            # Verifica se il PST è già aggiunto
            import time
            pst_already_added = False
            pst_filename = os.path.basename(pst_file_path).replace('.pst', '')
            
            print(f"\nVerifico se il PST è già aggiunto...")
            for store in namespace.Stores:
                try:
                    store_name = store.DisplayName
                    if pst_filename.lower() in store_name.lower() or "file di dati" in store_name.lower():
                        pst_already_added = True
                        print(f"   PST già aggiunto: {store_name}")
                        break
                except:
                    pass
            
            # Aggiungi il PST solo se non è già aggiunto
            if not pst_already_added:
                print(f"\nAggiungo il file PST...")
                print("Se appare una modale, CHIUDILA SUBITO!")
                try:
                    namespace.AddStore(pst_file_path)
                    print(f"File PST aggiunto")
                    time.sleep(2)  # Aspetta che Outlook carichi il PST
                except Exception as e:
                    print(f"Errore aggiungendo PST: {e}")
                    print(f"Il file potrebbe essere già aperto o bloccato")
                    print(f"Provo comunque a cercare...")
            else:
                print(f"PST già disponibile, procedo...")
            
            # Trova la cartella "Posta inviata" e mostra tutte le cartelle disponibili
            sent_folder = None
            pst_folder = None
            
            print(f"\nCercando cartella Email Inviate...")
            print(f"Cartelle disponibili:")
            
            def explore_folder(folder, depth=0, max_depth=3):
                """Esplora ricorsivamente tutte le cartelle"""
                indent = "   " * (depth + 1)
                try:
                    folder_name = folder.Name
                    folder_lower = folder_name.lower()
                    
                    if depth == 0:
                        print(f"   {folder_name}")
                    else:
                        print(f"{indent}{folder_name}")
                    
                    # Conta email in questa cartella
                    try:
                        items_count = folder.Items.Count
                        if items_count > 0:
                            print(f"{indent}   -> {items_count} email trovate!")
                    except:
                        pass
                    
                    # Cerca nelle sottocartelle
                    if depth < max_depth:
                        try:
                            for subfolder in folder.Folders:
                                explore_folder(subfolder, depth + 1, max_depth)
                        except:
                            pass
                except Exception as e:
                    if depth == 0:
                        print(f"   Errore leggendo cartella: {e}")
            
            for folder in namespace.Folders:
                try:
                    folder_name = folder.Name
                    folder_lower = folder_name.lower()
                    
                    # Salta Leonardo
                    if "leonardo" in folder_lower or "furlan" in folder_lower:
                        print(f"   {folder_name} (Saltata - Leonardo)")
                        continue
                    
                    # Questo dovrebbe essere il PST
                    pst_folder = folder
                    print(f"\nEsplorando cartella PST: {folder_name}")
                    explore_folder(folder, depth=0, max_depth=2)
                    
                    # Cerca direttamente "Posta inviata"
                    try:
                        sent_folder = folder.Folders.Item("Posta inviata")
                        print(f"\n✅ CARTELLA TROVATA: Posta inviata")
                        break
                    except:
                        try:
                            sent_folder = folder.Folders.Item("Sent Items")
                            print(f"\n✅ CARTELLA TROVATA: Sent Items")
                            break
                        except:
                            # Cerca ricorsivamente
                            for subfolder in folder.Folders:
                                subfolder_name = subfolder.Name.lower()
                                if "inviata" in subfolder_name or "sent" in subfolder_name:
                                    sent_folder = subfolder
                                    print(f"\n✅ CARTELLA TROVATA: {subfolder.Name}")
                                    break
                            if sent_folder:
                                break
                except Exception as e:
                    print(f"   Errore leggendo cartella: {e}")
            
            if not sent_folder:
                print(f"\nErrore: Cartella Email Inviate non trovata nel file PST")
                return
            
            # Estrai email dalle email inviate
            print(f"\nLettura email inviate...")
            try:
                items = sent_folder.Items
                items.Sort("[ReceivedTime]", True)
                items_count = items.Count
                print(f"Email trovate nella cartella principale: {items_count}")
                
                # Cerca anche nelle sottocartelle
                total_items = items_count
                all_folders_to_check = [sent_folder]
                
                print(f"Cercando email nelle sottocartelle...")
                try:
                    for subfolder in sent_folder.Folders:
                        try:
                            sub_items = subfolder.Items
                            sub_count = sub_items.Count
                            if sub_count > 0:
                                print(f"   {subfolder.Name}: {sub_count} email")
                                all_folders_to_check.append(subfolder)
                                total_items += sub_count
                        except:
                            pass
                except:
                    pass
                
                print(f"Totale email trovate: {total_items}")
                
            except Exception as e:
                print(f"Errore leggendo email: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Anche se il conteggio dice 0, prova comunque a leggere
            all_recipients = {}
            print(f"\nEstrazione destinatari dalle email...")
            if total_items == 0:
                print(f"Conteggio dice 0, ma provo comunque a leggere le email...")
            
            email_processed = 0
            
            for folder_to_check in all_folders_to_check:
                try:
                    folder_items = folder_to_check.Items
                    folder_items.Sort("[ReceivedTime]", True)
                    folder_count = folder_items.Count
                    
                    print(f"\n   Processando cartella: {folder_to_check.Name} (conteggio: {folder_count})...")
                    
                    # Prova comunque a iterare anche se il conteggio è 0
                    # Usa un approccio diverso per iterare
                    try:
                        # Metodo 1: Prova GetFirst/GetNext
                        print(f"      Provo GetFirst()...")
                        try:
                            # Reset della collezione prima di GetFirst
                            folder_items.ResetColumns()
                            first_item = folder_items.GetFirst()
                            if first_item:
                                print(f"      ✅ Trovata prima email con GetFirst()!")
                                print(f"      Tipo oggetto: {type(first_item)}")
                                try:
                                    item_class = first_item.Class
                                    print(f"      Classe oggetto: {item_class}")
                                    # 43 = olMail (email)
                                    if item_class == 43:
                                        print(f"      ✅ È un messaggio email!")
                                except:
                                    pass
                                email_processed += 1
                                try:
                                    recipients = []
                                    
                                    # Estrai destinatari (To, CC, BCC)
                                    try:
                                        to_recipients = first_item.Recipients
                                        for recipient in to_recipients:
                                            try:
                                                email = recipient.AddressEntry.GetExchangeUser().PrimarySmtpAddress if hasattr(recipient.AddressEntry, 'GetExchangeUser') else recipient.Address
                                                name = recipient.Name
                                                if email and '@' in email:
                                                    recipients.append((email, name))
                                            except:
                                                pass
                                    except:
                                        # Prova metodo alternativo
                                        try:
                                            to_field = getattr(first_item, 'To', '') or ''
                                            if to_field:
                                                for email_str in re.split(r'[,;]', to_field):
                                                    email, name = parse_email_address(email_str.strip())
                                                    if email:
                                                        recipients.append((email, name))
                                        except:
                                            pass
                                    
                                    # CC
                                    try:
                                        cc_field = getattr(first_item, 'CC', '') or ''
                                        if cc_field:
                                            for email_str in re.split(r'[,;]', cc_field):
                                                email, name = parse_email_address(email_str.strip())
                                                if email:
                                                    recipients.append((email, name))
                                    except:
                                        pass
                                    
                                    # Aggiungi ai destinatari unici
                                    for email, name in recipients:
                                        email_lower = email.lower()
                                        if email_lower not in all_recipients:
                                            all_recipients[email_lower] = {
                                                'email': email,
                                                'name': name or '',
                                                'count': 0
                                            }
                                        all_recipients[email_lower]['count'] += 1
                                    
                                    # Continua con gli altri items
                                    while True:
                                        next_item = folder_items.GetNext()
                                        if not next_item:
                                            break
                                        email_processed += 1
                                        try:
                                            recipients = []
                                            
                                            # Estrai destinatari (To, CC, BCC)
                                            try:
                                                to_recipients = next_item.Recipients
                                                for recipient in to_recipients:
                                                    try:
                                                        email = recipient.AddressEntry.GetExchangeUser().PrimarySmtpAddress if hasattr(recipient.AddressEntry, 'GetExchangeUser') else recipient.Address
                                                        name = recipient.Name
                                                        if email and '@' in email:
                                                            recipients.append((email, name))
                                                    except:
                                                        pass
                                            except:
                                                # Prova metodo alternativo
                                                try:
                                                    to_field = getattr(next_item, 'To', '') or ''
                                                    if to_field:
                                                        for email_str in re.split(r'[,;]', to_field):
                                                            email, name = parse_email_address(email_str.strip())
                                                            if email:
                                                                recipients.append((email, name))
                                                except:
                                                    pass
                                            
                                            # CC
                                            try:
                                                cc_field = getattr(next_item, 'CC', '') or ''
                                                if cc_field:
                                                    for email_str in re.split(r'[,;]', cc_field):
                                                        email, name = parse_email_address(email_str.strip())
                                                        if email:
                                                            recipients.append((email, name))
                                            except:
                                                pass
                                            
                                            # Aggiungi ai destinatari unici
                                            for email, name in recipients:
                                                email_lower = email.lower()
                                                if email_lower not in all_recipients:
                                                    all_recipients[email_lower] = {
                                                        'email': email,
                                                        'name': name or '',
                                                        'count': 0
                                                    }
                                                all_recipients[email_lower]['count'] += 1
                                            
                                            if email_processed % 100 == 0:
                                                print(f"      Processate {email_processed} email...")
                                                
                                        except Exception as e:
                                            if email_processed <= 10:
                                                print(f"      Errore processando email {email_processed}: {e}")
                                            continue
                                except Exception as e:
                                    if email_processed <= 10:
                                        print(f"      Errore processando email {email_processed}: {e}")
                                    pass
                        except:
                            # Se GetFirst fallisce, prova con enumerate
                            for i, mail_item in enumerate(folder_items, 1):
                                email_processed += 1
                                try:
                                    recipients = []
                                    
                                    # Estrai destinatari (To, CC, BCC)
                                    try:
                                        to_recipients = mail_item.Recipients
                                        for recipient in to_recipients:
                                            try:
                                                email = recipient.AddressEntry.GetExchangeUser().PrimarySmtpAddress if hasattr(recipient.AddressEntry, 'GetExchangeUser') else recipient.Address
                                                name = recipient.Name
                                                if email and '@' in email:
                                                    recipients.append((email, name))
                                            except:
                                                pass
                                    except:
                                        # Prova metodo alternativo
                                        try:
                                            to_field = getattr(mail_item, 'To', '') or ''
                                            if to_field:
                                                for email_str in re.split(r'[,;]', to_field):
                                                    email, name = parse_email_address(email_str.strip())
                                                    if email:
                                                        recipients.append((email, name))
                                        except:
                                            pass
                                    
                                    # CC
                                    try:
                                        cc_field = getattr(mail_item, 'CC', '') or ''
                                        if cc_field:
                                            for email_str in re.split(r'[,;]', cc_field):
                                                email, name = parse_email_address(email_str.strip())
                                                if email:
                                                    recipients.append((email, name))
                                    except:
                                        pass
                                    
                                    # Aggiungi ai destinatari unici
                                    for email, name in recipients:
                                        email_lower = email.lower()
                                        if email_lower not in all_recipients:
                                            all_recipients[email_lower] = {
                                                'email': email,
                                                'name': name or '',
                                                'count': 0
                                            }
                                        all_recipients[email_lower]['count'] += 1
                                    
                                    if email_processed % 100 == 0:
                                        print(f"      Processate {email_processed} email...")
                                        
                                except Exception as e:
                                    if email_processed <= 10:
                                        print(f"      Errore processando email {email_processed}: {e}")
                                    continue
                    except StopIteration:
                        pass
                    except Exception as e:
                        print(f"   Errore iterando email: {e}")
                        pass
                except Exception as e:
                    print(f"   Errore processando cartella: {e}")
                    continue
            
            print(f"\nEmail processate: {email_processed}")
            print(f"Destinatari unici trovati: {len(all_recipients)}")
            
        except Exception as e:
            print(f"Errore nella connessione a Outlook o apertura PST: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Se non ci sono destinatari, esci
        if not all_recipients:
            print(f"\nNessun destinatario trovato")
            return
        
        # Importa contatti
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        matched_accounts = {}
        
        print("\nImportazione contatti...")
        print()
        
        for email_lower, recipient_data in all_recipients.items():
            try:
                email = recipient_data['email']
                name = recipient_data['name']
                email_count = recipient_data['count']
                
                # Estrai nome e cognome dal nome
                first_name = ''
                last_name = ''
                if name:
                    name_parts = name.strip().split(' ', 1)
                    if len(name_parts) == 2:
                        first_name = name_parts[0]
                        last_name = name_parts[1]
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]
                        last_name = ''
                
                # Se non c'è nome, usa l'email come fallback
                if not first_name and not last_name:
                    email_local = email.split('@')[0] if '@' in email else email
                    first_name = email_local
                    last_name = ''
                
                # Cerca account corrispondente
                account = find_account_for_email(email, accounts)
                
                # Cerca se il contatto esiste già (per email)
                existing_contact = Contact.query.filter_by(email=email).first()
                
                if existing_contact:
                    # Aggiorna contatto esistente
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
                        account_name = account.name if account else 'Nessuno'
                        if updated_count <= 10:
                            print(f"   Aggiornato: {first_name} {last_name} ({email}) -> Account: {account_name} ({email_count} email)")
                else:
                    # Crea nuovo contatto
                    new_contact = Contact(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        account_id=account.id if account else None,
                        owner_id=default_user.id
                    )
                    db.session.add(new_contact)
                    imported_count += 1
                    account_name = account.name if account else 'Nessuno'
                    if imported_count <= 10:
                        print(f"   Importato: {first_name} {last_name} ({email}) -> Account: {account_name} ({email_count} email)")
                
                # Traccia account associati
                if account:
                    if account.id not in matched_accounts:
                        matched_accounts[account.id] = []
                    matched_accounts[account.id].append(email)
                
            except Exception as e:
                print(f"   Errore processando contatto: {e}")
                skipped_count += 1
                continue
        
        # Commit delle modifiche
        print()
        print("Salvataggio nel database...")
        db.session.commit()
        
        print()
        print("=" * 80)
        print("RIEPILOGO IMPORTAZIONE")
        print("=" * 80)
        print(f"Contatti importati: {imported_count}")
        print(f"Contatti aggiornati: {updated_count}")
        print(f"Contatti saltati: {skipped_count}")
        print(f"Totale processati: {imported_count + updated_count + skipped_count}")
        print()
        
        if matched_accounts:
            print("Account associati:")
            for account_id, emails in matched_accounts.items():
                account = Account.query.get(account_id)
                if account:
                    print(f"   - {account.name}: {len(emails)} contatti")
        
        print()
        print("Importazione completata!")

if __name__ == '__main__':
    pst_file = r"C:\Users\user\OneDrive - ME.KO. Srl\Documenti\mail_inviata.pst"
    
    if len(sys.argv) > 1:
        pst_file = sys.argv[1]
    
    try:
        import_contacts_from_sent_emails(pst_file)
    except KeyboardInterrupt:
        print("\n\nOperazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

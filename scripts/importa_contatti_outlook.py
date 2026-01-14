#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti da Outlook e li associa agli account nel database
Usa win32com per accedere a Outlook su Windows
"""
import sys
import os
from pathlib import Path
import re
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent))

try:
    import win32com.client
except ImportError:
    print("❌ Errore: win32com non installato.")
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

def find_account_for_contact(outlook_contact, accounts):
    """
    Trova l'account più probabile per un contatto Outlook
    Usa diversi criteri di matching
    """
    contact_email = outlook_contact.get('Email1Address', '') or outlook_contact.get('EmailAddress', '')
    contact_company = outlook_contact.get('CompanyName', '') or outlook_contact.get('BusinessAddress', '')
    
    if not contact_email and not contact_company:
        return None
    
    best_match = None
    best_score = 0.0
    
    # Estrai dominio email
    email_domain = extract_domain(contact_email)
    
    for account in accounts:
        score = 0.0
        
        # Match per dominio email vs website
        if email_domain and account.website:
            account_domain = extract_domain(account.website.replace('http://', '').replace('https://', '').replace('www.', ''))
            if account_domain and email_domain == account_domain:
                score = 1.0
            elif account_domain and email_domain and account_domain in email_domain:
                score = 0.8
        
        # Match per nome azienda
        if contact_company and account.name:
            company_similarity = similarity(contact_company, account.name)
            if company_similarity > score:
                score = company_similarity
        
        # Match per dominio email vs nome account (es. info@azienda.com -> account "Azienda")
        if email_domain and account.name:
            domain_base = email_domain.split('.')[0]  # Prende solo la parte prima del primo punto
            name_words = account.name.lower().split()
            if domain_base in name_words or any(word in domain_base for word in name_words if len(word) > 3):
                score = max(score, 0.7)
        
        if score > best_score and score >= 0.6:  # Soglia minima di matching
            best_score = score
            best_match = account
    
    return best_match if best_score >= 0.6 else None

def import_outlook_contacts():
    """Importa contatti da Outlook e li associa agli account"""
    with app.app_context():
        print("=" * 80)
        print("IMPORTAZIONE CONTATTI DA OUTLOOK")
        print("=" * 80)
        print()
        
        # Ottieni il primo utente come owner di default
        default_user = User.query.first()
        if not default_user:
            print("❌ Errore: Nessun utente trovato nel database!")
            return
        
        print(f"👤 Utente di default: {default_user.username} ({default_user.first_name} {default_user.last_name})")
        print()
        
        # Carica tutti gli account
        accounts = Account.query.all()
        print(f"📊 Account trovati nel database: {len(accounts)}")
        print()
        
        if len(accounts) == 0:
            print("⚠️  Nessun account nel database. I contatti verranno importati senza account associato.")
        else:
            print("Account disponibili:")
            for acc in accounts[:10]:  # Mostra solo i primi 10
                print(f"   - {acc.name} (ID: {acc.id})")
            if len(accounts) > 10:
                print(f"   ... e altri {len(accounts) - 10}")
        print()
        
        # Connetti a Outlook
        print("🔌 Connessione a Outlook...")
        print("⚠️  IMPORTANTE: Se appare un dialogo di login, CHIUDILO o inserisci le credenziali di giovanni.pitton@mekosrl.it")
        print()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
            # Cerca l'account specifico - cerca "giovanni.pitton" (può essere @mekosrl.it o @outlook.com)
            target_email = "giovanni.pitton"
            print(f"🔍 Cercando account che contiene: {target_email}")
            
            # Cerca l'account specifico e il suo store
            contacts_folder = None
            # Cerca account che contiene "giovanni.pitton" (può essere @outlook.com o @mekosrl.it)
            target_email_patterns = ["giovanni.pitton", "giovanni.pitton@"]
            target_keywords = ["giovanni", "pitton"]
            
            print(f"\n   📋 Account disponibili in Outlook:")
            accounts_list = namespace.Accounts
            for account in accounts_list:
                try:
                    smtp = getattr(account, 'SmtpAddress', '') or ''
                    display_name = getattr(account, 'DisplayName', '') or ''
                    print(f"      - {display_name} ({smtp})")
                except:
                    pass
            
            print(f"\n   📦 Store disponibili in Outlook:")
            for store in namespace.Stores:
                try:
                    store_name = store.DisplayName
                    print(f"      📦 Store: {store_name}")
                except:
                    pass
            
            # Cerca PRIMA direttamente nelle cartelle principali (dove appare giovanni.pitton@mekosrl...)
            print(f"\n   🔍 Elencando TUTTE le cartelle principali...")
            
            def explore_folder(folder, depth=0, max_depth=3):
                """Esplora ricorsivamente tutte le cartelle"""
                indent = "   " * (depth + 1)
                try:
                    folder_name = folder.Name
                    folder_lower = folder_name.lower()
                    
                    # Stampa sempre le cartelle principali
                    if depth == 0:
                        print(f"      📂 {folder_name}")
                    else:
                        print(f"{indent}📁 {folder_name}")
                    
                    # Se contiene "giovanni" o "pitton", evidenzia
                    if any(pattern.lower() in folder_lower for pattern in target_email_patterns) or any(keyword in folder_lower for keyword in target_keywords):
                        print(f"{indent}   ⭐⭐ CARTELLA CORRISPONDENTE! ⭐⭐")
                    
                    # Cerca sottocartelle se non abbiamo raggiunto la profondità massima
                    if depth < max_depth:
                        try:
                            for subfolder in folder.Folders:
                                explore_folder(subfolder, depth + 1, max_depth)
                        except:
                            pass
                except Exception as e:
                    if depth == 0:
                        print(f"      ⚠️  Errore leggendo cartella: {e}")
            
            # Elenca tutte le cartelle principali e cerca quella di Giovanni
            giovanni_folder = None
            for folder in namespace.Folders:
                folder_name = folder.Name
                folder_lower = folder_name.lower()
                explore_folder(folder, depth=0, max_depth=2)
                
                # Se trova la cartella di Giovanni, salvala
                if "giovanni.pitton" in folder_lower or ("giovanni" in folder_lower and "pitton" in folder_lower):
                    giovanni_folder = folder
                    print(f"\n      ⭐⭐ CARTELLA DI GIOVANNI TROVATA: {folder_name} ⭐⭐")
            
            # Ora cerca la cartella contatti nella cartella di Giovanni
            print(f"\n   🔍 Cercando cartella contatti nella cartella di Giovanni...")
            if giovanni_folder:
                try:
                    for subfolder in giovanni_folder.Folders:
                        subfolder_name = subfolder.Name.lower()
                        print(f"      📁 Sottocartella: {subfolder.Name}")
                        if "contatti" in subfolder_name or "contacts" in subfolder_name:
                            contacts_folder = subfolder
                            print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: {subfolder.Name} ✅✅✅")
                            break
                except Exception as e:
                    print(f"      ⚠️  Errore cercando sottocartelle: {e}")
            
            # Se ancora non trovato, cerca in tutte le cartelle
            if not contacts_folder:
                print(f"\n   🔍 Cercando in tutte le cartelle...")
                for folder in namespace.Folders:
                    try:
                        folder_name = folder.Name
                        folder_lower = folder_name.lower()
                        
                        # Cerca cartelle che contengono "giovanni.pitton" o "giovanni" o "pitton"
                        if any(pattern.lower() in folder_lower for pattern in target_email_patterns) or any(keyword in folder_lower for keyword in target_keywords):
                            print(f"      ✅ Cartella corrispondente trovata: {folder_name}")
                            try:
                                # Cerca sottocartella "Contatti" o "Contacts"
                                for subfolder in folder.Folders:
                                    subfolder_name = subfolder.Name.lower()
                                    if "contatti" in subfolder_name or "contacts" in subfolder_name:
                                        contacts_folder = subfolder
                                        print(f"         ✅✅✅ CARTELLA CONTATTI TROVATA: {subfolder.Name} ✅✅✅")
                                        break
                            except Exception as e:
                                print(f"         ⚠️  Errore esplorando cartella: {e}")
                    except Exception as e:
                        print(f"      ⚠️  Errore leggendo cartella: {e}")
            
            # Fallback: cerca la cartella Contatti in qualsiasi cartella principale
            if not contacts_folder:
                print(f"\n   ⚠️  Non trovata cartella contatti specifica per giovanni.pitton")
                print(f"   🔍 Cercando cartella 'Contatti' in tutte le cartelle principali...")
                for folder in namespace.Folders:
                    try:
                        for subfolder in folder.Folders:
                            subfolder_name = subfolder.Name.lower()
                            if subfolder_name == "contatti" or subfolder_name == "contacts":
                                contacts_folder = subfolder
                                print(f"      ✅ Cartella Contatti trovata in: {folder.Name} -> {subfolder.Name}")
                                break
                        if contacts_folder:
                            break
                    except:
                        pass
                
                # Ultimo fallback: cartella di default
                if not contacts_folder:
                    print(f"   ⚠️  Uso cartella contatti di default")
                    contacts_folder = namespace.GetDefaultFolder(10)
            
            print(f"\n   ✅ Cartella contatti selezionata: {contacts_folder.Name}")
            
            # Raccogli contatti da tutte le cartelle (incluso sottocartelle)
            def get_all_contacts(folder):
                """Raccoglie tutti i contatti da una cartella e dalle sue sottocartelle"""
                contacts_list = []
                try:
                    # Aggiungi contatti della cartella corrente
                    items = folder.Items
                    for item in items:
                        try:
                            if hasattr(item, 'Class') and item.Class == 43:  # 43 = olContact
                                contacts_list.append(item)
                        except:
                            pass
                    
                    # Cerca nelle sottocartelle
                    try:
                        for subfolder in folder.Folders:
                            contacts_list.extend(get_all_contacts(subfolder))
                    except:
                        pass
                except Exception as e:
                    print(f"   ⚠️  Errore leggendo cartella: {e}")
                
                return contacts_list
            
            all_contacts = get_all_contacts(contacts_folder)
            
            print(f"✅ Connesso a Outlook!")
            print(f"📇 Contatti trovati in Outlook: {len(all_contacts)}")
            print()
            
        except Exception as e:
            print(f"❌ Errore nella connessione a Outlook: {e}")
            print("   Assicurati che Outlook sia installato e aperto.")
            return
        
        # Estrai contatti
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        matched_accounts = {}
        
        print("📥 Estrazione contatti da Outlook...")
        print()
        
        for i, contact_item in enumerate(all_contacts, 1):
            try:
                # Estrai dati dal contatto Outlook
                outlook_contact = {
                    'FirstName': getattr(contact_item, 'FirstName', '') or '',
                    'LastName': getattr(contact_item, 'LastName', '') or '',
                    'FullName': getattr(contact_item, 'FullName', '') or '',
                    'Email1Address': getattr(contact_item, 'Email1Address', '') or '',
                    'EmailAddress': getattr(contact_item, 'EmailAddress', '') or '',
                    'BusinessTelephoneNumber': getattr(contact_item, 'BusinessTelephoneNumber', '') or '',
                    'MobileTelephoneNumber': getattr(contact_item, 'MobileTelephoneNumber', '') or '',
                    'CompanyName': getattr(contact_item, 'CompanyName', '') or '',
                    'JobTitle': getattr(contact_item, 'JobTitle', '') or '',
                    'Department': getattr(contact_item, 'Department', '') or '',
                    'BusinessAddress': getattr(contact_item, 'BusinessAddress', '') or '',
                }
                
                # Prendi email principale
                email = outlook_contact['Email1Address'] or outlook_contact['EmailAddress']
                
                # Se non c'è email, salta
                if not email:
                    skipped_count += 1
                    continue
                
                # Prendi nome e cognome
                first_name = outlook_contact['FirstName']
                last_name = outlook_contact['LastName']
                
                # Se non ci sono nome/cognome ma c'è FullName, prova a dividerlo
                if not first_name and not last_name and outlook_contact['FullName']:
                    name_parts = outlook_contact['FullName'].strip().split(' ', 1)
                    if len(name_parts) == 2:
                        first_name = name_parts[0]
                        last_name = name_parts[1]
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]
                        last_name = ''
                
                # Se ancora non c'è nome, usa l'email come fallback
                if not first_name and not last_name:
                    email_local = email.split('@')[0] if '@' in email else email
                    first_name = email_local
                    last_name = ''
                
                # Prendi telefono (business o mobile)
                phone = outlook_contact['BusinessTelephoneNumber'] or outlook_contact['MobileTelephoneNumber']
                
                # Cerca account corrispondente
                account = find_account_for_contact(outlook_contact, accounts)
                
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
                    if not existing_contact.phone and phone:
                        existing_contact.phone = phone
                        updated = True
                    if not existing_contact.title and outlook_contact['JobTitle']:
                        existing_contact.title = outlook_contact['JobTitle']
                        updated = True
                    if not existing_contact.department and outlook_contact['Department']:
                        existing_contact.department = outlook_contact['Department']
                        updated = True
                    if account and not existing_contact.account_id:
                        existing_contact.account_id = account.id
                        updated = True
                    
                    if updated:
                        db.session.add(existing_contact)
                        updated_count += 1
                        account_name = account.name if account else 'Nessuno'
                        print(f"   ✅ Aggiornato: {first_name} {last_name} ({email}) -> Account: {account_name}")
                else:
                    # Crea nuovo contatto
                    new_contact = Contact(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        title=outlook_contact['JobTitle'],
                        department=outlook_contact['Department'],
                        account_id=account.id if account else None,
                        owner_id=default_user.id
                    )
                    db.session.add(new_contact)
                    imported_count += 1
                    account_name = account.name if account else 'Nessuno'
                    print(f"   ➕ Importato: {first_name} {last_name} ({email}) -> Account: {account_name}")
                
                # Traccia account associati
                if account:
                    if account.id not in matched_accounts:
                        matched_accounts[account.id] = []
                    matched_accounts[account.id].append(email)
                
            except Exception as e:
                print(f"   ⚠️  Errore processando contatto {i}: {e}")
                skipped_count += 1
                continue
        
        # Commit delle modifiche
        print()
        print("💾 Salvataggio nel database...")
        db.session.commit()
        
        print()
        print("=" * 80)
        print("RIEPILOGO IMPORTAZIONE")
        print("=" * 80)
        print(f"✅ Contatti importati: {imported_count}")
        print(f"🔄 Contatti aggiornati: {updated_count}")
        print(f"⏭️  Contatti saltati: {skipped_count}")
        print(f"📊 Totale processati: {imported_count + updated_count + skipped_count}")
        print()
        
        if matched_accounts:
            print("📋 Account associati:")
            for account_id, emails in matched_accounts.items():
                account = Account.query.get(account_id)
                if account:
                    print(f"   - {account.name}: {len(emails)} contatti")
        
        print()
        print("✅ Importazione completata!")

if __name__ == '__main__':
    try:
        import_outlook_contacts()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

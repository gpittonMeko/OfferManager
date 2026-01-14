#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti da un file PST di Outlook e li associa agli account nel database
Legge direttamente il file PST senza dover accedere al profilo di default
"""
import sys
import os
from pathlib import Path
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
    contact_company = outlook_contact.get('CompanyName', '') or ''
    
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

def import_contacts_from_pst(pst_file_path):
    """Importa contatti da un file PST"""
    with app.app_context():
        print("=" * 80)
        print("IMPORTAZIONE CONTATTI DA FILE PST")
        print("=" * 80)
        print()
        
        # Verifica che il file esista
        if not os.path.exists(pst_file_path):
            print(f"❌ Errore: File PST non trovato: {pst_file_path}")
            return
        
        print(f"📁 File PST: {pst_file_path}")
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
            for acc in accounts[:10]:
                print(f"   - {acc.name} (ID: {acc.id})")
            if len(accounts) > 10:
                print(f"   ... e altri {len(accounts) - 10}")
        print()
        
        # Connetti a Outlook e apri il file PST
        print("🔌 Connessione a Outlook...")
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
            # Aggiungi il file PST (se non è già aggiunto)
            print(f"📂 Apertura file PST...")
            try:
                # Prova ad aggiungere il file PST
                namespace.AddStore(pst_file_path)
                print(f"✅ File PST aggiunto a Outlook")
            except Exception as e:
                # Il file potrebbe essere già aggiunto
                print(f"⚠️  File PST potrebbe essere già aggiunto: {e}")
            
            # Cerca la cartella Contatti nel file PST
            contacts_folder = None
            
            # Cerca in tutte le cartelle disponibili
            print(f"\n🔍 Cercando cartella Contatti nel file PST...")
            print(f"   📋 Cartelle disponibili:")
            
            # Prima trova la cartella del PST (dovrebbe essere "File di dati di Outlook" o simile)
            pst_folder = None
            for folder in namespace.Folders:
                try:
                    folder_name = folder.Name
                    print(f"      📂 {folder_name}")
                    
                    # Cerca cartella che corrisponde al file PST
                    # Il PST viene aggiunto come "File di dati di Outlook" o con il nome del file
                    if "file di dati" in folder_name.lower() or "outlook data file" in folder_name.lower() or "giovanni.pitton" in folder_name.lower() or "giovanni" in folder_name.lower():
                        pst_folder = folder
                        print(f"         ⭐⭐ CARTELLA PST TROVATA: {folder_name} ⭐⭐")
                        
                        # Mostra tutte le sottocartelle
                        print(f"         📁 Sottocartelle disponibili:")
                        try:
                            for subfolder in folder.Folders:
                                print(f"            - {subfolder.Name}")
                        except:
                            pass
                except:
                    pass
            
            # Se trovata la cartella PST, cerca la sottocartella Contatti
            if pst_folder:
                print(f"\n   🔍 Cercando Contatti nella cartella PST...")
                try:
                    # Prova "Contatti" (italiano)
                    try:
                        contacts_folder = pst_folder.Folders.Item("Contatti")
                        print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: Contatti ✅✅✅")
                    except:
                        # Prova "Contacts" (inglese)
                        try:
                            contacts_folder = pst_folder.Folders.Item("Contacts")
                            print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: Contacts ✅✅✅")
                        except:
                            # Cerca ricorsivamente
                            print(f"      🔍 Cercando ricorsivamente...")
                            for subfolder in pst_folder.Folders:
                                subfolder_name = subfolder.Name.lower()
                                print(f"         📁 {subfolder.Name}")
                                if "contatti" in subfolder_name or "contacts" in subfolder_name:
                                    contacts_folder = subfolder
                                    print(f"         ✅✅✅ CARTELLA CONTATTI TROVATA: {subfolder.Name} ✅✅✅")
                                    break
                except Exception as e:
                    print(f"      ⚠️  Errore cercando Contatti: {e}")
            
            # Se ancora non trovato, cerca in tutte le cartelle
            if not contacts_folder:
                print(f"\n   🔍 Cercando in tutte le cartelle...")
                for folder in namespace.Folders:
                    try:
                        folder_name = folder.Name
                        # Cerca la cartella Contatti
                        try:
                            contacts_subfolder = folder.Folders.Item("Contatti")
                            contacts_folder = contacts_subfolder
                            print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: {folder_name} -> Contatti ✅✅✅")
                            break
                        except:
                            try:
                                contacts_subfolder = folder.Folders.Item("Contacts")
                                contacts_folder = contacts_subfolder
                                print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: {folder_name} -> Contacts ✅✅✅")
                                break
                            except:
                                pass
                        
                        # Cerca ricorsivamente
                        try:
                            for subfolder in folder.Folders:
                                subfolder_name = subfolder.Name.lower()
                                if "contatti" in subfolder_name or "contacts" in subfolder_name:
                                    contacts_folder = subfolder
                                    print(f"      ✅✅✅ CARTELLA CONTATTI TROVATA: {folder_name} -> {subfolder.Name} ✅✅✅")
                                    break
                            if contacts_folder:
                                break
                        except:
                            pass
                    except Exception as e:
                        print(f"      ⚠️  Errore leggendo cartella: {e}")
            
            if not contacts_folder:
                print(f"\n❌ Errore: Cartella Contatti non trovata nel file PST")
                print(f"   Verifica che il file PST contenga una cartella 'Contatti' o 'Contacts'")
                return
            
            # Mostra informazioni sulla cartella Contatti
            print(f"\n📊 Informazioni cartella Contatti:")
            try:
                items_count = contacts_folder.Items.Count
                print(f"   📇 Numero di items nella cartella: {items_count}")
                
                # Mostra sottocartelle se ci sono
                try:
                    subfolders_count = contacts_folder.Folders.Count
                    print(f"   📁 Numero di sottocartelle: {subfolders_count}")
                    if subfolders_count > 0:
                        print(f"   📁 Sottocartelle:")
                        for subfolder in contacts_folder.Folders:
                            print(f"      - {subfolder.Name} ({subfolder.Items.Count} items)")
                except:
                    pass
            except Exception as e:
                print(f"   ⚠️  Errore leggendo informazioni: {e}")
            
            # Raccogli contatti da tutte le cartelle (incluso sottocartelle)
            def get_all_contacts(folder, depth=0):
                """Raccoglie tutti i contatti da una cartella e dalle sue sottocartelle"""
                contacts_list = []
                indent = "   " * (depth + 1)
                try:
                    # Aggiungi contatti della cartella corrente
                    items = folder.Items
                    items_count = items.Count
                    if depth == 0:
                        print(f"\n📥 Estrazione contatti da: {folder.Name} ({items_count} items)")
                    
                    for i, item in enumerate(items, 1):
                        try:
                            item_class = getattr(item, 'Class', None)
                            if item_class == 43:  # 43 = olContact
                                contacts_list.append(item)
                                if depth == 0 and len(contacts_list) <= 5:
                                    email = getattr(item, 'Email1Address', '') or getattr(item, 'EmailAddress', '')
                                    name = getattr(item, 'FullName', '') or f"{getattr(item, 'FirstName', '')} {getattr(item, 'LastName', '')}"
                                    print(f"   ✅ Contatto {len(contacts_list)}: {name} ({email})")
                        except Exception as e:
                            if depth == 0:
                                print(f"   ⚠️  Errore leggendo item {i}: {e}")
                    
                    # Cerca nelle sottocartelle
                    try:
                        for subfolder in folder.Folders:
                            if depth == 0:
                                print(f"\n📁 Cercando in sottocartella: {subfolder.Name}")
                            subfolder_contacts = get_all_contacts(subfolder, depth + 1)
                            contacts_list.extend(subfolder_contacts)
                    except Exception as e:
                        if depth == 0:
                            print(f"   ⚠️  Errore cercando sottocartelle: {e}")
                except Exception as e:
                    print(f"   ⚠️  Errore leggendo cartella: {e}")
                
                return contacts_list
            
            all_contacts = get_all_contacts(contacts_folder)
            
            print(f"\n✅ File PST aperto!")
            print(f"📇 Contatti trovati nel PST: {len(all_contacts)}")
            print()
            
        except Exception as e:
            print(f"❌ Errore nella connessione a Outlook o apertura PST: {e}")
            import traceback
            traceback.print_exc()
            print("\n💡 SUGGERIMENTO: Assicurati che:")
            print("   - Outlook sia installato")
            print("   - Il file PST non sia già aperto in Outlook")
            print("   - Il percorso del file sia corretto")
            return
        
        # Estrai contatti
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        matched_accounts = {}
        
        print("📥 Estrazione contatti dal PST...")
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
                        if updated_count <= 10:
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
                    if imported_count <= 10:
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
        
        # Rimuovi il file PST da Outlook (opzionale)
        try:
            namespace.RemoveStore(contacts_folder.Parent.StoreID)
            print("📂 File PST rimosso da Outlook")
        except:
            pass

if __name__ == '__main__':
    pst_file = r"C:\Users\user\OneDrive - ME.KO. Srl\Documenti\giovanni.pitton@mekosrl.it.pst"
    
    if len(sys.argv) > 1:
        pst_file = sys.argv[1]
    
    try:
        import_contacts_from_pst(pst_file)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti da un file CSV esportato da Outlook e li associa agli account nel database
"""
import sys
import os
import csv
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent))

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

def find_account_for_contact(contact_data, accounts):
    """
    Trova l'account più probabile per un contatto
    Usa diversi criteri di matching
    """
    contact_email = contact_data.get('Email Address', '') or contact_data.get('E-mail', '') or contact_data.get('Email', '')
    contact_company = contact_data.get('Company', '') or contact_data.get('Company Name', '')
    
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

def import_contacts_from_csv(csv_file_path):
    """Importa contatti da un file CSV"""
    with app.app_context():
        print("=" * 80)
        print("IMPORTAZIONE CONTATTI DA CSV")
        print("=" * 80)
        print()
        
        # Verifica che il file esista
        if not os.path.exists(csv_file_path):
            print(f"❌ Errore: File non trovato: {csv_file_path}")
            print("\n📋 ISTRUZIONI PER ESPORTARE CONTATTI DA OUTLOOK:")
            print("   1. Apri Outlook")
            print("   2. Vai su File > Apri ed esporta > Importa/Esporta")
            print("   3. Seleziona 'Esporta in un file' > Avanti")
            print("   4. Seleziona 'Valori separati da virgola (CSV)' > Avanti")
            print("   5. Seleziona la cartella 'Contatti' > Avanti")
            print("   6. Scegli dove salvare il file e salvalo come 'contatti_outlook.csv'")
            print("   7. Esegui di nuovo questo script con il percorso del file")
            return
        
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
        
        # Leggi il file CSV
        print(f"📥 Lettura file CSV: {csv_file_path}")
        print()
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        matched_accounts = {}
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                # Prova a rilevare il delimitatore
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Normalizza i nomi delle colonne (Outlook può usare nomi diversi)
                fieldnames = [f.lower().strip() for f in reader.fieldnames] if reader.fieldnames else []
                
                print(f"📋 Colonne trovate nel CSV: {', '.join(fieldnames[:10])}")
                if len(fieldnames) > 10:
                    print(f"   ... e altre {len(fieldnames) - 10} colonne")
                print()
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Normalizza i valori del dizionario
                        contact_data = {k.lower().strip(): v for k, v in row.items() if v}
                        
                        # Estrai email (prova diversi nomi di colonna)
                        email = (contact_data.get('email address', '') or 
                                contact_data.get('e-mail', '') or 
                                contact_data.get('email', '') or 
                                contact_data.get('e-mail address', '') or '').strip()
                        
                        if not email:
                            skipped_count += 1
                            continue
                        
                        # Estrai nome e cognome
                        first_name = (contact_data.get('first name', '') or 
                                     contact_data.get('nome', '') or '').strip()
                        last_name = (contact_data.get('last name', '') or 
                                    contact_data.get('cognome', '') or '').strip()
                        
                        # Se non ci sono nome/cognome ma c'è "Full Name" o "Nome completo"
                        if not first_name and not last_name:
                            full_name = (contact_data.get('full name', '') or 
                                        contact_data.get('nome completo', '') or '').strip()
                            if full_name:
                                name_parts = full_name.split(' ', 1)
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
                        
                        # Estrai altri dati
                        phone = (contact_data.get('business phone', '') or 
                                contact_data.get('mobile phone', '') or 
                                contact_data.get('phone', '') or 
                                contact_data.get('telefono', '') or '').strip()
                        
                        title = (contact_data.get('job title', '') or 
                                contact_data.get('title', '') or 
                                contact_data.get('titolo', '') or '').strip()
                        
                        department = (contact_data.get('department', '') or 
                                     contact_data.get('dipartimento', '') or '').strip()
                        
                        company = (contact_data.get('company', '') or 
                                  contact_data.get('company name', '') or 
                                  contact_data.get('azienda', '') or '').strip()
                        
                        # Cerca account corrispondente
                        account = find_account_for_contact({
                            'Email Address': email,
                            'Company': company
                        }, accounts)
                        
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
                            if not existing_contact.title and title:
                                existing_contact.title = title
                                updated = True
                            if not existing_contact.department and department:
                                existing_contact.department = department
                                updated = True
                            if account and not existing_contact.account_id:
                                existing_contact.account_id = account.id
                                updated = True
                            
                            if updated:
                                db.session.add(existing_contact)
                                updated_count += 1
                                account_name = account.name if account else 'Nessuno'
                                if updated_count <= 10:  # Mostra solo i primi 10
                                    print(f"   ✅ Aggiornato: {first_name} {last_name} ({email}) -> Account: {account_name}")
                        else:
                            # Crea nuovo contatto
                            new_contact = Contact(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone,
                                title=title,
                                department=department,
                                account_id=account.id if account else None,
                                owner_id=default_user.id
                            )
                            db.session.add(new_contact)
                            imported_count += 1
                            account_name = account.name if account else 'Nessuno'
                            if imported_count <= 10:  # Mostra solo i primi 10
                                print(f"   ➕ Importato: {first_name} {last_name} ({email}) -> Account: {account_name}")
                        
                        # Traccia account associati
                        if account:
                            if account.id not in matched_accounts:
                                matched_accounts[account.id] = []
                            matched_accounts[account.id].append(email)
                        
                    except Exception as e:
                        print(f"   ⚠️  Errore processando riga {row_num}: {e}")
                        skipped_count += 1
                        continue
        
        except Exception as e:
            print(f"❌ Errore leggendo file CSV: {e}")
            import traceback
            traceback.print_exc()
            return
        
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
    if len(sys.argv) < 2:
        print("=" * 80)
        print("IMPORTAZIONE CONTATTI DA CSV")
        print("=" * 80)
        print()
        print("📋 USO:")
        print("   python importa_contatti_csv.py <percorso_file_csv>")
        print()
        print("📋 ISTRUZIONI PER ESPORTARE CONTATTI DA OUTLOOK:")
        print("   1. Apri Outlook")
        print("   2. Vai su File > Apri ed esporta > Importa/Esporta")
        print("   3. Seleziona 'Esporta in un file' > Avanti")
        print("   4. Seleziona 'Valori separati da virgola (CSV)' > Avanti")
        print("   5. Seleziona la cartella 'Contatti' (o la cartella di giovanni.pitton@mekosrl.it)")
        print("   6. Scegli dove salvare il file (es. C:\\Users\\user\\Desktop\\contatti_outlook.csv)")
        print("   7. Esegui: python importa_contatti_csv.py C:\\Users\\user\\Desktop\\contatti_outlook.csv")
        print()
        sys.exit(1)
    
    csv_file = sys.argv[1]
    try:
        import_contacts_from_csv(csv_file)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

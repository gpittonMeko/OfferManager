#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizza offerte dalla cartella Windows K:\OFFERTE - K\OFFERTE 2025
Crea leads, accounts e opportunità basate sulle offerte trovate
"""
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Aggiungi il path del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import db, app, Lead, Account, Opportunity, User, OfferDocument, extract_offer_amount_from_file

# Cartella da sincronizzare
# Su Windows: K:\OFFERTE - K\OFFERTE 2025 - K
# Su Linux (EC2): usa la cartella copiata localmente
import platform
if platform.system() == 'Windows':
    OFFERS_FOLDER = r"K:\OFFERTE - K\OFFERTE 2025 - K"
else:
    # Su Linux (EC2), usa la cartella copiata localmente
    # Prima prova la cartella copiata, poi fallback a mount o offerte_generate
    base_dir = os.path.dirname(os.path.abspath(__file__))
    offers_backup = os.path.join(base_dir, 'offerte_2025_backup')
    offers_mount = os.environ.get('OFFERS_FOLDER', '/mnt/k/OFFERTE - K/OFFERTE 2025 - K')
    offers_generate = os.path.join(base_dir, 'offerte_generate')
    
    # Priorità: 1) offerte_2025_backup, 2) mount, 3) offerte_generate
    if os.path.exists(offers_backup):
        OFFERS_FOLDER = offers_backup
    elif os.path.exists(offers_mount):
        OFFERS_FOLDER = offers_mount
    else:
        OFFERS_FOLDER = offers_generate
        os.makedirs(offers_generate, exist_ok=True)

# Pattern per estrarre informazioni dalle offerte
# Esempio: "OFFERTA_12345_ClienteSrl_2025.docx"
OFFER_PATTERN = re.compile(r'OFFERTA[_\s]*(\d+)[_\s]*(.+?)[_\s]*(\d{4})', re.IGNORECASE)

def extract_offer_info(filename):
    """Estrae informazioni dal nome del file offerta
    Supporta formati:
    - K####-YY - CLIENTE - PRODOTTO - DD-MM-YYYY
    - OFFERTA_12345_ClienteSrl_2025
    - ClienteSrl_12345
    """
    # Rimuovi estensione
    name = os.path.splitext(filename)[0]
    
    # Pattern 1: K####-YY - CLIENTE - PRODOTTO - DD-MM-YYYY (formato standard)
    k_pattern = re.compile(r'K(\d{4})-(\d{2})\s*-\s*(.+?)\s*-\s*(.+?)\s*-\s*(\d{2}-\d{2}-\d{4})', re.IGNORECASE)
    match = k_pattern.search(name)
    if match:
        offer_number = f"K{match.group(1)}-{match.group(2)}"
        client_name = match.group(3).strip()
        product = match.group(4).strip()
        date_str = match.group(5)
        return {
            'offer_number': offer_number,
            'client_name': client_name,
            'product': product,
            'date': date_str,
            'year': match.group(2),
            'filename': filename
        }
    
    # Pattern 2: OFFERTA_12345_ClienteSrl_2025
    match = OFFER_PATTERN.search(name)
    if match:
        offer_number = match.group(1)
        client_name = match.group(2).strip()
        year = match.group(3)
        return {
            'offer_number': offer_number,
            'client_name': client_name,
            'year': year,
            'filename': filename
        }
    
    # Pattern 3: K####-YY (solo numero offerta)
    k_simple = re.compile(r'K(\d{4})-(\d{2})', re.IGNORECASE)
    match = k_simple.search(name)
    if match:
        offer_number = f"K{match.group(1)}-{match.group(2)}"
        # Cerca nome cliente dopo il numero
        rest = name[match.end():].strip()
        if rest.startswith('-'):
            rest = rest[1:].strip()
        parts = rest.split(' - ')
        client_name = parts[0].strip() if parts else 'Cliente Sconosciuto'
        return {
            'offer_number': offer_number,
            'client_name': client_name,
            'year': match.group(2),
            'filename': filename
        }
    
    # Pattern 4: cerca numero offerta e nome cliente
    # Es: "12345_ClienteSrl" o "ClienteSrl_12345"
    parts = re.split(r'[_\s-]+', name)
    if len(parts) >= 2:
        # Cerca un numero (probabilmente il numero offerta)
        numbers = [p for p in parts if p.isdigit() and len(p) >= 3]
        if numbers:
            offer_number = numbers[0]
            # Il resto è il nome cliente
            client_parts = [p for p in parts if not p.isdigit() and p.lower() not in ['offerta', 'offer', 'k']]
            client_name = ' '.join(client_parts) if client_parts else 'Cliente Sconosciuto'
            return {
                'offer_number': offer_number,
                'client_name': client_name,
                'year': str(datetime.now().year),
                'filename': filename
            }
    
    # Fallback: usa il nome del file come nome cliente
    return {
        'offer_number': None,
        'client_name': name.replace('_', ' ').replace('-', ' ').title(),
        'year': str(datetime.now().year),
        'filename': filename
    }

def determine_supplier_category(filename, content_hint=None):
    """Determina la categoria fornitore basandosi sul nome file o contenuto"""
    filename_lower = filename.lower()
    
    if 'unitree' in filename_lower or 'g1' in filename_lower or 'go2' in filename_lower or 'b2' in filename_lower:
        return 'Unitree'
    elif 'mir' in filename_lower or 'mobile' in filename_lower:
        return 'MiR'
    elif 'ur' in filename_lower or 'universal' in filename_lower or 'robot' in filename_lower:
        return 'Universal Robots'
    elif 'service' in filename_lower or 'servizi' in filename_lower:
        return 'Servizi'
    else:
        return 'Altri Fornitori'

def sync_offers():
    """Sincronizza offerte dalla cartella"""
    import logging
    logger = logging.getLogger(__name__)
    
    print(f"🔍 Verifica cartella: {OFFERS_FOLDER}")
    logger.info(f"🔍 Verifica cartella: {OFFERS_FOLDER}")
    
    if not os.path.exists(OFFERS_FOLDER):
        error_msg = f"❌ Cartella non trovata: {OFFERS_FOLDER}"
        print(error_msg)
        logger.error(error_msg)
        print(f"💡 Suggerimento: Verifica che la cartella K:\\ sia montata/accessibile")
        raise Exception(f"Cartella non trovata: {OFFERS_FOLDER}")
    
    print(f"📂 Sincronizzazione offerte da: {OFFERS_FOLDER}")
    
    with app.app_context():
        # Ottieni admin user ID come default owner
        # Usa query SQL diretta per evitare problemi con colonne mancanti nel modello
        from sqlalchemy import text
        
        admin_user_id = None
        result = db.session.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1"))
        admin_row = result.fetchone()
        if admin_row:
            admin_user_id = admin_row[0]
        else:
            # Prova a prendere il primo utente disponibile
            result = db.session.execute(text("SELECT id FROM users LIMIT 1"))
            first_user_row = result.fetchone()
            if first_user_row:
                admin_user_id = first_user_row[0]
                print(f"⚠️  Utente admin non trovato, usando il primo utente disponibile (ID: {admin_user_id})")
            else:
                print("❌ Nessun utente trovato nel database")
                return
        
        if not admin_user_id:
            print("❌ Impossibile recuperare un utente")
            return
        
        # Estensioni file offerte
        offer_extensions = ['.docx', '.pdf', '.doc']
        
        # Raccogli tutti i file offerte
        all_offer_files = []
        for root, dirs, files in os.walk(OFFERS_FOLDER):
            for file in files:
                if any(file.lower().endswith(ext) for ext in offer_extensions):
                    all_offer_files.append(os.path.join(root, file))
        
        print(f"📄 Trovati {len(all_offer_files)} file offerte totali")
        
        # Raggruppa per cartella fisica (ogni cartella = una offerta base)
        # Es: cartella "K2160 - CLIENTE - PRODOTTO" contiene K2160, K2161, K2162, K2163
        # Prendi solo l'ultima offerta (numero più alto) di ogni cartella
        offer_groups = {}  # {folder_path: [list of files]}
        
        for file_path in all_offer_files:
            filename = os.path.basename(file_path)
            dir_path = os.path.dirname(file_path)
            
            # Usa il percorso della cartella come chiave (normalizzato)
            # Se il file è nella root, usa il filename come cartella
            if dir_path == OFFERS_FOLDER or dir_path == os.path.normpath(OFFERS_FOLDER):
                # File nella root: usa il nome del file per raggruppare
                # Estrai numero base dal filename
                offer_info = extract_offer_info(filename)
                offer_number = offer_info.get('offer_number', '')
                if offer_number:
                    match = re.search(r'K(\d{4})', offer_number, re.IGNORECASE)
                    if match:
                        num = int(match.group(1))
                        folder_key = f"K{num // 10 * 10:04d}"  # Arrotonda alle decine
                    else:
                        folder_key = 'ROOT_' + os.path.splitext(filename)[0][:20]
                else:
                    folder_key = 'ROOT_' + os.path.splitext(filename)[0][:20]
            else:
                # File in una sottocartella: usa il nome della cartella
                folder_key = os.path.basename(dir_path)
            
            if folder_key not in offer_groups:
                offer_groups[folder_key] = []
            
            # Estrai numero offerta per ordinamento
            offer_info = extract_offer_info(filename)
            offer_number = offer_info.get('offer_number', '')
            number_value = 0
            if offer_number:
                match = re.search(r'K(\d{4})', offer_number, re.IGNORECASE)
                if match:
                    number_value = int(match.group(1))
                else:
                    # Prova a estrarre qualsiasi numero
                    num_match = re.search(r'\d{3,}', offer_number)
                    if num_match:
                        number_value = int(num_match.group())
            
            offer_groups[folder_key].append({
                'path': file_path,
                'filename': filename,
                'offer_number': offer_number,
                'number_value': number_value
            })
        
        # Per ogni gruppo, prendi solo l'ultima offerta (numero più alto)
        offer_files = []
        for base_folder, files in offer_groups.items():
            # Ordina per numero offerta (decrescente)
            files_sorted = sorted(files, key=lambda x: x['number_value'], reverse=True)
            if files_sorted:
                # Prendi solo la prima (ultima offerta)
                offer_files.append(files_sorted[0]['path'])
                if len(files_sorted) > 1:
                    print(f"  📁 Cartella {base_folder}: {len(files_sorted)} offerte, prendo l'ultima: {files_sorted[0]['offer_number']}")
        
        print(f"📄 Offerte da processare (ultime per cartella): {len(offer_files)}")
        
        created_accounts = 0
        created_opportunities = 0
        created_leads = 0
        created_offers = 0
        updated_offers = 0
        
        for file_path in offer_files:
            filename = os.path.basename(file_path)
            # Estrai anche il nome della cartella per riferimento
            folder_name = os.path.basename(os.path.dirname(file_path))
            offer_info = extract_offer_info(filename)
            
            client_name = offer_info['client_name']
            if not client_name or client_name == 'Cliente Sconosciuto':
                continue
            
            # Cerca o crea account
            account = Account.query.filter_by(name=client_name).first()
            if not account:
                # Genera immagine fittizia basata sul nome
                image_url = f"https://ui-avatars.com/api/?name={client_name.replace(' ', '+')}&size=128&background=667eea&color=fff"
                
                account = Account(
                    name=client_name,
                    owner_id=admin_user_id,
                    image_url=image_url
                )
                db.session.add(account)
                db.session.flush()
                created_accounts += 1
                print(f"  ✅ Account creato: {client_name}")
            
            # Determina categoria
            supplier_category = determine_supplier_category(filename)
            
            # Cerca opportunità esistente per questo account e numero offerta
            # Usa query SQL diretta per evitare problemi con colonne mancanti
            from sqlalchemy import text
            offer_number = offer_info.get('offer_number', 'N/A')
            opp_name = f"Offerta {offer_number} - {client_name}" if offer_number != 'N/A' else f"Offerta - {client_name}"
            
            existing_opp_id = None
            # Cerca per numero offerta
            result = db.session.execute(
                text("SELECT id FROM opportunities WHERE account_id = :account_id AND name LIKE :pattern LIMIT 1"),
                {"account_id": account.id, "pattern": f"%{offer_number}%"}
            )
            opp_row = result.fetchone()
            if opp_row:
                existing_opp_id = opp_row[0]
            
            if not existing_opp_id:
                # Cerca anche per nome cliente
                result = db.session.execute(
                    text("SELECT id FROM opportunities WHERE account_id = :account_id AND name LIKE :pattern LIMIT 1"),
                    {"account_id": account.id, "pattern": f"%{client_name}%"}
                )
                opp_row = result.fetchone()
                if opp_row:
                    existing_opp_id = opp_row[0]
            
            existing_opp = None
            if existing_opp_id:
                # Recupera solo i campi necessari senza colonne problematiche
                result = db.session.execute(
                    text("SELECT id, name, account_id, folder_path FROM opportunities WHERE id = :opp_id"),
                    {"opp_id": existing_opp_id}
                )
                opp_data = result.fetchone()
                if opp_data:
                    # Crea un oggetto Opportunity minimale solo con i dati necessari
                    existing_opp = type('Opportunity', (), {
                        'id': opp_data[0],
                        'name': opp_data[1],
                        'account_id': opp_data[2],
                        'folder_path': opp_data[3],
                        'supplier_category': None,
                        'description': None,
                        'offers': []
                    })()
            
            if not existing_opp:
                # Crea nuova opportunità con cartella
                import platform
                if platform.system() == 'Windows':
                    base_dir = r"K:\OFFERTE - K\OPPORTUNITA"
                else:
                    base_dir = os.environ.get('OPPORTUNITIES_FOLDER', '/mnt/k/OFFERTE - K/OPPORTUNITA')
                
                if not os.path.exists(base_dir):
                    base_dir = os.path.join(os.path.dirname(__file__), 'opportunita')
                
                os.makedirs(base_dir, exist_ok=True)
                opp_name_clean = "".join(c for c in opp_name if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                folder_name_opp = f"OPP-{datetime.now().strftime('%Y%m%d')}-{opp_name_clean}"
                folder_path_opp = os.path.join(base_dir, folder_name_opp)
                
                if not os.path.exists(folder_path_opp):
                    os.makedirs(folder_path_opp)
                
                # Crea opportunità usando SQL diretto per evitare problemi con colonne mancanti
                result = db.session.execute(
                    text("""
                        INSERT INTO opportunities 
                        (name, stage, amount, probability, supplier_category, account_id, folder_path, owner_id, description, created_at, updated_at)
                        VALUES (:name, :stage, :amount, :probability, :supplier_category, :account_id, :folder_path, :owner_id, :description, :created_at, :updated_at)
                    """),
                    {
                        "name": opp_name,
                        "stage": "Qualification",
                        "amount": 0.0,
                        "probability": 10,
                        "supplier_category": supplier_category,
                        "account_id": account.id,
                        "folder_path": folder_path_opp,
                        "owner_id": admin_user_id,
                        "description": f"Offerta sincronizzata da file: {filename}",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                db.session.flush()
                # Recupera l'ID dell'opportunità appena creata
                opp_id = result.lastrowid
                # Crea oggetto fittizio per compatibilità con il resto del codice
                opp = type('Opportunity', (), {
                    'id': opp_id,
                    'name': opp_name,
                    'account_id': account.id,
                    'folder_path': folder_path_opp,
                    'amount': 0.0
                })()
                created_opportunities += 1
                print(f"  ✅ Opportunità creata: {opp_name} ({supplier_category})")
            else:
                # Aggiorna opportunità esistente usando SQL diretto
                db.session.execute(
                    text("UPDATE opportunities SET supplier_category = :cat WHERE id = :opp_id"),
                    {"cat": supplier_category, "opp_id": existing_opp.id}
                )
                opp = existing_opp
                print(f"  🔄 Opportunità aggiornata: {existing_opp.name} ({supplier_category})")
            
            # Cerca o crea record OfferDocument
            offer_number_str = offer_number if offer_number != 'N/A' else filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
            
            # Se ancora non c'è un numero valido, genera uno basato sul nome del file
            if not offer_number_str or offer_number_str == 'N/A':
                # Estrai qualsiasi numero dal nome del file
                numbers = re.findall(r'\d+', filename)
                if numbers:
                    offer_number_str = f"FILE-{numbers[0]}"
                else:
                    # Usa hash del nome file come fallback
                    offer_number_str = f"FILE-{hash(filename) % 100000}"
            
            # Assicurati che il numero non sia vuoto
            if not offer_number_str or len(offer_number_str.strip()) == 0:
                print(f"  ⚠️  Saltando file senza numero offerta valido: {filename}")
                continue
            
            # Determina la cartella specifica dell'offerta
            # IMPORTANTE: Ogni offerta deve avere la sua cartella specifica, non la cartella principale!
            folder_path = os.path.dirname(file_path)
            
            # Se il file è nella root della cartella principale, crea una cartella specifica per questa offerta
            if folder_path == OFFERS_FOLDER or folder_path == os.path.normpath(OFFERS_FOLDER):
                # File nella root: crea una cartella specifica per questa offerta
                # Usa il numero offerta per creare il nome cartella
                if offer_number_str and offer_number_str != 'N/A':
                    # Estrai informazioni per creare nome cartella
                    offer_num_clean = offer_number_str.replace('FILE-', '').replace('K', '').split('-')[0] if '-' in offer_number_str else offer_number_str
                    folder_name = f"{offer_number_str} - {client_name}"
                    # Pulisci il nome cartella
                    folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).strip()[:100]
                    folder_path = os.path.join(OFFERS_FOLDER, folder_name)
                    
                    # Crea la cartella se non esiste
                    if not os.path.exists(folder_path):
                        try:
                            os.makedirs(folder_path, exist_ok=True)
                            print(f"  📁 Creata cartella specifica per offerta: {folder_name}")
                        except Exception as e:
                            print(f"  ⚠️  Errore creando cartella: {e}")
                            # Fallback: usa la root
                            folder_path = OFFERS_FOLDER
                else:
                    # Se non c'è numero offerta, usa la root (ma non dovrebbe succedere)
                    folder_path = OFFERS_FOLDER
                    print(f"  ⚠️  File nella root senza numero offerta: {filename}")
            
            # Verifica che la cartella non sia la cartella principale
            if folder_path == OFFERS_FOLDER or os.path.basename(folder_path) == os.path.basename(OFFERS_FOLDER):
                print(f"  ⚠️  ATTENZIONE: Offerta {offer_number_str} ha cartella principale invece di cartella specifica!")
                print(f"     Percorso: {folder_path}")
                # Crea una cartella specifica
                folder_name = f"{offer_number_str} - {client_name}"
                folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).strip()[:100]
                folder_path = os.path.join(OFFERS_FOLDER, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    print(f"  📁 Creata cartella specifica: {folder_name}")
            
            print(f"  📂 Cartella offerta: {os.path.basename(folder_path)}")
            
            # Cerca PDF nella stessa cartella
            pdf_path = None
            docx_path = None
            
            # Cerca PDF
            if filename.lower().endswith('.pdf'):
                pdf_path = file_path
            else:
                # Cerca PDF con stesso nome base
                base_name = os.path.splitext(filename)[0]
                pdf_candidate = os.path.join(folder_path, base_name + '.pdf')
                if os.path.exists(pdf_candidate):
                    pdf_path = pdf_candidate
            
            # Cerca DOCX
            if filename.lower().endswith('.docx'):
                docx_path = file_path
            else:
                base_name = os.path.splitext(filename)[0]
                docx_candidate = os.path.join(folder_path, base_name + '.docx')
                if os.path.exists(docx_candidate):
                    docx_path = docx_candidate
            
            # Estrai valore dal PDF se disponibile
            offer_amount = 0.0
            if pdf_path and os.path.exists(pdf_path):
                try:
                    offer_amount = extract_offer_amount_from_file(pdf_path)
                    if offer_amount > 0:
                        print(f"  💰 Valore estratto da PDF: €{offer_amount:,.2f}")
                except Exception as e:
                    print(f"  ⚠️  Errore estrazione valore da PDF: {e}")
            
            # Cerca offerta esistente
            existing_offer = OfferDocument.query.filter_by(number=offer_number_str).first()
            
            if not existing_offer:
                # Crea nuova offerta
                offer_doc = OfferDocument(
                    number=offer_number_str,
                    status='draft',
                    amount=offer_amount,
                    description=f"Offerta sincronizzata: {client_name}",
                    pdf_path=pdf_path if pdf_path and os.path.exists(pdf_path) else None,
                    docx_path=docx_path if docx_path and os.path.exists(docx_path) else None,
                    folder_path=folder_path,
                    opportunity_id=opp.id,
                    owner_id=admin_user_id
                )
                db.session.add(offer_doc)
                created_offers += 1
                print(f"  ✅ Offerta creata: {offer_number_str} (€{offer_amount:,.2f})")
            else:
                # Aggiorna offerta esistente
                if offer_amount > 0 and (not existing_offer.amount or existing_offer.amount == 0):
                    existing_offer.amount = offer_amount
                    updated_offers += 1
                    print(f"  💰 Valore aggiornato per offerta {offer_number_str}: €{offer_amount:,.2f}")
                
                if not existing_offer.pdf_path and pdf_path and os.path.exists(pdf_path):
                    existing_offer.pdf_path = pdf_path
                if not existing_offer.docx_path and docx_path and os.path.exists(docx_path):
                    existing_offer.docx_path = docx_path
                if not existing_offer.opportunity_id:
                    existing_offer.opportunity_id = opp.id
                if not existing_offer.folder_path:
                    existing_offer.folder_path = folder_path
            
            # Aggiorna valore opportunità con somma delle offerte usando SQL diretto
            result = db.session.execute(
                text("SELECT COALESCE(SUM(amount), 0) FROM offers WHERE opportunity_id = :opp_id"),
                {"opp_id": opp.id}
            )
            total_offers_value = result.fetchone()[0] or 0.0
            
            if total_offers_value > 0:
                # Verifica valore attuale opportunità
                result = db.session.execute(
                    text("SELECT amount FROM opportunities WHERE id = :opp_id"),
                    {"opp_id": opp.id}
                )
                current_amount = result.fetchone()
                if not current_amount or current_amount[0] == 0:
                    db.session.execute(
                        text("UPDATE opportunities SET amount = :amount WHERE id = :opp_id"),
                        {"amount": total_offers_value, "opp_id": opp.id}
                    )
                    print(f"  💰 Valore opportunità aggiornato: €{total_offers_value:,.2f}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ SINCRONIZZAZIONE COMPLETATA")
        print("=" * 60)
        print(f"📊 Account creati: {created_accounts}")
        print(f"📊 Opportunità create: {created_opportunities}")
        print(f"📊 Offerte create: {created_offers}")
        print(f"📊 Offerte aggiornate: {updated_offers}")
        print(f"📊 Leads creati: {created_leads}")

if __name__ == '__main__':
    sync_offers()


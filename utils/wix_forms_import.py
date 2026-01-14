#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti dal form Wix Studio e li crea come opportunità
"""
import sys
import os
import json
from datetime import datetime
from sqlalchemy import text

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db, Opportunity, Account, Contact, User


def extract_company_from_message(message):
    """Estrae il nome dell'azienda dal messaggio se presente"""
    if not message:
        return None
    
    import re
    
    # Cerca nomi aziendali con suffissi legali (SRL, SPA, SAS, ecc.)
    company_patterns = [
        r'([A-Z][a-zA-Z0-9\s&\.\-]+(?:SRL|SPA|SAS|S\.N\.C\.|S\.R\.L\.|S\.P\.A\.|S\.A\.S\.))',
        r'(?:azienda|ditta|società|company|societa)[:\s]+([A-Z][a-zA-Z0-9\s&\.\-]+)',
        r'([A-Z][a-zA-Z0-9\s&\.\-]{3,}(?:\s+(?:SRL|SPA|SAS|S\.N\.C\.))?)',
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        if matches:
            company = matches[0].strip()
            # Rimuovi parole comuni all'inizio
            company = re.sub(r'^(?:la|il|lo|gli|le|di|da|per|con|su|in|a|al|alla|dalla|nella|sulla)\s+', '', company, flags=re.IGNORECASE)
            if len(company) > 3 and not company.lower() in ['buongiorno', 'buonasera', 'salve', 'gentile', 'gentili']:
                return company.strip()
    
    # Cerca email nel messaggio e usa il dominio
    email_pattern = r'([a-zA-Z0-9._-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    emails = re.findall(email_pattern, message)
    if emails:
        domain = emails[0][1]
        # Ignora domini generici
        generic_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'live.com', 'mail.com']
        if domain.lower() not in generic_domains:
            company = domain.split('.')[0].replace('-', ' ').title()
            if len(company) > 2:
                return company
    
    return None


def categorize_product(product_name):
    """Categorizza il prodotto per determinare supplier_category"""
    if not product_name:
        return 'Altro'
    
    product_lower = product_name.lower()
    
    if 'unitree' in product_lower or 'g1' in product_lower or 'go2' in product_lower or 'b2' in product_lower or 'r1' in product_lower:
        return 'Unitree'
    elif 'ur' in product_lower or 'universal' in product_lower or 'cobot' in product_lower:
        return 'Universal Robots'
    elif 'mir' in product_lower or 'pallet' in product_lower or 'amr' in product_lower:
        return 'MIR'
    elif 'roeq' in product_lower:
        return 'ROEQ'
    elif 'servizi' in product_lower or 'corsi' in product_lower or 'formazione' in product_lower:
        return 'Servizi'
    else:
        return 'Altro'


def import_wix_form_submission(submission_data, user_id=1):
    """
    Importa una singola submission del form Wix come opportunità
    
    submission_data: dict con chiavi:
        - name: nome contatto
        - email: email
        - phone: telefono
        - product: prodotto di interesse
        - message: messaggio
        - created_date: data creazione
    """
    with app.app_context():
        try:
            # Verifica se esiste già un'opportunità con questa email
            existing_opp = db.session.execute(text("""
                SELECT o.id FROM opportunities o
                JOIN contacts c ON o.contact_id = c.id
                WHERE c.email = :email
                AND o.name LIKE :name_pattern
            """), {
                "email": submission_data['email'],
                "name_pattern": f"%{submission_data.get('product', '')}%"
            }).fetchone()
            
            if existing_opp:
                print(f"  ⚠️  Opportunità già esistente per {submission_data['email']}")
                return None
            
            # Estrai nome e cognome
            name_parts = submission_data.get('name', '').strip().split(' ', 1)
            first_name = name_parts[0] if name_parts else 'Contatto'
            last_name = name_parts[1] if len(name_parts) > 1 else 'Wix Form'
            
            # Estrai nome azienda dal messaggio o email
            email = submission_data.get('email', '')
            company_name = extract_company_from_message(submission_data.get('message', ''))
            
            if not company_name:
                # Prova a estrarre dal dominio email (solo se non è un dominio generico)
                if '@' in email:
                    domain = email.split('@')[1].lower()
                    generic_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'live.com', 'mail.com', 'libero.it', 'virgilio.it', 'tiscali.it']
                    if domain not in generic_domains:
                        company_name = domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()
            
            # Se ancora non abbiamo un nome azienda, usa un nome generico basato sul prodotto
            if not company_name or len(company_name) < 3:
                product = submission_data.get('product', 'Richiesta informazioni')
                # Usa il nome del contatto solo se abbiamo almeno nome e cognome
                if first_name and last_name and last_name != 'Wix Form':
                    company_name = f"Cliente {product[:20]} - {first_name} {last_name}"
                else:
                    company_name = f"Cliente {product[:30]}"
            
            # Cerca o crea Account
            account = db.session.execute(text("""
                SELECT id FROM accounts WHERE name = :name LIMIT 1
            """), {"name": company_name}).fetchone()
            
            if account:
                account_id = account[0]
            else:
                # Crea nuovo account
                result = db.session.execute(text("""
                    INSERT INTO accounts (name, phone, owner_id, created_at, updated_at)
                    VALUES (:name, :phone, :owner_id, :created_at, :updated_at)
                """), {
                    "name": company_name,
                    "phone": submission_data.get('phone'),
                    "owner_id": user_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
                account_id = result.lastrowid
            
            # Cerca o crea Contact
            contact = db.session.execute(text("""
                SELECT id FROM contacts WHERE email = :email LIMIT 1
            """), {"email": submission_data['email']}).fetchone()
            
            if contact:
                contact_id = contact[0]
            else:
                # Crea nuovo contatto
                result = db.session.execute(text("""
                    INSERT INTO contacts (first_name, last_name, email, phone, account_id, owner_id, created_at, updated_at)
                    VALUES (:first_name, :last_name, :email, :phone, :account_id, :owner_id, :created_at, :updated_at)
                """), {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": submission_data['email'],
                    "phone": submission_data.get('phone'),
                    "account_id": account_id,
                    "owner_id": user_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
                contact_id = result.lastrowid
            
            # Crea opportunità
            product = submission_data.get('product', 'Richiesta informazioni')
            opp_name = f"{product} - {company_name}"
            
            # Categorizza prodotto
            supplier_category = categorize_product(product)
            
            # Crea opportunità
            result = db.session.execute(text("""
                INSERT INTO opportunities 
                (name, stage, amount, probability, supplier_category, account_id, contact_id, 
                 owner_id, description, heat_level, created_at, updated_at)
                VALUES (:name, :stage, :amount, :probability, :supplier_category, :account_id, :contact_id,
                        :owner_id, :description, :heat_level, :created_at, :updated_at)
            """), {
                "name": opp_name,
                "stage": "Qualification",
                "amount": 0.0,
                "probability": 5,  # 5% per fredde con speranza
                "supplier_category": supplier_category,
                "account_id": account_id,
                "contact_id": contact_id,
                "owner_id": user_id,
                "description": submission_data.get('message', ''),
                "heat_level": "fredda_speranza",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            db.session.commit()
            opportunity_id = result.lastrowid
            
            # Crea attività "Chiamare" (se la tabella tasks esiste)
            try:
                db.session.execute(text("""
                    INSERT INTO tasks 
                    (opportunity_id, assigned_to_id, description, due_date, status, created_at, updated_at)
                    VALUES (:opportunity_id, :assigned_to_id, :description, :due_date, :status, :created_at, :updated_at)
                """), {
                    "opportunity_id": opportunity_id,
                    "assigned_to_id": user_id,
                    "description": "Chiamare cliente per informazioni su " + product,
                    "due_date": datetime.utcnow().date(),
                    "status": "Not Started",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
            except Exception as task_error:
                # Se la tabella tasks non esiste, continua senza creare attività
                db.session.rollback()
                pass
            
            print(f"  ✅ Importata: {opp_name} ({submission_data['email']})")
            return opportunity_id
            
        except Exception as e:
            db.session.rollback()
            print(f"  ❌ Errore importazione {submission_data.get('email', 'unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def import_wix_submissions_from_json(json_file_path, user_id=1):
    """
    Importa submissions da un file JSON
    Il file JSON deve contenere un array di oggetti con:
    - name, email, phone, product, message, created_date
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    imported = 0
    skipped = 0
    
    print(f"📥 Importazione {len(submissions)} submissions da Wix Studio...\n")
    
    for submission in submissions:
        result = import_wix_form_submission(submission, user_id)
        if result:
            imported += 1
        else:
            skipped += 1
    
    print(f"\n✅ Importate: {imported}")
    print(f"⚠️  Saltate: {skipped}")
    
    return imported, skipped


if __name__ == '__main__':
    # Esempio di utilizzo
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        import_wix_submissions_from_json(json_file)
    else:
        print("Utilizzo: python wix_forms_import.py <file_json>")
        print("\nFormato JSON atteso:")
        print("""
[
  {
    "name": "Mario Rossi",
    "email": "mario.rossi@example.com",
    "phone": "+39 123 456 7890",
    "product": "Unitree G1",
    "message": "Vorrei informazioni...",
    "created_date": "2026-01-13T12:33:00Z"
  }
]
        """)

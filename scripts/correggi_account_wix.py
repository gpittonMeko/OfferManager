#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corregge i nomi Account creati male dai contatti Wix
"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
import re

def extract_company_from_message(message):
    """Estrae il nome dell'azienda dal messaggio se presente"""
    if not message:
        return None
    
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

def fix_wix_accounts():
    """Corregge i nomi Account creati male"""
    with app.app_context():
        # Trova Account con nomi che sembrano messaggi (contengono "Buongiorno", "Salve", ecc.)
        bad_accounts = db.session.execute(text("""
            SELECT a.id, a.name, o.description, c.email, c.first_name, c.last_name, o.name as opp_name
            FROM accounts a
            JOIN opportunities o ON o.account_id = a.id
            LEFT JOIN contacts c ON o.contact_id = c.id
            WHERE (
                a.name LIKE '%Buongiorno%' OR
                a.name LIKE '%Buonasera%' OR
                a.name LIKE '%Salve%' OR
                a.name LIKE '%Gentile%' OR
                a.name LIKE '%Gentili%' OR
                a.name LIKE 'Cliente %' OR
                LENGTH(a.name) > 50
            )
            AND o.description IS NOT NULL
            AND o.description != ''
            ORDER BY a.id
        """)).fetchall()
        
        print(f"📊 Trovati {len(bad_accounts)} Account da correggere\n")
        
        fixed = 0
        skipped = 0
        
        for account_id, account_name, description, email, first_name, last_name, opp_name in bad_accounts:
            try:
                # Prova a estrarre il nome azienda dal messaggio
                new_name = extract_company_from_message(description)
                
                if not new_name:
                    # Prova a estrarre dal dominio email
                    if email and '@' in email:
                        domain = email.split('@')[1].lower()
                        generic_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'live.com', 'mail.com', 'libero.it', 'virgilio.it', 'tiscali.it']
                        if domain not in generic_domains:
                            new_name = domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()
                
                if not new_name or len(new_name) < 3:
                    # Usa nome contatto come fallback
                    if first_name and last_name and last_name != 'Wix Form':
                        new_name = f"{first_name} {last_name}"
                    else:
                        # Estrai prodotto dal nome opportunità
                        if ' - ' in opp_name:
                            product = opp_name.split(' - ')[0]
                            if first_name:
                                new_name = f"Cliente {product[:20]} - {first_name}"
                            else:
                                new_name = f"Cliente {product[:30]}"
                        else:
                            skipped += 1
                            print(f"  ⚠️  Saltato Account {account_id}: {account_name} (non riesco a estrarre nome valido)")
                            continue
                
                # Verifica se esiste già un Account con questo nome
                existing = db.session.execute(text("""
                    SELECT id FROM accounts WHERE name = :name AND id != :account_id LIMIT 1
                """), {"name": new_name, "account_id": account_id}).fetchone()
                
                if existing:
                    # Unisci gli Account
                    existing_id = existing[0]
                    print(f"  🔄 Account {account_id} ({account_name}) → unisce con Account {existing_id} ({new_name})")
                    
                    # Aggiorna tutte le opportunità
                    db.session.execute(text("""
                        UPDATE opportunities SET account_id = :existing_id WHERE account_id = :account_id
                    """), {"existing_id": existing_id, "account_id": account_id})
                    
                    # Aggiorna tutti i contatti
                    db.session.execute(text("""
                        UPDATE contacts SET account_id = :existing_id WHERE account_id = :account_id
                    """), {"existing_id": existing_id, "account_id": account_id})
                    
                    # Elimina Account duplicato
                    db.session.execute(text("DELETE FROM accounts WHERE id = :account_id"), {"account_id": account_id})
                    db.session.commit()
                    
                    fixed += 1
                else:
                    # Aggiorna il nome Account
                    print(f"  ✅ Account {account_id}: '{account_name}' → '{new_name}'")
                    db.session.execute(text("""
                        UPDATE accounts SET name = :new_name WHERE id = :account_id
                    """), {"new_name": new_name, "account_id": account_id})
                    db.session.commit()
                    fixed += 1
                    
            except Exception as e:
                print(f"  ❌ Errore correzione Account {account_id}: {str(e)}")
                db.session.rollback()
                skipped += 1
        
        print(f"\n📊 Riepilogo:")
        print(f"  Corretti: {fixed}")
        print(f"  Saltati: {skipped}")
        
        return fixed, skipped

if __name__ == '__main__':
    print("=" * 70)
    print("🔧 Correzione Account Wix con nomi errati")
    print("=" * 70)
    print()
    
    fixed, skipped = fix_wix_accounts()
    
    print("\n" + "=" * 70)
    print(f"✅ Completato: {fixed} Account corretti, {skipped} saltati")
    print("=" * 70)

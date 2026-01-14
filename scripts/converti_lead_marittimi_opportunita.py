#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte tutti i Lead marittimi (ROV) in Opportunità
"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
from datetime import datetime

def convert_maritime_leads_to_opportunities():
    """Converte Lead marittimi in Opportunità"""
    with app.app_context():
        # Trova tutti i Lead marittimi/ROV
        maritime_leads = db.session.execute(text("""
            SELECT id, company_name, contact_first_name, contact_last_name, 
                   email, phone, address, industry, interest, notes, owner_id
            FROM leads
            WHERE industry LIKE '%Marina%' 
               OR industry LIKE '%Marittim%'
               OR interest = 'ROV'
               OR notes LIKE '%ROV%'
               OR source = 'Database Marittimo'
            AND status != 'Converted'
        """)).fetchall()
        
        print(f"📊 Trovati {len(maritime_leads)} Lead marittimi da convertire\n")
        
        converted = 0
        skipped = 0
        
        for lead in maritime_leads:
            lead_id = lead[0]
            company_name = lead[1]
            first_name = lead[2] or 'Contatto'
            last_name = lead[3] or 'Marittimo'
            email = lead[4]
            phone = lead[5]
            address = lead[6]
            industry = lead[7]
            interest = lead[8] or 'ROV'
            notes = lead[9]
            owner_id = lead[10]
            
            # Verifica se esiste già un'opportunità per questo lead
            existing_opp = db.session.execute(text("""
                SELECT id FROM opportunities 
                WHERE account_id IN (
                    SELECT id FROM accounts WHERE name = :company_name
                )
                AND contact_id IN (
                    SELECT id FROM contacts WHERE email = :email
                )
            """), {"company_name": company_name, "email": email}).fetchone()
            
            if existing_opp:
                print(f"  ⚠️  Saltato: {company_name} (opportunità già esistente)")
                skipped += 1
                continue
            
            try:
                # Crea Account
                account = db.session.execute(text("""
                    SELECT id FROM accounts WHERE name = :name LIMIT 1
                """), {"name": company_name}).fetchone()
                
                if account:
                    account_id = account[0]
                else:
                    result = db.session.execute(text("""
                        INSERT INTO accounts (name, phone, billing_address, industry, owner_id, created_at, updated_at)
                        VALUES (:name, :phone, :address, :industry, :owner_id, :created_at, :updated_at)
                    """), {
                        "name": company_name,
                        "phone": phone,
                        "address": address,
                        "industry": industry,
                        "owner_id": owner_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    account_id = result.lastrowid
                
                # Crea Contact
                contact = db.session.execute(text("""
                    SELECT id FROM contacts WHERE email = :email LIMIT 1
                """), {"email": email}).fetchone()
                
                if contact:
                    contact_id = contact[0]
                else:
                    result = db.session.execute(text("""
                        INSERT INTO contacts (first_name, last_name, email, phone, account_id, owner_id, created_at, updated_at)
                        VALUES (:first_name, :last_name, :email, :phone, :account_id, :owner_id, :created_at, :updated_at)
                    """), {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "account_id": account_id,
                        "owner_id": owner_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    contact_id = result.lastrowid
                
                # Determina supplier_category basato su interest
                supplier_category = 'MIR'  # Default per ROV/Marittimo
                if 'ROV' in (interest or ''):
                    supplier_category = 'MIR'
                elif 'Unitree' in (notes or ''):
                    supplier_category = 'Unitree'
                
                # Crea Opportunità
                opp_name = f"{interest or 'ROV'} - {company_name}"
                result = db.session.execute(text("""
                    INSERT INTO opportunities 
                    (name, stage, amount, probability, supplier_category, account_id, contact_id,
                     owner_id, description, heat_level, lead_id, created_at, updated_at)
                    VALUES (:name, :stage, :amount, :probability, :supplier_category, :account_id, :contact_id,
                            :owner_id, :description, :heat_level, :lead_id, :created_at, :updated_at)
                """), {
                    "name": opp_name,
                    "stage": "Qualification",
                    "amount": 0.0,
                    "probability": 5,  # 5% per fredde con speranza
                    "supplier_category": supplier_category,
                    "account_id": account_id,
                    "contact_id": contact_id,
                    "owner_id": owner_id,
                    "description": notes or f"Lead marittimo - {interest or 'ROV'}",
                    "heat_level": "fredda_speranza",
                    "lead_id": lead_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
                opportunity_id = result.lastrowid
                
                # Aggiorna Lead come convertito
                db.session.execute(text("""
                    UPDATE leads 
                    SET status = 'Converted', 
                        converted_opportunity_id = :opp_id,
                        converted_account_id = :account_id,
                        converted_contact_id = :contact_id
                    WHERE id = :lead_id
                """), {
                    "opp_id": opportunity_id,
                    "account_id": account_id,
                    "contact_id": contact_id,
                    "lead_id": lead_id
                })
                db.session.commit()
                
                print(f"  ✅ Convertito: {opp_name}")
                converted += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"  ❌ Errore conversione {company_name}: {str(e)}")
                skipped += 1
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ COMPLETATO!")
        print(f"   Convertite: {converted} opportunità")
        print(f"   Saltate: {skipped}")
        print(f"{'='*70}")

if __name__ == '__main__':
    convert_maritime_leads_to_opportunities()

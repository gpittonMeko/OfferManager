#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte Lead ROV/Marittimi e VOX in Opportunità
"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
from datetime import datetime

def convert_all_rov_leads():
    """Converte tutti i Lead ROV/Marittimi in Opportunità"""
    with app.app_context():
        # Trova tutti i Lead ROV/Marittimi non convertiti
        leads = db.session.execute(text("""
            SELECT id, company_name, contact_first_name, contact_last_name, 
                   email, phone, address, industry, interest, notes, owner_id, source
            FROM leads
            WHERE status != 'Converted'
            AND (
                interest LIKE '%ROV%' OR 
                industry LIKE '%Marina%' OR 
                industry LIKE '%Marittim%' OR
                notes LIKE '%ROV%' OR
                notes LIKE '%marittimo%' OR
                notes LIKE '%subacqueo%'
            )
        """)).fetchall()
        
        print(f"📊 Trovati {len(leads)} Lead ROV/Marittimi da convertire\n")
        
        converted = 0
        skipped = 0
        errors = 0
        
        for lead in leads:
            try:
                lead_id, company_name, first_name, last_name, email, phone, address, industry, interest, notes, owner_id, source = lead
                
                # Verifica se esiste già un'opportunità per questo Lead
                existing = db.session.execute(text("""
                    SELECT id FROM opportunities WHERE lead_id = :lead_id
                """), {"lead_id": lead_id}).fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # Cerca o crea Account
                account = db.session.execute(text("""
                    SELECT id FROM accounts WHERE name = :name LIMIT 1
                """), {"name": company_name}).fetchone()
                
                if account:
                    account_id = account[0]
                else:
                    result = db.session.execute(text("""
                        INSERT INTO accounts (name, phone, address, owner_id, created_at, updated_at)
                        VALUES (:name, :phone, :address, :owner_id, :created_at, :updated_at)
                    """), {
                        "name": company_name,
                        "phone": phone,
                        "address": address,
                        "owner_id": owner_id or 1,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    account_id = result.lastrowid
                
                # Cerca o crea Contact
                contact = None
                if email:
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
                        "first_name": first_name or 'Contatto',
                        "last_name": last_name or 'Marittimo',
                        "email": email,
                        "phone": phone,
                        "account_id": account_id,
                        "owner_id": owner_id or 1,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    contact_id = result.lastrowid
                
                # Determina supplier_category
                supplier_category = 'MIR'
                if 'Unitree' in (notes or ''):
                    supplier_category = 'Unitree'
                elif 'UR' in (interest or '') or 'Universal' in (interest or ''):
                    supplier_category = 'Universal Robots'
                
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
                    "owner_id": owner_id or 1,
                    "description": notes or '',
                    "heat_level": "fredda_speranza",
                    "lead_id": lead_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
                opportunity_id = result.lastrowid
                
                # Crea attività "Chiamare"
                try:
                    db.session.execute(text("""
                        INSERT INTO tasks 
                        (opportunity_id, assigned_to_id, description, due_date, status, created_at, updated_at)
                        VALUES (:opportunity_id, :assigned_to_id, :description, :due_date, :status, :created_at, :updated_at)
                    """), {
                        "opportunity_id": opportunity_id,
                        "assigned_to_id": owner_id or 1,
                        "description": f"Chiamare cliente per informazioni su {interest or 'ROV'}",
                        "due_date": datetime.utcnow().date(),
                        "status": "Not Started",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                except:
                    db.session.rollback()
                
                # Marca Lead come convertito
                db.session.execute(text("""
                    UPDATE leads SET status = 'Converted', converted_opportunity_id = :opp_id
                    WHERE id = :lead_id
                """), {"lead_id": lead_id, "opp_id": opportunity_id})
                db.session.commit()
                
                converted += 1
                print(f"  ✅ Convertito: {opp_name}")
                
            except Exception as e:
                errors += 1
                print(f"  ❌ Errore conversione Lead {lead[0]}: {str(e)}")
                db.session.rollback()
        
        print(f"\n📊 Riepilogo:")
        print(f"  Convertiti: {converted}")
        print(f"  Saltati: {skipped}")
        print(f"  Errori: {errors}")
        
        return converted, skipped, errors


def convert_vox_leads():
    """Converte tutti i Lead VOX in Opportunità"""
    with app.app_context():
        # Trova tutti i Lead VOX non convertiti
        leads = db.session.execute(text("""
            SELECT id, company_name, contact_first_name, contact_last_name, 
                   email, phone, address, industry, interest, notes, owner_id, source
            FROM leads
            WHERE status != 'Converted'
            AND (
                source LIKE '%VOX%' OR 
                source LIKE '%Vox%' OR 
                notes LIKE '%VOX%' OR
                notes LIKE '%Vox%'
            )
        """)).fetchall()
        
        print(f"📊 Trovati {len(leads)} Lead VOX da convertire\n")
        
        converted = 0
        skipped = 0
        errors = 0
        
        for lead in leads:
            try:
                lead_id, company_name, first_name, last_name, email, phone, address, industry, interest, notes, owner_id, source = lead
                
                # Verifica se esiste già un'opportunità per questo Lead
                existing = db.session.execute(text("""
                    SELECT id FROM opportunities WHERE lead_id = :lead_id
                """), {"lead_id": lead_id}).fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # Cerca o crea Account
                account = db.session.execute(text("""
                    SELECT id FROM accounts WHERE name = :name LIMIT 1
                """), {"name": company_name}).fetchone()
                
                if account:
                    account_id = account[0]
                else:
                    result = db.session.execute(text("""
                        INSERT INTO accounts (name, phone, address, owner_id, created_at, updated_at)
                        VALUES (:name, :phone, :address, :owner_id, :created_at, :updated_at)
                    """), {
                        "name": company_name,
                        "phone": phone,
                        "address": address,
                        "owner_id": owner_id or 1,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    account_id = result.lastrowid
                
                # Cerca o crea Contact
                contact = None
                if email:
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
                        "first_name": first_name or 'Contatto',
                        "last_name": last_name or 'VOX',
                        "email": email,
                        "phone": phone,
                        "account_id": account_id,
                        "owner_id": owner_id or 1,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                    contact_id = result.lastrowid
                
                # Determina supplier_category
                supplier_category = 'Altro'
                if 'Unitree' in (notes or ''):
                    supplier_category = 'Unitree'
                elif 'UR' in (interest or '') or 'Universal' in (interest or ''):
                    supplier_category = 'Universal Robots'
                elif 'MIR' in (interest or '') or 'ROV' in (interest or ''):
                    supplier_category = 'MIR'
                
                # Crea Opportunità
                opp_name = f"{interest or 'Richiesta'} - {company_name}"
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
                    "owner_id": owner_id or 1,
                    "description": notes or '',
                    "heat_level": "fredda_speranza",
                    "lead_id": lead_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                db.session.commit()
                opportunity_id = result.lastrowid
                
                # Crea attività "Chiamare"
                try:
                    db.session.execute(text("""
                        INSERT INTO tasks 
                        (opportunity_id, assigned_to_id, description, due_date, status, created_at, updated_at)
                        VALUES (:opportunity_id, :assigned_to_id, :description, :due_date, :status, :created_at, :updated_at)
                    """), {
                        "opportunity_id": opportunity_id,
                        "assigned_to_id": owner_id or 1,
                        "description": f"Chiamare cliente VOX",
                        "due_date": datetime.utcnow().date(),
                        "status": "Not Started",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.session.commit()
                except:
                    db.session.rollback()
                
                # Marca Lead come convertito
                db.session.execute(text("""
                    UPDATE leads SET status = 'Converted', converted_opportunity_id = :opp_id
                    WHERE id = :lead_id
                """), {"lead_id": lead_id, "opp_id": opportunity_id})
                db.session.commit()
                
                converted += 1
                print(f"  ✅ Convertito: {opp_name}")
                
            except Exception as e:
                errors += 1
                print(f"  ❌ Errore conversione Lead {lead[0]}: {str(e)}")
                db.session.rollback()
        
        print(f"\n📊 Riepilogo:")
        print(f"  Convertiti: {converted}")
        print(f"  Saltati: {skipped}")
        print(f"  Errori: {errors}")
        
        return converted, skipped, errors


if __name__ == '__main__':
    print("=" * 70)
    print("🔄 Conversione Lead ROV/Marittimi e VOX in Opportunità")
    print("=" * 70)
    print()
    
    print("1️⃣ Conversione Lead ROV/Marittimi...")
    rov_converted, rov_skipped, rov_errors = convert_all_rov_leads()
    
    print("\n2️⃣ Conversione Lead VOX...")
    vox_converted, vox_skipped, vox_errors = convert_vox_leads()
    
    print("\n" + "=" * 70)
    print("📊 Riepilogo Finale:")
    print(f"  ROV/Marittimi: {rov_converted} convertiti, {rov_skipped} saltati, {rov_errors} errori")
    print(f"  VOX: {vox_converted} convertiti, {vox_skipped} saltati, {vox_errors} errori")
    print("=" * 70)

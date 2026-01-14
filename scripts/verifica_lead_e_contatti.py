#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dove sono finiti i Lead e i contatti"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    print("=" * 70)
    print("🔍 VERIFICA LEAD E CONTATTI")
    print("=" * 70)
    print()
    
    # Conta totale Lead
    total_leads = db.session.execute(text("SELECT COUNT(*) FROM leads")).fetchone()[0]
    print(f"📊 Totale Lead nel database: {total_leads}")
    
    # Lead convertiti
    converted_leads = db.session.execute(text("SELECT COUNT(*) FROM leads WHERE status = 'Converted'")).fetchone()[0]
    print(f"✅ Lead convertiti: {converted_leads}")
    
    # Lead non convertiti
    not_converted = db.session.execute(text("SELECT COUNT(*) FROM leads WHERE status != 'Converted' OR status IS NULL")).fetchone()[0]
    print(f"📋 Lead non convertiti: {not_converted}")
    
    # Lead ROV/Marittimi
    rov_leads = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE (
            interest LIKE '%ROV%' OR 
            industry LIKE '%Marina%' OR 
            industry LIKE '%Marittim%' OR
            notes LIKE '%ROV%' OR
            notes LIKE '%marittimo%' OR
            notes LIKE '%subacqueo%'
        )
    """)).fetchone()[0]
    print(f"🌊 Lead ROV/Marittimi: {rov_leads}")
    
    # Lead VOX
    vox_leads = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%')
    """)).fetchone()[0]
    print(f"📧 Lead VOX: {vox_leads}")
    
    # Conta totale Contatti
    total_contacts = db.session.execute(text("SELECT COUNT(*) FROM contacts")).fetchone()[0]
    print(f"\n👥 Totale Contatti nel database: {total_contacts}")
    
    # Contatti con email
    contacts_with_email = db.session.execute(text("SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ''")).fetchone()[0]
    print(f"📧 Contatti con email: {contacts_with_email}")
    
    # Opportunità create da Lead convertiti
    opps_from_leads = db.session.execute(text("SELECT COUNT(*) FROM opportunities WHERE lead_id IS NOT NULL")).fetchone()[0]
    print(f"\n💼 Opportunità create da Lead: {opps_from_leads}")
    
    # Mostra alcuni Lead non convertiti
    print(f"\n📋 Primi 10 Lead non convertiti:")
    leads = db.session.execute(text("""
        SELECT id, company_name, contact_first_name, contact_last_name, email, status, created_at
        FROM leads 
        WHERE status != 'Converted' OR status IS NULL
        ORDER BY created_at DESC
        LIMIT 10
    """)).fetchall()
    
    for lead in leads:
        print(f"   ID: {lead[0]}, Azienda: {lead[1]}, Contatto: {lead[2]} {lead[3]}, Email: {lead[4]}, Status: {lead[5]}, Creato: {lead[6]}")
    
    # Verifica se ci sono stati cancellazioni recenti
    print(f"\n🗑️  Verifica cancellazioni...")
    # Non possiamo verificare direttamente, ma possiamo vedere se ci sono opportunità senza Lead associati che dovrebbero averli
    
    print(f"\n✅ Verifica completata!")

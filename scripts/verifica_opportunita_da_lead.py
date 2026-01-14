#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica che le Opportunità create dai Lead siano visibili"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    print("=" * 70)
    print("🔍 VERIFICA OPPORTUNITÀ DA LEAD")
    print("=" * 70)
    print()
    
    # Opportunità create da Lead
    opps_from_leads = db.session.execute(text("""
        SELECT o.id, o.name, o.stage, o.heat_level, o.created_at, 
               l.company_name, l.email, l.status as lead_status
        FROM opportunities o
        JOIN leads l ON o.lead_id = l.id
        ORDER BY o.created_at DESC
        LIMIT 20
    """)).fetchall()
    
    print(f"📊 Opportunità create da Lead (prime 20):\n")
    
    for opp in opps_from_leads:
        print(f"  ID: {opp[0]}")
        print(f"  Nome: {opp[1]}")
        print(f"  Stage: {opp[2]}")
        print(f"  Heat Level: {opp[3]}")
        print(f"  Azienda Lead: {opp[5]}")
        print(f"  Email Lead: {opp[6]}")
        print(f"  Status Lead: {opp[7]}")
        print(f"  Creata: {opp[4]}")
        print()
    
    # Conta per tipo
    total_opps = db.session.execute(text("SELECT COUNT(*) FROM opportunities")).fetchone()[0]
    opps_with_leads = db.session.execute(text("SELECT COUNT(*) FROM opportunities WHERE lead_id IS NOT NULL")).fetchone()[0]
    opps_without_leads = total_opps - opps_with_leads
    
    print(f"\n📈 Statistiche:")
    print(f"  Totale Opportunità: {total_opps}")
    print(f"  Da Lead convertiti: {opps_with_leads}")
    print(f"  Non da Lead: {opps_without_leads}")
    
    # Verifica che i Contatti siano ancora presenti
    contacts_from_leads = db.session.execute(text("""
        SELECT COUNT(DISTINCT c.id) 
        FROM contacts c
        JOIN opportunities o ON c.id = o.contact_id
        WHERE o.lead_id IS NOT NULL
    """)).fetchone()[0]
    
    print(f"  Contatti associati a Opportunità da Lead: {contacts_from_leads}")

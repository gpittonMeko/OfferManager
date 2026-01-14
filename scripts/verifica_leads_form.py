#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica se i contatti del form sono stati importati come Lead"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Verifica se ci sono Lead con email del form
    form_emails_sample = [
        'miriamdimatera@hotmail.it',
        'geomgv@gmail.co',
        'fabio.cortinovis@ntsmoulding.com',
        'massimo.rienzi@innovagroup.it',
        'pspiezia@telsite.it',
        'antoniocapuano@hotmail.com',
        'chiara.tonanni@gmail.com',
        'acquisti@mb-fix.it'
    ]
    
    # Conta tutti i Lead
    total_leads = db.session.execute(text("SELECT COUNT(*) FROM leads")).fetchone()[0]
    print(f"📊 Totale Lead nel database: {total_leads}\n")
    
    # Verifica se ci sono Lead con queste email
    for email in form_emails_sample:
        lead = db.session.execute(text("""
            SELECT id, company_name, contact_first_name, contact_last_name, email, status, created_at
            FROM leads WHERE email = :email
        """), {"email": email}).fetchone()
        
        if lead:
            print(f"✅ Trovato Lead:")
            print(f"   ID: {lead[0]}")
            print(f"   Azienda: {lead[1]}")
            print(f"   Contatto: {lead[2]} {lead[3]}")
            print(f"   Email: {lead[4]}")
            print(f"   Status: {lead[5]}")
            print(f"   Creato: {lead[6]}")
            print()
    
    # Verifica se ci sono opportunità create da Lead convertiti
    opps_from_leads = db.session.execute(text("""
        SELECT o.id, o.name, o.stage, o.created_at, l.email, l.company_name
        FROM opportunities o
        JOIN leads l ON o.lead_id = l.id
        ORDER BY o.created_at DESC
        LIMIT 20
    """)).fetchall()
    
    print(f"\n📊 Opportunità create da Lead convertiti (ultime 20):\n")
    for opp in opps_from_leads:
        print(f"   ID: {opp[0]}, Nome: {opp[1]}, Lead: {opp[4]} ({opp[5]}), Creato: {opp[3]}")
    
    print(f"\n📈 Totale opportunità da Lead: {len(opps_from_leads)}")

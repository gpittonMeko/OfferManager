#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica se ci sono opportunità create dai contatti del form"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Cerca opportunità create da contatti/leads del form
    # (opportunità senza offerte associate e con nomi che sembrano essere da form)
    
    opps = db.session.execute(text("""
        SELECT o.id, o.name, o.stage, o.created_at, o.account_id, o.contact_id,
               a.name as account_name, c.first_name, c.last_name, c.email
        FROM opportunities o
        LEFT JOIN accounts a ON o.account_id = a.id
        LEFT JOIN contacts c ON o.contact_id = c.id
        WHERE o.id NOT IN (
            SELECT DISTINCT opportunity_id 
            FROM offers 
            WHERE opportunity_id IS NOT NULL
        )
        ORDER BY o.created_at DESC
        LIMIT 50
    """)).fetchall()
    
    print(f"📊 Opportunità senza offerte associate (ultime 50):\n")
    
    form_keywords = ['contatto', 'form', 'richiesta', 'informazioni', 'robot', 'unitree', 'mir', 'ur']
    
    form_opps = []
    for opp in opps:
        opp_name = opp[1] or ''
        opp_name_lower = opp_name.lower()
        
        # Verifica se sembra essere da form
        is_form = False
        if any(keyword in opp_name_lower for keyword in form_keywords):
            is_form = True
        if opp[5] and opp[6]:  # contact_id e first_name esistono
            is_form = True
        
        if is_form:
            form_opps.append(opp)
            print(f"⚠️  ID: {opp[0]}")
            print(f"   Nome: {opp[1]}")
            print(f"   Stage: {opp[2]}")
            print(f"   Creata: {opp[3]}")
            print(f"   Account: {opp[6]}")
            print(f"   Contatto: {opp[7]} {opp[8]} ({opp[9]})")
            print()
    
    print(f"\n📈 Totale opportunità senza offerte: {len(opps)}")
    print(f"⚠️  Probabili da form: {len(form_opps)}")
    
    if form_opps:
        print(f"\n💡 Suggerimento: Eliminare queste opportunità create dal form?")
        print(f"   ID da eliminare: {[o[0] for o in form_opps]}")

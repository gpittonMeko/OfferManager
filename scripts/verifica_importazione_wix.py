#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica quante opportunità sono state importate da Wix"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Conta opportunità con heat_level fredda_speranza
    total_fredde = db.session.execute(text("""
        SELECT COUNT(*) FROM opportunities WHERE heat_level = 'fredda_speranza'
    """)).fetchone()[0]
    
    # Conta opportunità create di recente (ultimi 7 giorni)
    recent = db.session.execute(text("""
        SELECT COUNT(*) FROM opportunities 
        WHERE heat_level = 'fredda_speranza' 
        AND created_at >= datetime('now', '-7 days')
    """)).fetchone()[0]
    
    print(f"📊 Opportunità 'fredda_speranza': {total_fredde}")
    print(f"📅 Create negli ultimi 7 giorni: {recent}")
    
    # Mostra alcune opportunità recenti
    opps = db.session.execute(text("""
        SELECT o.id, o.name, o.created_at, c.email
        FROM opportunities o
        LEFT JOIN contacts c ON o.contact_id = c.id
        WHERE o.heat_level = 'fredda_speranza'
        ORDER BY o.created_at DESC
        LIMIT 10
    """)).fetchall()
    
    print(f"\n📋 Ultime 10 opportunità importate:")
    for opp in opps:
        print(f"   {opp[1]} ({opp[3]}) - {opp[2]}")

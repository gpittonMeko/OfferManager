#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna database e verifica dati"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app, Opportunity, Lead, Account

with app.app_context():
    db.create_all()
    print("✅ Database aggiornato")
    
    opp_count = Opportunity.query.count()
    lead_count = Lead.query.count()
    ur_opp_count = Opportunity.query.filter_by(supplier_category='Universal Robots').count()
    
    print(f"\n📊 Statistiche:")
    print(f"  Opportunità totali: {opp_count}")
    print(f"  Leads totali: {lead_count}")
    print(f"  Opportunità UR: {ur_opp_count}")
    
    # Mostra alcune opportunità
    opps = Opportunity.query.limit(5).all()
    print(f"\n📋 Prime 5 opportunità:")
    for o in opps:
        print(f"  - {o.name} ({o.supplier_category or 'N/A'}) - Owner: {o.owner_id}")





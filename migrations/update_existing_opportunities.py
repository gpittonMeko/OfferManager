#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna opportunità esistenti con supplier_category"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app, Opportunity

with app.app_context():
    # Aggiorna tutte le opportunità senza supplier_category a 'Universal Robots'
    # (presumendo che quelle esistenti siano da UR)
    updated = 0
    for opp in Opportunity.query.filter((Opportunity.supplier_category == None) | (Opportunity.supplier_category == '')).all():
        opp.supplier_category = 'Universal Robots'
        updated += 1
    
    db.session.commit()
    print(f"✅ Aggiornate {updated} opportunità con supplier_category='Universal Robots'")
    
    # Statistiche finali
    total = Opportunity.query.count()
    ur_count = Opportunity.query.filter_by(supplier_category='Universal Robots').count()
    print(f"\n📊 Statistiche:")
    print(f"  Opportunità totali: {total}")
    print(f"  Opportunità UR: {ur_count}")





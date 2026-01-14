#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conta opportunità con e senza offerte"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    total = db.session.execute(text('SELECT COUNT(*) FROM opportunities')).fetchone()[0]
    with_offers = db.session.execute(text('SELECT COUNT(DISTINCT opportunity_id) FROM offers WHERE opportunity_id IS NOT NULL')).fetchone()[0]
    without_offers = total - with_offers
    
    print(f'📊 Statistiche Opportunità:')
    print(f'   Totale opportunità: {total}')
    print(f'   Con offerte: {with_offers}')
    print(f'   Senza offerte: {without_offers}')
    
    # Mostra alcune opportunità senza offerte
    if without_offers > 0:
        print(f'\n📋 Prime 10 opportunità senza offerte:')
        opps_no_offers = db.session.execute(text("""
            SELECT id, name, stage, created_at 
            FROM opportunities 
            WHERE id NOT IN (SELECT DISTINCT opportunity_id FROM offers WHERE opportunity_id IS NOT NULL)
            ORDER BY created_at DESC
            LIMIT 10
        """)).fetchall()
        for opp in opps_no_offers:
            print(f'   - ID {opp[0]}: {opp[1]} (Stage: {opp[2]}, Creata: {opp[3]})')

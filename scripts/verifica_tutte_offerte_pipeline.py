#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica che tutte le offerte siano incluse nella pipeline"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db, extract_date_from_folder_name, extract_offer_amount
from sqlalchemy import text
from datetime import datetime, date as date_type

with app.app_context():
    # Conta tutte le opportunità con offerte
    total_opps = db.session.execute(text("""
        SELECT COUNT(DISTINCT opportunity_id) 
        FROM offers 
        WHERE opportunity_id IS NOT NULL
    """)).fetchone()[0]
    
    print(f"📊 Totale opportunità con offerte nel DB: {total_opps}\n")
    
    # Carica tutte le opportunità dell'utente admin
    user_id = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()[0]
    
    opps_result = db.session.execute(text("""
        SELECT id, name, stage, amount, probability, created_at, heat_level
        FROM opportunities 
        WHERE owner_id = :user_id
    """), {"user_id": user_id}).fetchall()
    
    print(f"📋 Totale opportunità dell'utente: {len(opps_result)}\n")
    
    # Verifica quante hanno offerte
    opps_with_offers = 0
    opps_with_dates = 0
    opps_in_pipeline = 0
    total_value = 0.0
    total_weighted = 0.0
    
    for row in opps_result:
        opp_id = row[0]
        opp_name = row[1]
        opp_stage = row[2]
        opp_amount = row[3]
        opp_probability = row[4]
        opp_created = row[5]
        opp_heat_level = row[6]
        
        # Carica offerte
        offers = db.session.execute(text("""
            SELECT id, folder_path, amount FROM offers WHERE opportunity_id = :opp_id
        """), {"opp_id": opp_id}).fetchall()
        
        if offers:
            opps_with_offers += 1
            
            # Verifica date
            has_date = False
            for offer in offers:
                if offer[1]:  # folder_path
                    folder_date = extract_date_from_folder_name(offer[1])
                    if folder_date:
                        has_date = True
                        break
            
            if has_date:
                opps_with_dates += 1
            
            # Calcola valore
            opp_value = opp_amount if opp_amount and opp_amount > 0 else 0
            if opp_value == 0:
                for offer in offers:
                    offer_amount = offer[2] if offer[2] and offer[2] > 0 else 0
                    if offer_amount == 0 and offer[1]:
                        offer_amount = extract_offer_amount(type('Offer', (), {'folder_path': offer[1], 'pdf_path': None, 'amount': 0})())
                    opp_value += offer_amount
            
            # Determina probabilità da heat_level
            heat_level = opp_heat_level or 'da_categorizzare'
            if heat_level == 'calda':
                probability = 40
            elif heat_level == 'tiepida':
                probability = 15
            elif heat_level == 'fredda_speranza':
                probability = 5
            elif heat_level == 'fredda_gelo':
                probability = 0
            else:
                probability = 10
            
            if opp_stage not in ['Closed Won', 'Closed Lost']:
                opps_in_pipeline += 1
                total_value += opp_value
                total_weighted += opp_value * (probability / 100.0)
    
    print(f"📈 Statistiche:")
    print(f"  Opportunità con offerte: {opps_with_offers}")
    print(f"  Opportunità con date estratte: {opps_with_dates}")
    print(f"  Opportunità in pipeline (non chiuse): {opps_in_pipeline}")
    print(f"  Valore totale offerte: €{total_value:,.2f}")
    print(f"  Valore pipeline pesato (con probabilità): €{total_weighted:,.2f}")

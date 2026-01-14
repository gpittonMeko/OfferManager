#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica date estratte dalle cartelle"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db, extract_date_from_folder_name
from sqlalchemy import text
from datetime import datetime

with app.app_context():
    # Trova offerte con folder_path
    offers = db.session.execute(text("""
        SELECT id, number, folder_path, opportunity_id, created_at
        FROM offers 
        WHERE folder_path IS NOT NULL AND folder_path != ''
        LIMIT 20
    """)).fetchall()
    
    print(f"📁 Trovate {len(offers)} offerte con folder_path\n")
    
    for offer in offers:
        folder_path = offer[2]
        offer_id = offer[0]
        offer_num = offer[1]
        opp_id = offer[3]
        
        # Estrai data dalla cartella
        folder_date = extract_date_from_folder_name(folder_path)
        
        print(f"Offerta {offer_num} (ID: {offer_id}, Opp: {opp_id})")
        print(f"  Cartella: {folder_path}")
        if folder_date:
            print(f"  ✅ Data estratta: {folder_date} ({type(folder_date).__name__})")
        else:
            print(f"  ❌ Nessuna data estratta")
        print()
    
    # Conta quante offerte hanno date estratte
    total_with_dates = 0
    for offer in offers:
        folder_path = offer[2]
        folder_date = extract_date_from_folder_name(folder_path)
        if folder_date:
            total_with_dates += 1
    
    print(f"\n📊 Statistiche:")
    print(f"  Offerte con folder_path: {len(offers)}")
    print(f"  Offerte con data estratta: {total_with_dates}")
    print(f"  Percentuale: {(total_with_dates/len(offers)*100) if offers else 0:.1f}%")

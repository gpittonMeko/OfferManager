#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug estrazione date"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db, extract_date_from_folder_name
from sqlalchemy import text
from datetime import datetime, date as date_type

with app.app_context():
    # Trova alcune opportunità con offerte
    opps = db.session.execute(text("""
        SELECT o.id, o.name, o.created_at
        FROM opportunities o
        WHERE o.id IN (SELECT DISTINCT opportunity_id FROM offers WHERE folder_path IS NOT NULL LIMIT 5)
    """)).fetchall()
    
    for opp_row in opps:
        opp_id = opp_row[0]
        opp_name = opp_row[1]
        opp_created = opp_row[2]
        
        # Carica offerte
        offers = db.session.execute(text("""
            SELECT folder_path FROM offers WHERE opportunity_id = :opp_id AND folder_path IS NOT NULL LIMIT 1
        """), {"opp_id": opp_id}).fetchall()
        
        print(f"\nOpportunità {opp_id}: {opp_name}")
        print(f"  Created_at: {opp_created}")
        
        if offers:
            folder_path = offers[0][0]
            folder_date = extract_date_from_folder_name(folder_path)
            
            print(f"  Folder: {folder_path}")
            print(f"  Data estratta: {folder_date} (type: {type(folder_date).__name__})")
            
            if folder_date:
                if isinstance(folder_date, date_type):
                    folder_datetime = datetime.combine(folder_date, datetime.min.time())
                else:
                    folder_datetime = folder_date
                
                # Determina periodo
                period_key = folder_datetime.strftime('%Y-%m')
                print(f"  Periodo calcolato: {period_key}")
                print(f"  Usa questa data? {'✅' if folder_datetime else '❌'}")

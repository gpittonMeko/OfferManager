#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test dettagliato pipeline analytics"""
import sys
import os
import json
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
from datetime import datetime, timedelta

with app.app_context():
    from flask.testing import FlaskClient
    client = app.test_client()
    
    with client.session_transaction() as sess:
        user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
        if user:
            sess['user_id'] = user[0]
    
    # Test endpoint
    response = client.get('/api/analytics/pipeline?period=month')
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"Periodi trovati: {len(data.get('data', []))}")
        print(f"Heat counts: {data.get('heat_counts', {})}")
        print(f"Total in pipeline: {data.get('total_in_pipeline', 0)}\n")
        
        # Mostra dettagli per ogni periodo
        print("Dettagli per periodo:")
        for period_data in data.get('data', []):
            period = period_data.get('period', 'N/A')
            total_open = sum(
                period_data.get(cat, {}).get('open', 0) 
                for cat in ['MIR', 'UR', 'Unitree', 'ROEQ', 'Servizi', 'Altro']
            )
            if total_open > 0:
                print(f"\n  {period}:")
                for cat in ['MIR', 'UR', 'Unitree', 'ROEQ', 'Servizi', 'Altro']:
                    open_val = period_data.get(cat, {}).get('open', 0)
                    if open_val > 0:
                        print(f"    {cat}: €{open_val:,.2f}")
        
        # Verifica date estratte
        print("\n\nVerifica date estratte dalle cartelle:")
        end_date = datetime.utcnow()
        start_date = end_date
        for _ in range(6):
            start_date = start_date - timedelta(days=30)
        
        print(f"Range date: {start_date.date()} - {end_date.date()}")
        
        offers_with_dates = db.session.execute(text("""
            SELECT id, folder_path, opportunity_id 
            FROM offers 
            WHERE folder_path IS NOT NULL AND folder_path != ''
            LIMIT 10
        """)).fetchall()
        
        from crm_app_completo import extract_date_from_folder_name
        from datetime import date as date_type
        
        for offer in offers_with_dates:
            folder_path = offer[1]
            folder_date = extract_date_from_folder_name(folder_path)
            if folder_date:
                if isinstance(folder_date, date_type):
                    folder_datetime = datetime.combine(folder_date, datetime.min.time())
                else:
                    folder_datetime = folder_date
                
                in_range = start_date <= folder_datetime <= end_date
                print(f"  Offer {offer[0]}: {folder_date} {'✅' if in_range else '❌'} (in range: {in_range})")
    else:
        print(f"Error: {response.get_data(as_text=True)[:500]}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica completa pipeline"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    from flask.testing import FlaskClient
    client = app.test_client()
    
    with client.session_transaction() as sess:
        user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
        if user:
            sess['user_id'] = user[0]
    
    # Test endpoint
    response = client.get('/api/analytics/pipeline?period=month')
    if response.status_code == 200:
        data = response.get_json()
        
        # Conta opportunità totali con offerte
        total_opps_with_offers = db.session.execute(text("""
            SELECT COUNT(DISTINCT opportunity_id) 
            FROM offers 
            WHERE opportunity_id IS NOT NULL
        """)).fetchone()[0]
        
        print(f"📊 Opportunità con offerte nel DB: {total_opps_with_offers}")
        print(f"📊 Opportunità in pipeline (heat_counts): {data.get('total_in_pipeline', 0)}")
        print(f"📊 Periodi trovati: {len(data.get('data', []))}\n")
        
        # Conta valori per periodo
        total_by_period = {}
        for period_data in data.get('data', []):
            period = period_data.get('period', 'N/A')
            total = sum(
                period_data.get(cat, {}).get('open', 0) 
                for cat in ['MIR', 'UR', 'Unitree', 'ROEQ', 'Servizi', 'Altro']
            )
            if total > 0:
                total_by_period[period] = total
        
        print(f"📈 Valori per periodo (pesati con probabilità):")
        grand_total = 0
        for period, value in sorted(total_by_period.items()):
            print(f"  {period}: €{value:,.2f}")
            grand_total += value
        
        print(f"\n💰 Totale pipeline: €{grand_total:,.2f}")
        
        # Verifica che tutte le opportunità con offerte siano incluse
        if data.get('total_in_pipeline', 0) < total_opps_with_offers:
            print(f"\n⚠️ ATTENZIONE: Solo {data.get('total_in_pipeline', 0)} opportunità in pipeline su {total_opps_with_offers} con offerte!")
        else:
            print(f"\n✅ Tutte le opportunità con offerte sono incluse nella pipeline")

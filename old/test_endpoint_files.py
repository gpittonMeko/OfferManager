#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test dell'endpoint /api/opportunities/<id>/files
per verificare che mostri solo i file delle cartelle specifiche
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Opportunity, User
from sqlalchemy import text

# Trova opportunità con offerte
with app.app_context():
    # Trova opportunità con offerte associate
    result = db.session.execute(text("""
        SELECT DISTINCT o.id, o.name, COUNT(off.id) as offers_count
        FROM opportunities o
        JOIN offers off ON off.opportunity_id = o.id
        GROUP BY o.id, o.name
        HAVING COUNT(off.id) > 0
        ORDER BY o.id
        LIMIT 3
    """))
    
    opps = result.fetchall()
    
    print("="*80)
    print("TEST ENDPOINT FILE OFFERTE")
    print("="*80)
    
    for opp_row in opps:
        opp_id = opp_row[0]
        opp_name = opp_row[1]
        offers_count = opp_row[2]
        
        print(f"\n{'='*80}")
        print(f"Opportunita: {opp_name} (ID: {opp_id})")
        print(f"Offerte associate: {offers_count}")
        
        # Simula chiamata API
        with app.test_request_context('/api/opportunities/{}/files'.format(opp_id)):
            # Simula login admin
            from flask import session
            admin_user = db.session.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1")).fetchone()
            if admin_user:
                session['user_id'] = admin_user[0]
                
                # Chiama la funzione direttamente
                from crm_app_completo import get_opportunity_files
                try:
                    response = get_opportunity_files(opp_id)
                    data = response.get_json()
                    
                    print(f"\nFile trovati: {data.get('files_found', 0)}")
                    print(f"Cartelle verificate: {len(data.get('folders_checked', []))}")
                    
                    if data.get('files_found', 0) > 20:
                        print(f"⚠️  PROBLEMA: Trovati {data.get('files_found', 0)} file (troppi!)")
                        print(f"   Dovrebbero essere solo i file delle cartelle specifiche delle offerte")
                    
                    # Mostra info debug
                    if data.get('debug_info'):
                        print(f"\nDebug info (ultime 10 righe):")
                        for line in data['debug_info'][-10:]:
                            print(f"  {line}")
                    
                    # Mostra prime 5 cartelle verificate
                    if data.get('folders_checked'):
                        print(f"\nCartelle verificate:")
                        for folder in data['folders_checked'][:5]:
                            folder_name = os.path.basename(folder)
                            print(f"  • {folder_name}")
                            if folder_name in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']:
                                print(f"    ⚠️  PROBLEMA: Cartella principale invece di specifica!")
                    
                    # Mostra prime 10 file
                    if data.get('files'):
                        print(f"\nPrime 10 file trovati:")
                        for file in data['files'][:10]:
                            print(f"  • {file.get('name')} (Cartella: {file.get('folder', 'N/A')})")
                    
                except Exception as e:
                    print(f"❌ Errore: {e}")
                    import traceback
                    traceback.print_exc()

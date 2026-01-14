#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test specifico per offerta K1651-25"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db
from sqlalchemy import text

# Trova opportunità con offerta K1651-25
with app.app_context():
    # Trova offerta K1651-25
    offer_result = db.session.execute(text("""
        SELECT id, number, folder_path, opportunity_id
        FROM offers 
        WHERE number LIKE '%1651%'
    """)).fetchone()
    
    if offer_result:
        offer_id, number, folder_path, opp_id = offer_result
        print("="*80)
        print(f"TEST OFFERTA K1651-25")
        print("="*80)
        print(f"\nOfferta ID: {offer_id}")
        print(f"Numero: {number}")
        print(f"Cartella: {folder_path}")
        print(f"Opportunita ID: {opp_id}")
        
        # Simula chiamata API
        with app.test_request_context('/api/opportunities/{}/files'.format(opp_id)):
            from flask import session
            admin_user = db.session.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1")).fetchone()
            if admin_user:
                session['user_id'] = admin_user[0]
                
                from crm_app_completo import get_opportunity_files
                try:
                    response = get_opportunity_files(opp_id)
                    data = response.get_json()
                    
                    print(f"\n{'='*80}")
                    print(f"RISULTATI CHIAMATA API")
                    print(f"{'='*80}")
                    print(f"\nFile trovati: {data.get('files_found', 0)}")
                    print(f"Offerte associate: {data.get('offers_count', 0)}")
                    print(f"Cartelle verificate: {len(data.get('folders_checked', []))}")
                    
                    if data.get('files_found', 0) > 50:
                        print(f"\n⚠️  PROBLEMA: Trovati {data.get('files_found', 0)} file (troppi!)")
                        print(f"   Dovrebbero essere solo i file delle cartelle specifiche")
                    else:
                        print(f"\n✅ OK: Trovati {data.get('files_found', 0)} file (corretto)")
                    
                    print(f"\nCartelle verificate:")
                    for folder in data.get('folders_checked', []):
                        folder_name = os.path.basename(folder)
                        print(f"  • {folder_name}")
                    
                    print(f"\nFile trovati:")
                    for file in data.get('files', [])[:10]:
                        print(f"  • {file.get('name')} (Cartella: {file.get('folder', 'N/A')})")
                    
                    if len(data.get('files', [])) > 10:
                        print(f"  ... e altri {len(data.get('files', [])) - 10} file")
                    
                except Exception as e:
                    print(f"❌ Errore: {e}")
                    import traceback
                    traceback.print_exc()
    else:
        print("Offerta K1651-25 non trovata")

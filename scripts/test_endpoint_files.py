#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test endpoint /api/opportunities/<id>/files"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
from flask import session

def test_get_opportunity_files(opportunity_id):
    """Test funzione get_opportunity_files"""
    with app.app_context():
        # Simula sessione utente
        with app.test_request_context():
            # Trova un utente admin
            user_result = db.session.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
            if user_result:
                session['user_id'] = user_result[0]
                
                # Importa e chiama la funzione
                from crm_app_completo import get_opportunity_files
                from flask import jsonify
                
                try:
                    response = get_opportunity_files(opportunity_id)
                    if hasattr(response, 'get_json'):
                        data = response.get_json()
                        print(f"✅ Test completato!")
                        print(f"  Offerte trovate: {data.get('offers_count', 0)}")
                        print(f"  File trovati: {data.get('files_found', 0)}")
                        print(f"  Debug info: {len(data.get('debug_info', []))} messaggi")
                        if data.get('debug_info'):
                            print("\n  Messaggi debug:")
                            for msg in data.get('debug_info', []):
                                if any(keyword in msg.lower() for keyword in ['configurazione', 'server', 'ip', 'share', 'utente', 'default']):
                                    print(f"    - {msg}")
                        return True
                    else:
                        print(f"❌ Risposta non valida: {response}")
                        return False
                except Exception as e:
                    print(f"❌ Errore durante il test: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("❌ Nessun utente trovato nel database")
                return False

if __name__ == '__main__':
    opp_id = int(sys.argv[1]) if len(sys.argv) > 1 else 127
    print(f"Test endpoint files per opportunità {opp_id}...")
    test_get_opportunity_files(opp_id)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test simulando Linux per verificare generazione link SMB"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import platform

# Simula Linux
original_system = platform.system
platform.system = lambda: 'Linux'

def test_k1550_linux():
    """Test endpoint files per K1550-25 simulando Linux"""
    with app.app_context():
        with app.test_client() as client:
            # Trova utente admin
            user = db.session.execute(text("""
                SELECT id, username FROM users WHERE username = 'admin' LIMIT 1
            """)).fetchone()
            
            if not user:
                print("ERRORE: Utente admin non trovato")
                return False
            
            # Trova opportunità K1550-25
            opp = db.session.execute(text("""
                SELECT id, name FROM opportunities 
                WHERE name LIKE '%K1550%'
                ORDER BY id
            """)).fetchone()
            
            if not opp:
                print("ERRORE: Opportunità K1550-25 non trovata")
                return False
            
            opp_id = opp[0]
            opp_name = opp[1]
            
            print(f"OK Opportunità trovata: ID={opp_id}, Nome={opp_name}")
            print(f"Simulazione: Platform={platform.system()}")
            
            # Simula sessione loggata
            with client.session_transaction() as sess:
                sess['user_id'] = user[0]
            
            # Chiama endpoint files
            response = client.get(f'/api/opportunities/{opp_id}/files')
            
            if response.status_code != 200:
                print(f"ERRORE: Status code {response.status_code}")
                print(response.get_data(as_text=True))
                return False
            
            data = response.get_json()
            
            print(f"\nRISPOSTA ENDPOINT:")
            print(f"  File trovati: {data.get('files_found', 0)}")
            print(f"  Offerte associate: {data.get('offers_count', 0)}")
            print(f"  File nella lista: {len(data.get('files', []))}")
            
            if data.get('files'):
                print(f"\nFILE/LINK TROVATI:")
                has_smb = False
                for i, f in enumerate(data['files'], 1):
                    print(f"\n  {i}. {f.get('name')}")
                    print(f"     Tipo: {f.get('type')}")
                    print(f"     Estensione: {f.get('extension')}")
                    if f.get('smb_path'):
                        print(f"     SMB Path: {f.get('smb_path')}")
                        has_smb = True
                    if f.get('is_folder_link'):
                        print(f"     [LINK CARTELLA SMB]")
                        has_smb = True
                
                if has_smb:
                    print(f"\nOK LINK SMB GENERATI CORRETTAMENTE!")
                    return True
                else:
                    print(f"\nERRORE: Nessun link SMB generato!")
                    return False
            else:
                print(f"\nERRORE: NESSUN FILE/LINK TROVATO")
                return False

if __name__ == '__main__':
    print("=" * 60)
    print("TEST SIMULAZIONE LINUX - K1550-25")
    print("=" * 60)
    
    try:
        success = test_k1550_linux()
        
        print("\n" + "=" * 60)
        if success:
            print("OK TEST COMPLETATO CON SUCCESSO")
        else:
            print("ERRORE TEST FALLITO")
        print("=" * 60)
    finally:
        # Ripristina platform.system
        platform.system = original_system

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test COMPLETO endpoint K1550-25 simulando browser"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import re

def test_k1550_endpoint():
    """Test completo endpoint files per K1550-25"""
    with app.app_context():
        with app.test_client() as client:
            # Simula login creando sessione
            # Prima trova l'utente admin
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
                print(f"\nFILE TROVATI:")
                for i, f in enumerate(data['files'], 1):
                    print(f"\n  {i}. {f.get('name')}")
                    print(f"     Tipo: {f.get('type')}")
                    print(f"     Estensione: {f.get('extension')}")
                    if f.get('smb_path'):
                        print(f"     SMB Path: {f.get('smb_path')}")
                    if f.get('is_folder_link'):
                        print(f"     [LINK CARTELLA]")
                return True
            else:
                print(f"\nERRORE: NESSUN FILE TROVATO")
                print(f"\nDettagli:")
                print(f"  Offerte associate: {data.get('offers_count', 0)}")
                
                # Verifica perché non ha trovato file
                offers = db.session.execute(text("""
                    SELECT id, number, folder_path, pdf_path, docx_path 
                    FROM offers 
                    WHERE opportunity_id = :opp_id
                """), {"opp_id": opp_id}).fetchall()
                
                print(f"\nVerifica offerte nel DB:")
                for off in offers:
                    print(f"  - {off[1]}: folder={off[2]}, pdf={off[3]}, docx={off[4]}")
                
                # Verifica associazione automatica
                match = re.search(r'K(\d{4})-(\d{2})', opp_name)
                if match:
                    offer_number = match.group(0)
                    print(f"\nNumero offerta estratto: {offer_number}")
                    
                    matching_offer = db.session.execute(text("""
                        SELECT id, number, folder_path, opportunity_id 
                        FROM offers 
                        WHERE number = :offer_number
                    """), {"offer_number": offer_number}).fetchone()
                    
                    if matching_offer:
                        print(f"Offerta trovata: ID={matching_offer[0]}, associata a opp_id={matching_offer[3]}")
                        if matching_offer[3] != opp_id:
                            print(f"PROBLEMA: Offerta associata a opportunità diversa!")
                            return False
                
                return False

if __name__ == '__main__':
    print("=" * 60)
    print("TEST COMPLETO K1550-25")
    print("=" * 60)
    
    success = test_k1550_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("OK TEST COMPLETATO CON SUCCESSO")
    else:
        print("ERRORE TEST FALLITO")
    print("=" * 60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test download file SMB"""
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
    
    # Trova un'opportunità con file
    opp = db.session.execute(text("""
        SELECT id FROM opportunities 
        WHERE id IN (SELECT opportunity_id FROM offers WHERE folder_path IS NOT NULL LIMIT 1)
        LIMIT 1
    """)).fetchone()
    
    if opp:
        opp_id = opp[0]
        # Chiama endpoint files
        response = client.get(f'/api/opportunities/{opp_id}/files')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('files'):
                first_file = data['files'][0]
                filename = first_file['name']
                print(f"Test download file: {filename}")
                
                # Testa endpoint download
                download_response = client.get(f'/api/opportunities/{opp_id}/files/{filename}')
                print(f"Status: {download_response.status_code}")
                print(f"Content-Type: {download_response.content_type}")
                
                if download_response.status_code == 200:
                    if 'text/html' in download_response.content_type:
                        content = download_response.get_data(as_text=True)
                        if 'Percorso copiato' in content or 'Apertura Cartella' in content:
                            print("OK Pagina HTML generata correttamente")
                        else:
                            print(f"ERRORE: Contenuto HTML non valido: {content[:200]}")
                    else:
                        print("OK File scaricato direttamente")
                else:
                    print(f"ERRORE: Status {download_response.status_code}")
                    print(download_response.get_data(as_text=True)[:200])
            else:
                print("ERRORE: Nessun file trovato")
        else:
            print(f"ERRORE: Status {response.status_code}")
    else:
        print("ERRORE: Nessuna opportunità con file trovata")

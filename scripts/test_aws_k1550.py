#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test endpoint K1550-25 sul server AWS"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
import platform
import json

with app.app_context():
    print("Platform:", platform.system())
    
    # Trova opportunita K1550-25
    opp = db.session.execute(text("""
        SELECT id, name FROM opportunities 
        WHERE name LIKE '%K1550%'
        LIMIT 1
    """)).fetchone()
    
    if not opp:
        print("ERRORE: Opportunita K1550-25 non trovata")
        sys.exit(1)
    
    print(f"OK Opportunita: ID={opp[0]}, Nome={opp[1]}")
    
    # Trova offerte associate
    offers = db.session.execute(text("""
        SELECT id, number, folder_path, pdf_path, docx_path 
        FROM offers 
        WHERE opportunity_id = :opp_id
    """), {"opp_id": opp[0]}).fetchall()
    
    print(f"Offerte associate: {len(offers)}")
    for off in offers:
        print(f"  - {off[1]}: folder={off[2]}")
    
    # Simula chiamata endpoint
    from flask import session
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # Trova utente admin
            user = db.session.execute(text("""
                SELECT id FROM users WHERE username = 'admin' LIMIT 1
            """)).fetchone()
            if user:
                sess['user_id'] = user[0]
        
        response = client.get(f'/api/opportunities/{opp[0]}/files')
        data = response.get_json()
        
        print(f"\nRISPOSTA ENDPOINT:")
        print(f"  Status: {response.status_code}")
        print(f"  File trovati: {data.get('files_found', 0)}")
        print(f"  Offerte associate: {data.get('offers_count', 0)}")
        print(f"  File nella lista: {len(data.get('files', []))}")
        
        if data.get('files'):
            has_smb = False
            print("\nFile trovati:")
            for f in data['files']:
                print(f"  - {f.get('name')}: tipo={f.get('type')}, smb={bool(f.get('smb_path'))}")
                if f.get('smb_path') or f.get('is_folder_link'):
                    has_smb = True
                    print(f"    SMB Path: {f.get('smb_path')}")
            
            if has_smb:
                print("\nOK LINK SMB GENERATI!")
                sys.exit(0)
            else:
                print("\nERRORE: Nessun link SMB!")
                sys.exit(1)
        else:
            print("\nERRORE: Nessun file trovato!")
            print(json.dumps(data, indent=2))
            sys.exit(1)

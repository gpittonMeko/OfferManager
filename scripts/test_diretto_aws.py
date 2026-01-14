#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test DIRETTO sul server AWS via SSH"""
import subprocess
import sys

print("=" * 70)
print("TEST DIRETTO SERVER AWS - K1550-25")
print("=" * 70)

# Crea script Python da eseguire sul server
script = '''
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
import platform

with app.app_context():
    print("Platform:", platform.system())
    
    # Trova opportunità K1550-25
    opp = db.session.execute(text("""
        SELECT id, name FROM opportunities 
        WHERE name LIKE '%K1550%'
        LIMIT 1
    """)).fetchone()
    
    if not opp:
        print("ERRORE: Opportunità K1550-25 non trovata")
        sys.exit(1)
    
    print(f"OK Opportunità: ID={opp[0]}, Nome={opp[1]}")
    
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
        
        print(f"\\nRISPOSTA ENDPOINT:")
        print(f"  Status: {response.status_code}")
        print(f"  File trovati: {data.get('files_found', 0)}")
        print(f"  Offerte associate: {data.get('offers_count', 0)}")
        print(f"  File nella lista: {len(data.get('files', []))}")
        
        if data.get('files'):
            has_smb = False
            for f in data['files']:
                if f.get('smb_path') or f.get('is_folder_link'):
                    has_smb = True
                    print(f"  - {f.get('name')}: SMB={f.get('smb_path')}")
            
            if has_smb:
                print("\\nOK LINK SMB GENERATI!")
                sys.exit(0)
            else:
                print("\\nERRORE: Nessun link SMB!")
                print("File trovati:")
                for f in data['files']:
                    print(f"  - {f.get('name')}: {f.get('type')}")
                sys.exit(1)
        else:
            print("\\nERRORE: Nessun file trovato!")
            print(json.dumps(data, indent=2))
            sys.exit(1)
'''

# Esegui script sul server
cmd = [
    'ssh', '-i', 'C:\\Users\\user\\Documents\\LLM_14.pem',
    'ubuntu@13.53.183.146',
    'cd /home/ubuntu/offermanager && source venv/bin/activate && python3'
]

try:
    result = subprocess.run(
        cmd,
        input=script,
        text=True,
        capture_output=True,
        timeout=30
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("OK TEST COMPLETATO CON SUCCESSO")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("ERRORE TEST FALLITO")
        print("=" * 70)
        sys.exit(1)
        
except Exception as e:
    print(f"ERRORE esecuzione: {e}")
    sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test FINALE COMPLETO - Tutto deve funzionare"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

print("=" * 70)
print("TEST FINALE COMPLETO")
print("=" * 70)

errors = []

with app.app_context():
    # 1. Test Dashboard
    print("\n1. Test Dashboard...")
    try:
        from flask.testing import FlaskClient
        client = app.test_client()
        
        with client.session_transaction() as sess:
            user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
            if user:
                sess['user_id'] = user[0]
        
        response = client.get('/api/dashboard/summary')
        if response.status_code == 200:
            data = response.get_json()
            if data and 'metrics' in data:
                print("OK Dashboard funziona")
            else:
                errors.append("Dashboard: risposta non valida")
        else:
            errors.append(f"Dashboard: Status {response.status_code}")
    except Exception as e:
        errors.append(f"Dashboard: {str(e)}")
    
    # 2. Test Endpoint Files K1550-25
    print("\n2. Test Endpoint Files K1550-25...")
    try:
        opp = db.session.execute(text("""
            SELECT id FROM opportunities WHERE name LIKE '%K1550%' LIMIT 1
        """)).fetchone()
        
        if opp:
            response = client.get(f'/api/opportunities/{opp[0]}/files')
            if response.status_code == 200:
                data = response.get_json()
                if data and 'files' in data:
                    files_with_smb = [f for f in data.get('files', []) if f.get('smb_path') or f.get('is_folder_link')]
                    if files_with_smb:
                        print(f"OK Endpoint files: {len(files_with_smb)} file con link SMB")
                    else:
                        errors.append("Endpoint files: nessun link SMB generato")
                else:
                    errors.append("Endpoint files: risposta non valida")
            else:
                errors.append(f"Endpoint files: Status {response.status_code}")
        else:
            errors.append("Endpoint files: K1550-25 non trovata")
    except Exception as e:
        errors.append(f"Endpoint files: {str(e)}")
    
    # 3. Test Frontend
    print("\n3. Test Frontend...")
    try:
        template_path = '/home/ubuntu/offermanager/templates/app_mekocrm_completo.html'
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'smbPath' in content and 'downloadOpportunityFile' in content:
                print("OK Frontend gestisce link SMB")
            else:
                errors.append("Frontend: non gestisce link SMB")
        else:
            errors.append("Frontend: template non trovato")
    except Exception as e:
        errors.append(f"Frontend: {str(e)}")

print("\n" + "=" * 70)
if errors:
    print("ERRORE: Test falliti:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("TUTTI I TEST PASSATI!")
    print("=" * 70)
    print("\nSistema pronto e funzionante:")
    print("  - Dashboard: OK")
    print("  - Endpoint files: OK")
    print("  - Link SMB: OK")
    print("  - Frontend: OK")
    sys.exit(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test TUTTI gli endpoint che potrebbero essere chiamati dalla dashboard"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

print("=" * 70)
print("TEST TUTTI GLI ENDPOINT DASHBOARD")
print("=" * 70)

errors = []

with app.app_context():
    from flask.testing import FlaskClient
    client = app.test_client()
    
    with client.session_transaction() as sess:
        user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
        if user:
            sess['user_id'] = user[0]
    
    # 1. Dashboard summary
    print("\n1. Test /api/dashboard/summary...")
    try:
        response = client.get('/api/dashboard/summary')
        if response.status_code == 200:
            data = response.get_json()
            if data and 'metrics' in data:
                print("OK Dashboard summary")
            else:
                errors.append("Dashboard summary: risposta non valida")
        else:
            errors.append(f"Dashboard summary: Status {response.status_code}")
    except Exception as e:
        errors.append(f"Dashboard summary: {str(e)}")
    
    # 2. Analytics pipeline
    print("\n2. Test /api/analytics/pipeline?period=month...")
    try:
        response = client.get('/api/analytics/pipeline?period=month')
        if response.status_code == 200:
            data = response.get_json()
            if data and ('data' in data or isinstance(data, list)):
                print("OK Analytics pipeline")
            else:
                errors.append("Analytics pipeline: risposta non valida")
        else:
            errors.append(f"Analytics pipeline: Status {response.status_code}")
            print(response.get_data(as_text=True)[:200])
    except Exception as e:
        errors.append(f"Analytics pipeline: {str(e)}")
    
    # 3. Opportunities list
    print("\n3. Test /api/opportunities?limit=10&sort=created_at...")
    try:
        response = client.get('/api/opportunities?limit=10&sort=created_at')
        if response.status_code == 200:
            data = response.get_json()
            if data and 'opportunities' in data:
                print("OK Opportunities list")
            else:
                errors.append("Opportunities list: risposta non valida")
        else:
            errors.append(f"Opportunities list: Status {response.status_code}")
            print(response.get_data(as_text=True)[:200])
    except Exception as e:
        errors.append(f"Opportunities list: {str(e)}")
    
    # 4. Files endpoint (già testato)
    print("\n4. Test /api/opportunities/127/files...")
    try:
        response = client.get('/api/opportunities/127/files')
        if response.status_code == 200:
            data = response.get_json()
            if data and 'files' in data:
                files_with_smb = [f for f in data.get('files', []) if f.get('smb_path')]
                if files_with_smb:
                    print(f"OK Files endpoint: {len(files_with_smb)} file con SMB")
                else:
                    errors.append("Files endpoint: nessun link SMB")
            else:
                errors.append("Files endpoint: risposta non valida")
        else:
            errors.append(f"Files endpoint: Status {response.status_code}")
    except Exception as e:
        errors.append(f"Files endpoint: {str(e)}")

print("\n" + "=" * 70)
if errors:
    print("ERRORE: Test falliti:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("TUTTI I TEST PASSATI!")
    print("=" * 70)
    sys.exit(0)

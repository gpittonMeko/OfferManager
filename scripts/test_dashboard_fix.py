#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test fix dashboard"""
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
    
    response = client.get('/api/dashboard/summary')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        if data and 'metrics' in data:
            print("OK Dashboard funziona!")
            print(f"Metrics: {data['metrics']}")
            sys.exit(0)
        else:
            print("ERRORE: Risposta non valida")
            print(data)
            sys.exit(1)
    else:
        print(f"ERRORE: Status {response.status_code}")
        print(response.get_data(as_text=True))
        sys.exit(1)

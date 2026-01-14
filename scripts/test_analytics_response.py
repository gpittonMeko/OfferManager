#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test risposta analytics pipeline"""
import sys
import os
import json
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
    
    response = client.get('/api/analytics/pipeline?period=month')
    print(f"Status: {response.status_code}")
    data = response.get_json()
    print(f"Type: {type(data)}")
    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
    if isinstance(data, list):
        print(f"Length: {len(data)}")
    print(f"Sample: {json.dumps(data, indent=2)[:1000]}")

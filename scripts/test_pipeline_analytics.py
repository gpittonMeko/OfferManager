#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test pipeline analytics endpoint"""
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
    
    # Test endpoint
    response = client.get('/api/analytics/pipeline?period=month')
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.get_data(as_text=True)[:500]}")
    else:
        data = response.get_json()
        print(f"Success: {len(data.get('data', []))} periods")
        print(f"Heat counts: {data.get('heat_counts', {})}")

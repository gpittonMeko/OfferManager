#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità ID 187 e configurazione admin"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Verifica opportunità 187
    opp187 = db.session.execute(text("SELECT id, name FROM opportunities WHERE id = 187")).fetchone()
    print(f"Opportunità ID 187: {opp187}")
    
    # Verifica opportunità 19
    opp19 = db.session.execute(text("SELECT id, name FROM opportunities WHERE id = 19")).fetchone()
    print(f"Opportunità ID 19: {opp19}")
    
    # Verifica offerte K0192
    offers = db.session.execute(text("SELECT id, number, opportunity_id FROM offers WHERE number LIKE '%K0192%'")).fetchall()
    print(f"\nOfferte K0192:")
    for o in offers:
        print(f"  ID: {o[0]}, Numero: {o[1]}, Opp ID: {o[2]}")
    
    # Verifica offerte per opportunità 187
    offers187 = db.session.execute(text("SELECT id, number, opportunity_id FROM offers WHERE opportunity_id = 187")).fetchall()
    print(f"\nOfferte per opportunità 187: {len(offers187)}")
    for o in offers187:
        print(f"  ID: {o[0]}, Numero: {o[1]}, Opp ID: {o[2]}")
    
    # Verifica configurazione admin
    user = db.session.execute(text("SELECT id, username, local_pc_ip, local_pc_share FROM users WHERE username = 'admin'")).fetchone()
    if user:
        print(f"\nUtente admin:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  IP: {user[2]}")
        print(f"  Share: {user[3]}")

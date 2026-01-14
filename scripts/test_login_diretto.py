#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test login diretto"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text
from werkzeug.security import check_password_hash

with app.app_context():
    # Ottieni utente admin
    user = db.session.execute(text("SELECT id, username, password FROM users WHERE username='admin'")).fetchone()
    if user:
        print(f"Utente trovato: ID={user[0]}, Username='{user[1]}'")
        print(f"Password hash: {user[2][:50]}...")
        
        # Testa diverse password
        passwords_to_test = ['admin', 'Admin', 'ADMIN', 'password', 'Password', '123456']
        for pwd in passwords_to_test:
            if check_password_hash(user[2], pwd):
                print(f"✓ Password corretta: '{pwd}'")
                break
        else:
            print("✗ Nessuna password corrisponde tra quelle testate")
    else:
        print("Utente 'admin' non trovato")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resetta password di un utente"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import User, db, app
from werkzeug.security import generate_password_hash

if len(sys.argv) < 3:
    print("Uso: python reset_user_password.py <username> <nuova_password>")
    print("Esempio: python reset_user_password.py admin nuovaPassword123")
    sys.exit(1)

username = sys.argv[1]
new_password = sys.argv[2]

with app.app_context():
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        print(f"✅ Password resettata per utente: {username}")
        print(f"   Nuova password: {new_password}")
        print(f"   Nome: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
    else:
        print(f"❌ Utente '{username}' non trovato")
        print("\nUtenti disponibili:")
        users = User.query.all()
        for u in users:
            print(f"  - {u.username} ({u.first_name} {u.last_name})")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista tutti gli utenti con informazioni"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import User, db, app

with app.app_context():
    users = User.query.all()
    print("=" * 80)
    print("UTENTI NEL DATABASE - CREDENZIALI")
    print("=" * 80)
    print()
    
    for u in users:
        print(f"ID: {u.id}")
        print(f"  Username: {u.username}")
        print(f"  Nome: {u.first_name} {u.last_name}")
        print(f"  Email: {u.email}")
        print(f"  Ruolo: {u.role}")
        print(f"  Password: [HASHATA - Non recuperabile]")
        print(f"  Creato: {u.created_at}")
        print("-" * 80)
    
    print()
    print(f"Totale: {len(users)} utenti")
    print("=" * 80)
    print()
    print("NOTA: Le password sono hashate e non possono essere recuperate.")
    print("Per resettare una password, usa lo script reset_user_password.py")

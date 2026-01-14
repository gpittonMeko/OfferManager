#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea o aggiorna utente Mauro Zanet"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    username = 'mauro'
    password = 'mauro2025'
    
    existing = User.query.filter_by(username=username).first()
    if existing:
        # Aggiorna utente esistente
        existing.password = generate_password_hash(password)
        existing.first_name = 'Mauro'
        existing.last_name = 'Zanet'
        existing.email = 'mauro.zanet@mekosrl.it'
        existing.role = 'commerciale'
        db.session.commit()
        print(f"🔄 Utente {username} aggiornato")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Nome: Mauro Zanet")
        print(f"   Ruolo: commerciale")
    else:
        # Crea nuovo utente
        user = User(
            username=username,
            password=generate_password_hash(password),
            first_name='Mauro',
            last_name='Zanet',
            email='mauro.zanet@mekosrl.it',
            role='commerciale'
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Utente {username} creato")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Nome: Mauro Zanet")
        print(f"   Ruolo: commerciale")
    
    print("\n✅ Operazione completata!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea utenti Fima, Filippo, Mariuzzo"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    users_to_create = [
        {
            'username': 'fima',
            'first_name': 'Fima',
            'last_name': 'User',
            'email': 'fima@mekosrl.it',
            'role': 'commerciale',
            'password': 'fima2025'
        },
        {
            'username': 'filippo',
            'first_name': 'Filippo',
            'last_name': 'User',
            'email': 'filippo@mekosrl.it',
            'role': 'commerciale',
            'password': 'filippo2025'
        },
        {
            'username': 'mariuzzo',
            'first_name': 'Mariuzzo',
            'last_name': 'User',
            'email': 'mariuzzo@mekosrl.it',
            'role': 'commerciale',
            'password': 'mariuzzo2025'
        }
    ]
    
    for user_data in users_to_create:
        existing = User.query.filter_by(username=user_data['username']).first()
        if existing:
            print(f"⚠️  Utente {user_data['username']} già esistente")
        else:
            user = User(
                username=user_data['username'],
                password=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                role=user_data['role']
            )
            db.session.add(user)
            print(f"✅ Utente {user_data['username']} creato")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
    
    db.session.commit()
    print("\n✅ Tutti gli utenti creati!")





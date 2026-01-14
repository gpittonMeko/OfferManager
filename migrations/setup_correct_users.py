#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea solo gli utenti richiesti: filippo, mariuzzo, giovanni pitton, davide cal, mauro zanet + admin"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Lista utenti richiesti
    required_users = [
        {
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'System',
            'email': 'admin@mekosrl.it',
            'role': 'admin',
            'password': 'admin'
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
        },
        {
            'username': 'giovanni',
            'first_name': 'Giovanni',
            'last_name': 'Pitton',
            'email': 'giovanni.pitton@mekosrl.it',
            'role': 'commerciale',
            'password': 'giovanni2025'
        },
        {
            'username': 'davide',
            'first_name': 'Davide',
            'last_name': 'Cal',
            'email': 'davide.cal@mekosrl.it',
            'role': 'commerciale',
            'password': 'davide2025'
        },
        {
            'username': 'mauro',
            'first_name': 'Mauro',
            'last_name': 'Zanet',
            'email': 'mauro.zanet@mekosrl.it',
            'role': 'commerciale',
            'password': 'mauro2025'
        }
    ]
    
    # Ottieni tutti gli username richiesti
    required_usernames = {u['username'] for u in required_users}
    
    # Rimuovi utenti non richiesti
    print("🗑️  Rimozione utenti non necessari...")
    all_users = User.query.all()
    removed = 0
    for user in all_users:
        if user.username not in required_usernames:
            print(f"  ❌ Rimozione: {user.username}")
            db.session.delete(user)
            removed += 1
    
    if removed > 0:
        db.session.commit()
        print(f"✅ Rimossi {removed} utenti")
    
    # Crea/aggiorna utenti richiesti
    print("\n👥 Creazione/Aggiornamento utenti richiesti...")
    created = 0
    updated = 0
    
    for user_data in required_users:
        existing = User.query.filter_by(username=user_data['username']).first()
        if existing:
            # Aggiorna utente esistente
            existing.password = generate_password_hash(user_data['password'])
            existing.first_name = user_data['first_name']
            existing.last_name = user_data['last_name']
            existing.email = user_data['email']
            existing.role = user_data['role']
            updated += 1
            print(f"  🔄 {user_data['username']}: aggiornato")
        else:
            # Crea nuovo utente
            user = User(
                username=user_data['username'],
                password=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                role=user_data['role']
            )
            db.session.add(user)
            created += 1
            print(f"  ✅ {user_data['username']}: creato")
    
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("✅ COMPLETATO")
    print("=" * 60)
    print(f"Creati: {created}, Aggiornati: {updated}, Rimossi: {removed}")
    print(f"Totale utenti finali: {User.query.count()}")
    print("\nUtenti finali:")
    for u in User.query.order_by(User.username).all():
        print(f"  - {u.username} ({u.first_name} {u.last_name})")





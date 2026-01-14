#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica e corregge tutti gli utenti con le password corrette"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    # Lista utenti corretti con password
    users_config = [
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
    
    print("=" * 80)
    print("VERIFICA E CORREZIONE UTENTI")
    print("=" * 80)
    print()
    
    # Rimuovi utenti duplicati o non validi
    fima_user = User.query.filter_by(username='fima').first()
    if fima_user:
        db.session.delete(fima_user)
        db.session.commit()
        print("❌ Utente 'fima' rimosso")
        print()
    
    # Rimuovi duplicati di filippo (mantieni solo quello con ruolo commerciale)
    filippo_users = User.query.filter_by(username='filippo').all()
    if len(filippo_users) > 1:
        print(f"⚠️ Trovati {len(filippo_users)} utenti 'filippo', rimuovo i duplicati...")
        # Mantieni solo il primo con ruolo commerciale, elimina gli altri
        kept = None
        for f in filippo_users:
            if f.role == 'commerciale':
                if kept is None:
                    kept = f
                else:
                    db.session.delete(f)
                    print(f"  ❌ Rimosso duplicato filippo (ID: {f.id}, ruolo: {f.role})")
            else:
                db.session.delete(f)
                print(f"  ❌ Rimosso filippo con ruolo errato (ID: {f.id}, ruolo: {f.role})")
        db.session.commit()
        print()
    
    # Verifica e aggiorna/crea tutti gli utenti
    for user_data in users_config:
        existing = User.query.filter_by(username=user_data['username']).first()
        
        if existing:
            # Verifica se la password è corretta
            password_ok = check_password_hash(existing.password, user_data['password'])
            
            if not password_ok:
                # Reset password
                existing.password = generate_password_hash(user_data['password'])
                print(f"🔄 Password resettata per: {user_data['username']}")
            else:
                print(f"✅ Password OK per: {user_data['username']}")
            
            # Aggiorna altri dati
            existing.first_name = user_data['first_name']
            existing.last_name = user_data['last_name']
            existing.email = user_data['email']
            existing.role = user_data['role']
            
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
            print(f"✅ Creato nuovo utente: {user_data['username']}")
    
    db.session.commit()
    
    print()
    print("=" * 80)
    print("TEST CREDENZIALI")
    print("=" * 80)
    print()
    
    # Testa tutte le credenziali
    for user_data in users_config:
        user = User.query.filter_by(username=user_data['username']).first()
        if user:
            password_valid = check_password_hash(user.password, user_data['password'])
            status = "✅ OK" if password_valid else "❌ ERRORE"
            print(f"{status} Username: {user_data['username']:15} Password: {user_data['password']:15} Email: {user_data['email']}")
        else:
            print(f"❌ ERRORE Username: {user_data['username']:15} - UTENTE NON TROVATO")
    
    print()
    print("=" * 80)
    print("RIEPILOGO UTENTI FINALI")
    print("=" * 80)
    print()
    
    all_users = User.query.all()
    for u in all_users:
        print(f"  - {u.username:15} | {u.first_name} {u.last_name:20} | {u.email:30} | {u.role}")
    
    print()
    print(f"Totale: {len(all_users)} utenti")
    print("=" * 80)

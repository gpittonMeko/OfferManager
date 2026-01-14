#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea utente admin nel database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Verifica se esiste già
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("✅ Utente admin già esistente")
    else:
        admin = User(
            username='admin',
            password=generate_password_hash('admin'),
            first_name='Admin',
            last_name='User',
            email='admin@meko.it',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Utente admin creato con successo!")
        print("   Username: admin")
        print("   Password: admin")





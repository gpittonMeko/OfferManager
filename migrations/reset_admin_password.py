#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resetta password admin"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.password = generate_password_hash('admin')
        db.session.commit()
        print("✅ Password admin resettata!")
        print("   Username: admin")
        print("   Password: admin")
    else:
        print("❌ Utente admin non trovato")





#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica credenziali nel database"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("SELECT id, username, email, role FROM users")).fetchall()
    print("Utenti nel database:")
    for r in result:
        print(f"ID: {r[0]}, Username: '{r[1]}', Email: {r[2]}, Role: {r[3]}")

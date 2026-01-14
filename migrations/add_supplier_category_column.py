#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna supplier_category alla tabella opportunities"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app
from sqlalchemy import text

with app.app_context():
    try:
        # SQLite non supporta ALTER TABLE ADD COLUMN IF NOT EXISTS
        # Prova ad aggiungere la colonna
        db.session.execute(text("ALTER TABLE opportunities ADD COLUMN supplier_category VARCHAR(50)"))
        db.session.commit()
        print("✅ Colonna supplier_category aggiunta")
    except Exception as e:
        db.session.rollback()
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  Colonna supplier_category già esistente")
        else:
            print(f"⚠️  Errore: {e}")
    
    # Aggiungi anche image_url ad accounts se non esiste
    try:
        db.session.execute(text("ALTER TABLE accounts ADD COLUMN image_url VARCHAR(500)"))
        db.session.commit()
        print("✅ Colonna image_url aggiunta ad accounts")
    except Exception as e:
        db.session.rollback()
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  Colonna image_url già esistente")
        else:
            print(f"⚠️  Errore: {e}")
    
    print("✅ Database aggiornato")


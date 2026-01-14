#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea tutte le tabelle nel database"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app

with app.app_context():
    try:
        print("📦 Creazione tabelle nel database...")
        db.create_all()
        print("✅ Tabelle create con successo!")
        
        # Verifica tabelle create
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Tabelle create: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

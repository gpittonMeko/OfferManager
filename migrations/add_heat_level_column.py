#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna heat_level alla tabella opportunities"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, Opportunity, app
import sqlite3

with app.app_context():
    try:
        # Prova prima con crm.db (database attivo)
        db_files = ['crm.db', 'mekocrm.db']
        db_file = None
        
        for dbf in db_files:
            if os.path.exists(dbf):
                conn_test = sqlite3.connect(dbf)
                cursor_test = conn_test.cursor()
                try:
                    cursor_test.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opportunities'")
                    if cursor_test.fetchone():
                        db_file = dbf
                        conn_test.close()
                        break
                except:
                    pass
                conn_test.close()
        
        if not db_file:
            print("❌ Nessun database con tabella opportunities trovato")
            print("✅ Creazione tabelle con SQLAlchemy...")
            db.create_all()
            db_file = 'mekocrm.db'
            if not os.path.exists(db_file):
                db_file = 'crm.db'
        
        print(f"📁 Database: {db_file}")
        
        # Aggiungi colonna heat_level se non esiste
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verifica se la colonna esiste già
        cursor.execute("PRAGMA table_info(opportunities)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'heat_level' not in columns:
            cursor.execute("ALTER TABLE opportunities ADD COLUMN heat_level VARCHAR(30) DEFAULT 'tiepida'")
            conn.commit()
            print("✅ Colonna heat_level aggiunta alla tabella opportunities")
        else:
            print("ℹ️ Colonna heat_level già esistente")
        
        # Aggiorna tutte le opportunità senza heat_level
        cursor.execute("UPDATE opportunities SET heat_level = 'tiepida' WHERE heat_level IS NULL")
        conn.commit()
        print(f"✅ Aggiornate {cursor.rowcount} opportunità con heat_level default")
        
        conn.close()
        print("✅ Migrazione completata!")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

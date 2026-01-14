#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna lost_reason alla tabella opportunities"""
import sys
import os
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db

def add_lost_reason_column():
    with app.app_context():
        print("=" * 80)
        print("AGGIUNTA COLONNA lost_reason")
        print("=" * 80)
        print()
        
        # Trova il database - prova diversi percorsi
        db_paths = [
            app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''),
            os.path.join('instance', 'mekocrm.db'),
            'mekocrm.db',
            os.path.join(os.path.dirname(__file__), 'instance', 'mekocrm.db'),
            os.path.join(os.path.dirname(__file__), 'mekocrm.db')
        ]
        
        db_path = None
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            print("❌ Database non trovato! Percorsi provati:")
            for path in db_paths:
                print(f"   - {path}")
            return
        
        print(f"📁 Database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Trova il nome corretto della tabella - prova diversi nomi
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelle trovate: {', '.join(all_tables)}")
        
        table_name = None
        for name in ['opportunities', 'opportunity']:
            if name in all_tables:
                table_name = name
                break
        
        if not table_name:
            print("❌ Tabella opportunities non trovata!")
            conn.close()
            return
        
        print(f"📋 Tabella trovata: {table_name}")
        
        # Verifica se la colonna esiste già
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colonne esistenti: {', '.join(columns)}")
        
        if 'lost_reason' not in columns:
            print("➕ Aggiunta colonna lost_reason...")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN lost_reason TEXT")
                conn.commit()
                print("✅ Colonna aggiunta!")
            except Exception as e:
                print(f"❌ Errore aggiungendo colonna: {e}")
        else:
            print("ℹ️ Colonna lost_reason già esistente")
        
        conn.close()
        print("\n✅ Completato!")

if __name__ == '__main__':
    try:
        add_lost_reason_column()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna heat_level alla tabella opportunities"""
import sys
import os
from pathlib import Path

# Aggiungi la root del progetto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from crm_app_completo import db, Opportunity, app
import sqlite3

with app.app_context():
    try:
        # Flask cerca il database in instance/ quando si usa sqlite:///mekocrm.db
        base_dir = Path(__file__).parent.parent
        instance_dir = base_dir / 'instance'
        db_file = instance_dir / 'mekocrm.db'
        
        # Se non esiste in instance/, prova nella root
        if not db_file.exists():
            db_file = base_dir / 'mekocrm.db'
        
        # Se ancora non esiste, prova crm.db
        if not db_file.exists():
            db_file = base_dir / 'crm.db'
        
        # Se non esiste, crea le tabelle
        if not db_file.exists():
            print("❌ Nessun database trovato")
            print("✅ Creazione tabelle con SQLAlchemy...")
            db.create_all()
            db_file = instance_dir / 'mekocrm.db'
            if not db_file.exists():
                db_file = base_dir / 'mekocrm.db'
        
        db_file = str(db_file)
        
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

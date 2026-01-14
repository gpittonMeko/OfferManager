#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggiunge colonne per configurazione PC locale alla tabella users
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
import sqlite3

def add_local_pc_columns():
    """Aggiunge colonne per configurazione PC locale"""
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri.replace('sqlite:///', '')
        
        # Flask cerca il database in instance/ quando si usa sqlite:///filename.db
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root del progetto
        if not os.path.isabs(db_path):
            # Prova prima in instance/ nella root del progetto
            instance_path = os.path.join(base_dir, 'instance', db_path)
            root_path = os.path.join(base_dir, db_path)
            if os.path.exists(instance_path):
                db_path = instance_path
            elif os.path.exists(root_path):
                db_path = root_path
            else:
                # Se non esiste, usa instance/ come default (comportamento Flask)
                db_path = instance_path
        
        print(f"Database path: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ Database non trovato: {db_path}")
            print("💡 Creando le tabelle...")
            db.create_all()
            # Dopo create_all, il database dovrebbe essere creato
            if not os.path.exists(db_path):
                print(f"❌ Impossibile creare il database: {db_path}")
                return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Verifica se le colonne esistono già
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'local_pc_ip' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN local_pc_ip VARCHAR(50)")
                print("✅ Aggiunta colonna local_pc_ip")
            else:
                print("⚠️  Colonna local_pc_ip già esistente")
            
            if 'local_pc_share' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN local_pc_share VARCHAR(100)")
                print("✅ Aggiunta colonna local_pc_share")
            else:
                print("⚠️  Colonna local_pc_share già esistente")
            
            if 'local_pc_base_path' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN local_pc_base_path VARCHAR(500)")
                print("✅ Aggiunta colonna local_pc_base_path")
            else:
                print("⚠️  Colonna local_pc_base_path già esistente")
            
            if 'local_pc_username' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN local_pc_username VARCHAR(100)")
                print("✅ Aggiunta colonna local_pc_username")
            else:
                print("⚠️  Colonna local_pc_username già esistente")
            
            if 'local_pc_password' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN local_pc_password VARCHAR(200)")
                print("✅ Aggiunta colonna local_pc_password")
            else:
                print("⚠️  Colonna local_pc_password già esistente")
            
            conn.commit()
            print("\n✅ Migrazione completata!")
            
        except Exception as e:
            print(f"❌ Errore: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    add_local_pc_columns()

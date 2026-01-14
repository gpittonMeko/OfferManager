#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna lost_reason alla tabella opportunities - versione server"""
import sys
import os
from pathlib import Path
import sqlite3

def add_lost_reason_column():
    print("=" * 80)
    print("AGGIUNTA COLONNA lost_reason")
    print("=" * 80)
    print()
    
    # Prova diversi percorsi database
    possible_paths = [
        'instance/mekocrm.db',
        'mekocrm.db',
        '/home/ubuntu/offermanager/instance/mekocrm.db',
        '/home/ubuntu/offermanager/mekocrm.db',
        os.path.join(os.path.dirname(__file__), 'instance', 'mekocrm.db'),
        os.path.join(os.path.dirname(__file__), 'mekocrm.db')
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Database trovato: {path}")
            break
    
    if not db_path:
        print("❌ Database non trovato! Percorsi provati:")
        for path in possible_paths:
            exists = os.path.exists(path)
            print(f"   {'✅' if exists else '❌'} {path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Trova tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelle trovate: {', '.join(all_tables)}")
        
        # Trova la tabella opportunities
        table_name = None
        for name in ['opportunities', 'opportunity']:
            if name in all_tables:
                table_name = name
                break
        
        if not table_name:
            print("❌ Tabella opportunities non trovata!")
            conn.close()
            return False
        
        print(f"📋 Tabella trovata: {table_name}")
        
        # Verifica colonne esistenti
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colonne esistenti: {', '.join(columns)}")
        
        if 'lost_reason' not in columns:
            print("➕ Aggiunta colonna lost_reason...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN lost_reason TEXT")
            conn.commit()
            print("✅ Colonna aggiunta!")
            
            # Verifica
            cursor.execute(f"PRAGMA table_info({table_name})")
            new_columns = [col[1] for col in cursor.fetchall()]
            if 'lost_reason' in new_columns:
                print("✅ Verifica: colonna lost_reason presente!")
            else:
                print("❌ Errore: colonna non aggiunta!")
                conn.close()
                return False
        else:
            print("ℹ️ Colonna lost_reason già esistente")
        
        conn.close()
        print("\n✅ Completato!")
        return True
        
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_lost_reason_column()
    sys.exit(0 if success else 1)

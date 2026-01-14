#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix database - aggiunge colonne mancanti
"""
import sqlite3
import os
from pathlib import Path

def fix_database():
    """Aggiunge colonne mancanti al database"""
    db_path = Path(__file__).parent / 'instance' / 'mekocrm.db'
    if not db_path.exists():
        db_path = Path(__file__).parent / 'mekocrm.db'
    
    if not db_path.exists():
        print(f"❌ Database non trovato: {db_path}")
        return False
    
    print(f"📦 Database trovato: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Verifica colonne esistenti in opportunities
        cursor.execute("PRAGMA table_info(opportunities)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonne esistenti: {columns}")
        
        # Aggiungi folder_path se manca
        if 'folder_path' not in columns:
            print("➕ Aggiungo colonna folder_path...")
            cursor.execute("ALTER TABLE opportunities ADD COLUMN folder_path VARCHAR(400)")
            print("   ✅ Colonna folder_path aggiunta")
        
        # Verifica colonne in altre tabelle se necessario
        # (Aggiungi qui altre colonne mancanti se ce ne sono)
        
        conn.commit()
        print("✅ Database aggiornato con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()








#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FORZA aggiornamento di TUTTE le opportunità a 'da_categorizzare' su AWS
"""
import sqlite3
from pathlib import Path

def fix_heat_level():
    print("=" * 80)
    print("FORZA AGGIORNAMENTO OPPORTUNITÀ A 'DA CATEGORIZZARE' - AWS")
    print("=" * 80)
    print()
    
    # Trova il database
    base_dir = Path('/home/ubuntu/offermanager')
    instance_dir = base_dir / 'instance'
    db_file = instance_dir / 'mekocrm.db'
    
    if not db_file.exists():
        db_file = base_dir / 'mekocrm.db'
    
    if not db_file.exists():
        print("❌ Database non trovato!")
        return
    
    print(f"📁 Database: {db_file}")
    print()
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # Verifica colonna
        cursor.execute("PRAGMA table_info(opportunities)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'heat_level' not in columns:
            print("📝 Aggiungo colonna heat_level...")
            cursor.execute("ALTER TABLE opportunities ADD COLUMN heat_level VARCHAR(30)")
            conn.commit()
            print("✅ Colonna aggiunta!")
        
        # Conta prima
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        total = cursor.fetchone()[0]
        print(f"📊 Totale opportunità: {total}")
        
        # Conta per heat_level
        cursor.execute("SELECT heat_level, COUNT(*) FROM opportunities GROUP BY heat_level")
        before = dict(cursor.fetchall())
        print(f"📊 Prima: {before}")
        
        # FORZA aggiornamento di TUTTE le opportunità
        cursor.execute("UPDATE opportunities SET heat_level = 'da_categorizzare'")
        conn.commit()
        
        updated = cursor.rowcount
        print(f"✅ Aggiornate {updated} opportunità!")
        
        # Verifica dopo
        cursor.execute("SELECT heat_level, COUNT(*) FROM opportunities GROUP BY heat_level")
        after = dict(cursor.fetchall())
        print(f"📊 Dopo: {after}")
        
    finally:
        conn.close()
    
    print("\n✅ OPERAZIONE COMPLETATA!")

if __name__ == '__main__':
    try:
        fix_heat_level()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

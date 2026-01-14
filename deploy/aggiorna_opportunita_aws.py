#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggiorna tutte le opportunità a 'da_categorizzare' sul server AWS
Usa solo SQLite, non richiede Flask
"""
import os
import sqlite3
from pathlib import Path

def aggiorna_opportunita_aws():
    print("=" * 80)
    print("AGGIORNAMENTO OPPORTUNITÀ A 'DA CATEGORIZZARE' - SERVER AWS")
    print("=" * 80)
    print()
    
    # Trova il database (Flask cerca in instance/)
    base_dir = Path(__file__).parent
    instance_dir = base_dir / 'instance'
    db_file = instance_dir / 'mekocrm.db'
    
    if not db_file.exists():
        db_file = base_dir / 'mekocrm.db'
    
    if not db_file.exists():
        print("❌ Database non trovato!")
        print(f"   Cercato in: {instance_dir / 'mekocrm.db'}")
        print(f"   Cercato in: {base_dir / 'mekocrm.db'}")
        return
    
    print(f"📁 Database: {db_file}")
    print()
    
    # Connetti direttamente al database SQLite
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # Verifica se la colonna heat_level esiste
        cursor.execute("PRAGMA table_info(opportunities)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'heat_level' not in columns:
            print("📝 Aggiungo colonna heat_level...")
            cursor.execute("ALTER TABLE opportunities ADD COLUMN heat_level VARCHAR(30)")
            conn.commit()
            print("✅ Colonna aggiunta!")
        else:
            print("ℹ️ Colonna heat_level già esistente")
        
        # Conta le opportunità
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        total = cursor.fetchone()[0]
        print(f"📊 Totale opportunità: {total}")
        
        if total == 0:
            print("✅ Nessuna opportunità da aggiornare!")
            return
        
        # Aggiorna TUTTE le opportunità a 'da_categorizzare'
        cursor.execute("UPDATE opportunities SET heat_level = 'da_categorizzare'")
        conn.commit()
        
        updated = cursor.rowcount
        print(f"✅ Aggiornate {updated} opportunità a 'da_categorizzare'!")
        
        # Verifica
        cursor.execute("SELECT COUNT(*) FROM opportunities WHERE heat_level = 'da_categorizzare'")
        verified = cursor.fetchone()[0]
        print(f"📊 Verifica: {verified} opportunità con heat_level = 'da_categorizzare'")
        
    finally:
        conn.close()
    
    print("\n✅ Operazione completata con successo!")

if __name__ == '__main__':
    try:
        aggiorna_opportunita_aws()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

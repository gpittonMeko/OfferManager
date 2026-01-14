#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggiunge colonne closed_amount e margin alla tabella offers
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

def add_closed_amount_margin_columns():
    """Aggiunge colonne closed_amount e margin alla tabella offers"""
    with app.app_context():
        try:
            # Verifica se le colonne esistono già
            result = db.session.execute(text("PRAGMA table_info(offers)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'closed_amount' not in columns:
                print("Aggiungo colonna closed_amount...")
                db.session.execute(text("ALTER TABLE offers ADD COLUMN closed_amount REAL DEFAULT 0.0"))
                print("✅ Colonna closed_amount aggiunta")
            else:
                print("⚠️  Colonna closed_amount già esistente")
            
            if 'margin' not in columns:
                print("Aggiungo colonna margin...")
                db.session.execute(text("ALTER TABLE offers ADD COLUMN margin REAL DEFAULT 0.0"))
                print("✅ Colonna margin aggiunta")
            else:
                print("⚠️  Colonna margin già esistente")
            
            db.session.commit()
            print("\n✅ Migrazione completata!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore durante la migrazione: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    print("="*80)
    print("MIGRAZIONE: Aggiunta colonne closed_amount e margin a offers")
    print("="*80)
    print()
    
    if add_closed_amount_margin_columns():
        print("\n✅ Migrazione completata con successo!")
    else:
        print("\n❌ Migrazione fallita!")
        sys.exit(1)

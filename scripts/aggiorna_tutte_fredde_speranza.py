#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna tutte le opportunità a fredda_speranza"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Verifica se la colonna heat_level esiste
    try:
        # Prova a fare una query che include heat_level
        test_result = db.session.execute(text("SELECT heat_level FROM opportunities LIMIT 1")).fetchone()
        has_heat_level = True
    except Exception:
        # Se la colonna non esiste, la creiamo
        try:
            db.session.execute(text("ALTER TABLE opportunities ADD COLUMN heat_level VARCHAR(30)"))
            db.session.commit()
            has_heat_level = True
            print("✅ Colonna heat_level creata")
        except Exception as e:
            print(f"⚠️ Impossibile creare colonna heat_level: {e}")
            has_heat_level = False
    
    if has_heat_level:
        # Aggiorna tutte le opportunità a fredda_speranza
        result = db.session.execute(text("""
            UPDATE opportunities 
            SET heat_level = 'fredda_speranza'
            WHERE heat_level IS NULL OR heat_level != 'fredda_speranza'
        """))
        db.session.commit()
        
        print(f"✅ Aggiornate {result.rowcount} opportunità a stato 'fredda_speranza'")
        
        # Verifica il risultato
        counts = db.session.execute(text("""
            SELECT heat_level, COUNT(*) 
            FROM opportunities 
            GROUP BY heat_level
        """)).fetchall()
        
        print("\n📊 Distribuzione stati:")
        for row in counts:
            print(f"   {row[0] or 'NULL'}: {row[1]}")
    else:
        print("❌ Impossibile aggiornare: colonna heat_level non disponibile")

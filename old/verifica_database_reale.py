#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica quale database contiene i dati reali"""
import sqlite3
import os

databases = [
    ('crm.db', 'Database principale'),
    ('instance/mekocrm.db', 'Database instance mekocrm'),
    ('instance/offer_manager_crm.db', 'Database instance offer_manager'),
]

for db_path, desc in databases:
    if os.path.exists(db_path):
        print(f"\n{'='*60}")
        print(f"📁 {desc}: {db_path}")
        print(f"{'='*60}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica tabelle
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"Tabelle: {len(tables)}")
            
            # Conta record importanti
            counts = {}
            for table in ['users', 'opportunities', 'offers', 'products', 'accounts', 'leads']:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                    print(f"  ✅ {table}: {counts[table]} record")
            
            # Mostra alcune opportunità se esistono
            if 'opportunities' in tables and counts.get('opportunities', 0) > 0:
                cursor.execute("SELECT id, name, stage, amount FROM opportunities LIMIT 5")
                opps = cursor.fetchall()
                print(f"\n  📊 Prime 5 opportunità:")
                for opp in opps:
                    print(f"     - {opp[1]} ({opp[2]}) - €{opp[3]}")
            
            # Mostra alcune offerte se esistono
            if 'offers' in tables and counts.get('offers', 0) > 0:
                cursor.execute("SELECT id, number, amount FROM offers LIMIT 5")
                offers = cursor.fetchall()
                print(f"\n  📄 Prime 5 offerte:")
                for off in offers:
                    print(f"     - {off[1]} - €{off[2]}")
            
            conn.close()
            
            # Calcola totale record
            total = sum(counts.values())
            if total > 100:
                print(f"\n  ⭐ QUESTO DATABASE CONTIENE DATI REALI! ({total} record totali)")
        except Exception as e:
            print(f"  ❌ Errore: {e}")

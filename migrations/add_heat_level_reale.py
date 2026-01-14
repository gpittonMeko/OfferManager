#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge colonna heat_level al database REALE instance/mekocrm.db"""
import sqlite3

db_file = 'instance/mekocrm.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"📁 Aggiunta colonna heat_level a {db_file}...")

# Verifica colonne esistenti
cursor.execute("PRAGMA table_info(opportunities)")
columns = [col[1] for col in cursor.fetchall()]

if 'heat_level' not in columns:
    print("➕ Aggiunta colonna heat_level...")
    cursor.execute("ALTER TABLE opportunities ADD COLUMN heat_level VARCHAR(30) DEFAULT 'tiepida'")
    conn.commit()
    print("✅ Colonna aggiunta!")
    
    # Aggiorna record esistenti
    cursor.execute("UPDATE opportunities SET heat_level = 'tiepida' WHERE heat_level IS NULL")
    conn.commit()
    print(f"✅ Aggiornati {cursor.rowcount} record")
else:
    print("ℹ️ Colonna heat_level già esistente")

conn.close()
print("✅ Completato!")

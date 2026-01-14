#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra struttura tabella opportunities"""
import sqlite3

db_file = 'crm.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"📁 Migrazione struttura tabella opportunities in {db_file}...")

# Verifica colonne esistenti
cursor.execute("PRAGMA table_info(opportunities)")
columns = [col[1] for col in cursor.fetchall()]

# Colonne da aggiungere
columns_to_add = {
    'close_date': 'DATE',
    'opportunity_type': 'VARCHAR(50)',
    'description': 'TEXT',
    'supplier_category': 'VARCHAR(50)',
    'folder_path': 'VARCHAR(400)',
    'heat_level': 'VARCHAR(30) DEFAULT "tiepida"',
    'contact_id': 'INTEGER',
    'lead_id': 'INTEGER',
    'updated_at': 'TIMESTAMP'
}

for col_name, col_type in columns_to_add.items():
    if col_name not in columns:
        print(f"➕ Aggiunta colonna {col_name}...")
        try:
            cursor.execute(f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}")
        except Exception as e:
            print(f"   ⚠️ Errore aggiunta {col_name}: {e}")

# Aggiorna heat_level default per record esistenti
if 'heat_level' in columns_to_add:
    cursor.execute("UPDATE opportunities SET heat_level = 'tiepida' WHERE heat_level IS NULL")

conn.commit()
print("✅ Migrazione completata!")

# Verifica struttura finale
cursor.execute("PRAGMA table_info(opportunities)")
columns = cursor.fetchall()
print("\n📋 Struttura finale tabella opportunities:")
for col in columns:
    print(f"   {col[1]} ({col[2]})")

conn.close()

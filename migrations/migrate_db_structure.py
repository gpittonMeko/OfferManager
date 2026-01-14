#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra struttura database crm.db al nuovo formato"""
import sqlite3
import os

db_file = 'crm.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"📁 Migrazione struttura database {db_file}...")

# Verifica colonne esistenti
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

# Aggiungi first_name e last_name se non esistono
if 'first_name' not in columns:
    print("➕ Aggiunta colonna first_name...")
    cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
    
if 'last_name' not in columns:
    print("➕ Aggiunta colonna last_name...")
    cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT")

# Migra dati da full_name a first_name/last_name
if 'full_name' in columns and 'first_name' in columns:
    print("📝 Migrazione dati da full_name a first_name/last_name...")
    cursor.execute("SELECT id, full_name FROM users WHERE full_name IS NOT NULL AND (first_name IS NULL OR first_name = '')")
    users = cursor.fetchall()
    for user_id, full_name in users:
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = parts[1] if len(parts) > 1 else ''
            cursor.execute("UPDATE users SET first_name = ?, last_name = ? WHERE id = ?", 
                         (first_name, last_name, user_id))

# Aggiungi updated_at se non esiste
if 'updated_at' not in columns:
    print("➕ Aggiunta colonna updated_at...")
    cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP")
    # Copia created_at in updated_at per i record esistenti
    cursor.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")

conn.commit()
print("✅ Migrazione completata!")

# Verifica struttura finale
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("\n📋 Struttura finale tabella users:")
for col in columns:
    print(f"   {col[1]} ({col[2]})")

conn.close()

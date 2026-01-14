#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conta le offerte associate"""
import sqlite3
import os

db_path = os.path.join('instance', 'mekocrm.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM offers')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM offers WHERE folder_path IS NOT NULL AND folder_path != ""')
con_cartella = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM offers WHERE opportunity_id IS NOT NULL')
con_opportunita = cursor.fetchone()[0]

print("="*60)
print("RIEPILOGO OFFERTE ASSOCIATE")
print("="*60)
print(f"\nOfferte totali nel database: {total}")
print(f"Offerte con cartella associata: {con_cartella}")
print(f"Offerte associate ad opportunita: {con_opportunita}")
print(f"\nPercentuale con cartella: {(con_cartella/total*100) if total > 0 else 0:.1f}%")
print(f"Percentuale con opportunita: {(con_opportunita/total*100) if total > 0 else 0:.1f}%")

conn.close()

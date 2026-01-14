#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità con cartella principale"""
import sqlite3
import os

db_path = os.path.join('instance', 'mekocrm.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Trova opportunità con cartella principale
cursor.execute("""
    SELECT id, name, folder_path 
    FROM opportunities 
    WHERE folder_path LIKE '%OFFERTE 2025 - K' 
       OR folder_path LIKE '%OFFERTE 2026 - K'
""")

opps = cursor.fetchall()

print("="*80)
print("OPPORTUNITA CON CARTELLA PRINCIPALE")
print("="*80)

for opp in opps:
    folder_basename = os.path.basename(opp[2]) if opp[2] else None
    if folder_basename in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']:
        print(f"\nID: {opp[0]}")
        print(f"Nome: {opp[1]}")
        print(f"Cartella: {opp[2]}")
        print(f"PROBLEMA: Cartella principale!")
        
        # Conta offerte associate
        cursor.execute("SELECT COUNT(*) FROM offers WHERE opportunity_id = ?", (opp[0],))
        offers_count = cursor.fetchone()[0]
        print(f"Offerte associate: {offers_count}")

print(f"\n\nTotale opportunità con cartella principale: {len([o for o in opps if os.path.basename(o[2] if o[2] else '') in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']])}")

conn.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica offerta K1651-25"""
import sqlite3
import os

db_path = os.path.join('instance', 'mekocrm.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Trova offerta K1651
cursor.execute("SELECT id, number, folder_path, opportunity_id FROM offers WHERE number LIKE '%1651%'")
offers = cursor.fetchall()

print("="*80)
print("VERIFICA OFFERTA K1651-25")
print("="*80)

for offer in offers:
    print(f"\nID: {offer[0]}")
    print(f"Numero: {offer[1]}")
    print(f"Cartella: {offer[2]}")
    print(f"Opportunita ID: {offer[3]}")
    
    if offer[2]:
        folder_basename = os.path.basename(offer[2])
        print(f"Cartella base: {folder_basename}")
        
        if folder_basename in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']:
            print("PROBLEMA: Cartella principale!")
        else:
            print("OK: Cartella specifica")
            
            # Verifica file nella cartella
            if os.path.exists(offer[2]):
                files = [f for f in os.listdir(offer[2]) 
                        if os.path.isfile(os.path.join(offer[2], f)) 
                        and f.lower().endswith(('.pdf', '.docx', '.doc'))]
                print(f"File nella cartella: {len(files)}")
                if len(files) > 0:
                    print(f"Esempi: {', '.join(files[:5])}")
            else:
                print("Cartella non trovata sul filesystem")

conn.close()

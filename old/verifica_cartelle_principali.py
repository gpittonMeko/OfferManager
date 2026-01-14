#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica offerte con cartella principale invece di cartella specifica"""
import sqlite3
import os

db_path = os.path.join('instance', 'mekocrm.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Trova offerte con cartella principale
cursor.execute("""
    SELECT id, number, folder_path 
    FROM offers 
    WHERE folder_path LIKE '%OFFERTE 2025 - K' 
       OR folder_path LIKE '%OFFERTE 2026 - K'
    ORDER BY id
""")

offers = cursor.fetchall()

print("="*80)
print("OFFERTE CON CARTELLA PRINCIPALE (DA CORREGGERE)")
print("="*80)

offers_with_main_folder = []
for offer in offers:
    folder = offer[2]
    folder_basename = os.path.basename(folder)
    
    # Verifica se è la cartella principale (non contiene K####)
    if folder_basename in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']:
        offers_with_main_folder.append(offer)
        print(f"\nID: {offer[0]}, Numero: {offer[1]}")
        print(f"  Cartella: {folder}")
        print(f"  PROBLEMA: Cartella principale invece di cartella specifica!")

print(f"\n\nTotale offerte con cartella principale: {len(offers_with_main_folder)}")
print(f"Totale offerte verificate: {len(offers)}")

conn.close()

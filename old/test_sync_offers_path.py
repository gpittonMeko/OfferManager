#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test percorso sync offerte"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_offers_from_folder import OFFERS_FOLDER

print("="*60)
print("TEST PERCORSO SYNC OFFERTE")
print("="*60)
print(f"\nOFFERS_FOLDER: {OFFERS_FOLDER}")
print(f"Esiste: {os.path.exists(OFFERS_FOLDER)}")

if os.path.exists(OFFERS_FOLDER):
    # Conta file
    file_count = 0
    for root, dirs, files in os.walk(OFFERS_FOLDER):
        file_count += len([f for f in files if f.endswith(('.docx', '.pdf', '.doc'))])
    print(f"File offerte trovati: {file_count}")
    
    # Mostra primi 5 file
    print("\nPrimi 5 file:")
    count = 0
    for root, dirs, files in os.walk(OFFERS_FOLDER):
        for f in files:
            if f.endswith(('.docx', '.pdf', '.doc')):
                print(f"  - {os.path.join(root, f)}")
                count += 1
                if count >= 5:
                    break
        if count >= 5:
            break
else:
    print("\nERRORE: Cartella non trovata!")





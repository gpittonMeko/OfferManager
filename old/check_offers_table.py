#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica la tabella offers nel database"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, OfferDocument

db_path = os.path.join('instance', 'mekocrm.db')

print(f"Database: {db_path}")
print(f"Esiste: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica se la tabella esiste
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='offers'")
    table_exists = cursor.fetchone() is not None
    print(f"\nTabella 'offers' esiste: {table_exists}")
    
    if table_exists:
        # Conta le offerte
        cursor.execute("SELECT COUNT(*) FROM offers")
        count = cursor.fetchone()[0]
        print(f"Numero offerte: {count}")
        
        # Mostra schema
        cursor.execute("PRAGMA table_info(offers)")
        columns = cursor.fetchall()
        print("\nSchema tabella 'offers':")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Mostra alcune offerte di esempio
        if count > 0:
            cursor.execute("SELECT id, number, folder_path, opportunity_id FROM offers LIMIT 5")
            offers = cursor.fetchall()
            print("\nPrime 5 offerte:")
            for offer in offers:
                print(f"  ID: {offer[0]}, Numero: {offer[1]}, Cartella: {offer[2]}, Opportunità: {offer[3]}")
    
    # Verifica anche con SQLAlchemy
    print("\n" + "="*60)
    print("Verifica con SQLAlchemy:")
    print("="*60)
    with app.app_context():
        offers = OfferDocument.query.all()
        print(f"Offerte trovate: {len(offers)}")
        
        if len(offers) > 0:
            print("\nPrime 5 offerte:")
            for offer in offers[:5]:
                print(f"  ID: {offer.id}, Numero: {offer.number}, Cartella: {offer.folder_path}, Opportunità: {offer.opportunity_id}")
    
    conn.close()

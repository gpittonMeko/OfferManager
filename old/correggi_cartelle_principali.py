#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corregge le offerte che hanno la cartella principale invece di cartella specifica"""
import sys
import os
import sqlite3
import re

sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, OfferDocument
from sqlalchemy import text

db_path = os.path.join('instance', 'mekocrm.db')

with app.app_context():
    # Trova offerte con cartella principale
    offers_to_fix = db.session.execute(text("""
        SELECT id, number, folder_path, pdf_path, docx_path
        FROM offers 
        WHERE folder_path LIKE '%OFFERTE 2025 - K' 
           OR folder_path LIKE '%OFFERTE 2026 - K'
    """)).fetchall()
    
    print("="*80)
    print("CORREZIONE CARTELLE PRINCIPALI")
    print("="*80)
    
    fixed = 0
    for offer_row in offers_to_fix:
        offer_id, number, folder_path, pdf_path, docx_path = offer_row
        folder_basename = os.path.basename(folder_path)
        
        if folder_basename in ['OFFERTE 2025 - K', 'OFFERTE 2026 - K']:
            print(f"\nOfferta ID {offer_id}, Numero: {number}")
            print(f"  Cartella attuale: {folder_path}")
            
            # Prova a trovare la cartella specifica guardando i file PDF/DOCX
            new_folder_path = None
            
            if pdf_path:
                # Il PDF dovrebbe essere in una cartella specifica
                pdf_dir = os.path.dirname(pdf_path)
                if os.path.exists(pdf_dir) and os.path.basename(pdf_dir) != folder_basename:
                    new_folder_path = pdf_dir
                    print(f"  Trovata cartella da PDF: {os.path.basename(new_folder_path)}")
            
            if not new_folder_path and docx_path:
                docx_dir = os.path.dirname(docx_path)
                if os.path.exists(docx_dir) and os.path.basename(docx_dir) != folder_basename:
                    new_folder_path = docx_dir
                    print(f"  Trovata cartella da DOCX: {os.path.basename(new_folder_path)}")
            
            # Se non trovata, cerca nella cartella principale usando il numero offerta
            if not new_folder_path:
                base_folder = folder_path
                # Cerca cartelle che contengono il numero offerta
                if os.path.exists(base_folder):
                    try:
                        for item in os.listdir(base_folder):
                            item_path = os.path.join(base_folder, item)
                            if os.path.isdir(item_path):
                                # Verifica se il numero offerta è nel nome della cartella
                                if number and number in item:
                                    new_folder_path = item_path
                                    print(f"  Trovata cartella per numero: {os.path.basename(new_folder_path)}")
                                    break
                    except Exception as e:
                        print(f"  Errore cercando cartelle: {e}")
            
            if new_folder_path and os.path.exists(new_folder_path):
                # Aggiorna la cartella nel database
                db.session.execute(text("""
                    UPDATE offers 
                    SET folder_path = :new_path 
                    WHERE id = :offer_id
                """), {"new_path": new_folder_path, "offer_id": offer_id})
                fixed += 1
                print(f"  ✅ Aggiornata a: {os.path.basename(new_folder_path)}")
            else:
                print(f"  ⚠️  Impossibile trovare cartella specifica - offerta da risincronizzare")
    
    db.session.commit()
    print(f"\n\n✅ Corrette {fixed} offerte")
    print("="*80)

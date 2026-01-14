#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica e sincronizza offerte dalle cartelle al database
SENZA modificare i file sul server
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, OfferDocument

# Verifica database
db_path = os.path.join('instance', 'mekocrm.db')
print(f"Database: {db_path}")
print(f"Esiste: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Conta offerte
    cursor.execute("SELECT COUNT(*) FROM offers")
    count_before = cursor.fetchone()[0]
    print(f"\nOfferte nel database PRIMA della sincronizzazione: {count_before}")
    
    conn.close()

# Ora esegui la sincronizzazione
print("\n" + "="*80)
print("ESECUZIONE SINCRONIZZAZIONE OFFERTE")
print("="*80)
print("\n⚠️  IMPORTANTE: La sincronizzazione NON modificherà i file sul server")
print("   Verranno solo creati record nel database per associare le cartelle\n")

from sync_offers_from_folder import sync_offers

try:
    sync_offers()
    
    # Verifica dopo
    print("\n" + "="*80)
    print("VERIFICA DOPO SINCRONIZZAZIONE")
    print("="*80)
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM offers")
        count_after = cursor.fetchone()[0]
        print(f"\nOfferte nel database DOPO la sincronizzazione: {count_after}")
        print(f"Offerte aggiunte: {count_after - count_before}")
        
        # Conta offerte con cartella associata
        cursor.execute("SELECT COUNT(*) FROM offers WHERE folder_path IS NOT NULL AND folder_path != ''")
        count_with_folder = cursor.fetchone()[0]
        print(f"Offerte con cartella associata: {count_with_folder}")
        
        # Conta offerte associate ad opportunità
        cursor.execute("SELECT COUNT(*) FROM offers WHERE opportunity_id IS NOT NULL")
        count_with_opp = cursor.fetchone()[0]
        print(f"Offerte associate ad opportunità: {count_with_opp}")
        
        # Mostra alcune offerte di esempio
        if count_after > 0:
            cursor.execute("SELECT id, number, folder_path, opportunity_id FROM offers LIMIT 10")
            offers = cursor.fetchall()
            print("\nPrime 10 offerte sincronizzate:")
            for offer in offers:
                folder = offer[2] if offer[2] else "Nessuna"
                opp = offer[3] if offer[3] else "Nessuna"
                print(f"  • ID: {offer[0]}, Numero: {offer[1]}, Cartella: {os.path.basename(folder) if folder != 'Nessuna' else 'Nessuna'}, Opportunità: {opp}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✅ SINCRONIZZAZIONE COMPLETATA")
        print("="*80)
        print(f"\n📊 RIEPILOGO:")
        print(f"   • Offerte totali nel database: {count_after}")
        print(f"   • Offerte con cartella associata: {count_with_folder}")
        print(f"   • Offerte associate ad opportunità: {count_with_opp}")
        
except Exception as e:
    print(f"\n❌ Errore durante la sincronizzazione: {e}")
    import traceback
    traceback.print_exc()

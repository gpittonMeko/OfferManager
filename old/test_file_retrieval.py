#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test per verificare che ogni offerta mostri solo i file della sua cartella
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Opportunity, OfferDocument

# Trova un'opportunità con offerte
with app.app_context():
    from sqlalchemy import text
    
    # Cerca opportunità con offerte
    opps_with_offers = db.session.execute(text("""
        SELECT DISTINCT o.id, o.name, COUNT(off.id) as offers_count
        FROM opportunities o
        JOIN offers off ON off.opportunity_id = o.id
        GROUP BY o.id, o.name
        HAVING COUNT(off.id) > 0
        LIMIT 5
    """)).fetchall()
    
    print("="*80)
    print("TEST VERIFICA FILE OFFERTE")
    print("="*80)
    
    for opp_row in opps_with_offers:
        opp_id = opp_row[0]
        opp_name = opp_row[1]
        offers_count = opp_row[2]
        
        print(f"\n📋 Opportunità: {opp_name} (ID: {opp_id})")
        print(f"   Offerte associate: {offers_count}")
        
        # Recupera le offerte
        offers = db.session.execute(text("""
            SELECT id, number, folder_path 
            FROM offers 
            WHERE opportunity_id = :opp_id
        """), {"opp_id": opp_id}).fetchall()
        
        print(f"\n   Cartelle delle offerte:")
        for offer in offers:
            folder = offer[2] if offer[2] else "Nessuna cartella"
            folder_name = os.path.basename(folder) if folder != "Nessuna cartella" else "Nessuna"
            print(f"     • Offerta {offer[1]}: {folder_name}")
            
            # Verifica se la cartella esiste
            if folder and folder != "Nessuna cartella":
                if os.path.exists(folder):
                    try:
                        files = [f for f in os.listdir(folder) 
                                if os.path.isfile(os.path.join(folder, f)) 
                                and f.lower().endswith(('.pdf', '.docx', '.doc'))]
                        print(f"       File trovati: {len(files)}")
                        if len(files) > 0:
                            print(f"       Esempi: {', '.join(files[:3])}")
                    except Exception as e:
                        print(f"       Errore: {e}")
                else:
                    print(f"       ⚠️  Cartella non trovata sul filesystem")
        
        print()

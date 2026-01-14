#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità K1550-25"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Trova opportunità K1550-25
    opp = db.session.execute(text("""
        SELECT id, name FROM opportunities 
        WHERE name LIKE '%K1550%'
    """)).fetchall()
    
    print("Opportunità trovate:")
    for o in opp:
        print(f"  ID: {o[0]}, Nome: {o[1]}")
        
        # Trova offerte associate
        offers = db.session.execute(text("""
            SELECT id, number, folder_path, opportunity_id 
            FROM offers 
            WHERE opportunity_id = :opp_id
        """), {"opp_id": o[0]}).fetchall()
        
        print(f"  Offerte associate: {len(offers)}")
        for off in offers:
            print(f"    - ID: {off[0]}, Numero: {off[1]}, Folder: {off[2]}")
        
        # Cerca offerta K1550-25
        offer_k1550 = db.session.execute(text("""
            SELECT id, number, folder_path, opportunity_id 
            FROM offers 
            WHERE number = 'K1550-25'
        """)).fetchone()
        
        if offer_k1550:
            print(f"\n  Offerta K1550-25 trovata:")
            print(f"    ID: {offer_k1550[0]}")
            print(f"    Folder: {offer_k1550[2]}")
            print(f"    Associata a opportunity_id: {offer_k1550[3]}")
            
            if offer_k1550[3] != o[0]:
                print(f"    ⚠️  ASSOCIATA ALL'OPPORTUNITÀ SBAGLIATA!")
                print(f"    🔄 Correzione...")
                db.session.execute(text("""
                    UPDATE offers SET opportunity_id = :opp_id WHERE id = :offer_id
                """), {"opp_id": o[0], "offer_id": offer_k1550[0]})
                db.session.commit()
                print(f"    ✅ Corretto!")
            else:
                print(f"    ✅ Già associata correttamente")

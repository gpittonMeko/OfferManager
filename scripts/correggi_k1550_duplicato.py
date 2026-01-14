#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correggi opportunità K1550-25 duplicata"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Trova tutte le opportunità K1550-25
    opps = db.session.execute(text("""
        SELECT id, name FROM opportunities 
        WHERE name LIKE '%K1550%'
    """)).fetchall()
    
    print("Opportunità trovate:")
    for o in opps:
        print(f"  ID: {o[0]}, Nome: {o[1]}")
        
        # Trova offerte associate
        offers = db.session.execute(text("""
            SELECT id, number, folder_path, opportunity_id 
            FROM offers 
            WHERE opportunity_id = :opp_id
        """), {"opp_id": o[0]}).fetchall()
        
        print(f"    Offerte associate: {len(offers)}")
        for off in offers:
            print(f"      - {off[1]}")
    
    # Trova offerta K1550-25
    offer_k1550 = db.session.execute(text("""
        SELECT id, number, folder_path, opportunity_id 
        FROM offers 
        WHERE number = 'K1550-25'
    """)).fetchone()
    
    if offer_k1550:
        print(f"\nOfferta K1550-25 trovata:")
        print(f"  ID: {offer_k1550[0]}")
        print(f"  Folder: {offer_k1550[2]}")
        print(f"  Associata a opportunity_id: {offer_k1550[3]}")
        
        # Trova quale opportunità dovrebbe avere questa offerta
        # (quella che ha il nome più completo)
        opp_corretta = None
        for o in opps:
            if 'MC ENGINEERING' in o[1]:
                opp_corretta = o[0]
                break
        
        if opp_corretta and offer_k1550[3] != opp_corretta:
            print(f"\nCORREZIONE: Offerta associata a {offer_k1550[3]}, dovrebbe essere {opp_corretta}")
            print(f"Associazione offerta {offer_k1550[0]} all'opportunità {opp_corretta}...")
            db.session.execute(text("""
                UPDATE offers SET opportunity_id = :opp_id WHERE id = :offer_id
            """), {"opp_id": opp_corretta, "offer_id": offer_k1550[0]})
            db.session.commit()
            print(f"OK Corretto!")
        elif not opp_corretta:
            # Se non troviamo quella corretta, associamo alla prima che ha offerte associate
            opp_con_offerte = None
            for o in opps:
                offers_count = db.session.execute(text("""
                    SELECT COUNT(*) FROM offers WHERE opportunity_id = :opp_id
                """), {"opp_id": o[0]}).fetchone()[0]
                if offers_count > 0:
                    opp_con_offerte = o[0]
                    break
            
            if opp_con_offerte and offer_k1550[3] != opp_con_offerte:
                print(f"\nCORREZIONE: Offerta associata a {offer_k1550[3]}, spostiamo a {opp_con_offerte}")
                db.session.execute(text("""
                    UPDATE offers SET opportunity_id = :opp_id WHERE id = :offer_id
                """), {"opp_id": opp_con_offerte, "offer_id": offer_k1550[0]})
                db.session.commit()
                print(f"OK Corretto!")
        else:
            print(f"OK Già associata correttamente")

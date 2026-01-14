#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test associazione automatica offerte"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import re

with app.app_context():
    # Trova opportunità 190 (quella che viene trovata dall'API)
    opp = db.session.execute(text("""
        SELECT id, name FROM opportunities WHERE id = 190
    """)).fetchone()
    
    if opp:
        print(f"Opportunità 190: {opp[1]}")
        
        # Verifica se ha offerte associate
        offers = db.session.execute(text("""
            SELECT id, number FROM offers WHERE opportunity_id = 190
        """)).fetchall()
        
        print(f"Offerte associate: {len(offers)}")
        
        # Testa la logica di associazione automatica
        opp_name = opp[1]
        match = re.search(r'K(\d{4})-(\d{2})', opp_name)
        if match:
            offer_number = match.group(0)
            print(f"Numero offerta estratto: {offer_number}")
            
            # Cerca offerta con questo numero
            matching_offer = db.session.execute(text("""
                SELECT id, number, folder_path, opportunity_id
                FROM offers 
                WHERE number = :offer_number
                LIMIT 1
            """), {"offer_number": offer_number}).fetchone()
            
            if matching_offer:
                print(f"Offerta trovata: ID={matching_offer[0]}, associata a opportunity_id={matching_offer[3]}")
                
                if matching_offer[3] != 190:
                    print(f"ASSOCIAZIONE: Offerta {matching_offer[0]} all'opportunità 190...")
                    db.session.execute(text("""
                        UPDATE offers 
                        SET opportunity_id = :opp_id
                        WHERE id = :offer_id
                    """), {
                        "opp_id": 190,
                        "offer_id": matching_offer[0]
                    })
                    db.session.commit()
                    print(f"OK Corretto!")
                else:
                    print(f"OK Già associata correttamente")
            else:
                print(f"ERRORE Offerta {offer_number} non trovata")
        else:
            print(f"ERRORE Nessun numero offerta trovato nel nome")
    else:
        print("ERRORE Opportunità 190 non trovata")

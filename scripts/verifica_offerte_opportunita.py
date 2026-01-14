#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica offerte associate a un'opportunità"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

def verifica_offerte_opportunita(opp_name_pattern):
    """Verifica offerte associate a un'opportunità"""
    with app.app_context():
        # Cerca opportunità
        opps = db.session.execute(text("""
            SELECT id, name FROM opportunities 
            WHERE name LIKE :pattern
        """), {"pattern": f"%{opp_name_pattern}%"}).fetchall()
        
        print(f"Opportunità trovate con pattern '{opp_name_pattern}':")
        for opp_id, opp_name in opps:
            print(f"\n  ID: {opp_id}, Nome: {opp_name}")
            
            # Cerca offerte associate
            offers = db.session.execute(text("""
                SELECT id, number, folder_path, opportunity_id
                FROM offers 
                WHERE opportunity_id = :opp_id
            """), {"opp_id": opp_id}).fetchall()
            
            print(f"  Offerte associate: {len(offers)}")
            for offer_id, offer_number, folder_path, opp_id_offer in offers:
                print(f"    - ID: {offer_id}, Numero: {offer_number}, Cartella: {folder_path or 'Nessuna'}")

if __name__ == '__main__':
    import sys
    pattern = sys.argv[1] if len(sys.argv) > 1 else "K1550"
    verifica_offerte_opportunita(pattern)

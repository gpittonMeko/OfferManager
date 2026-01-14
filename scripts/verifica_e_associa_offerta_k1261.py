#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica e associa offerta K1261-25 all'opportunità corretta"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

def verifica_e_associa():
    """Verifica e associa offerta K1261-25"""
    with app.app_context():
        print("=" * 60)
        print("VERIFICA E ASSOCIAZIONE OFFERTA K1261-25")
        print("=" * 60)
        
        # Trova offerta K1261-25
        offer_result = db.session.execute(text("""
            SELECT id, number, folder_path, status, amount, opportunity_id
            FROM offers 
            WHERE number = 'K1261-25'
        """)).fetchone()
        
        if not offer_result:
            print("❌ Offerta K1261-25 NON TROVATA nel database!")
            return
        
        offer_id, offer_number, folder_path, status, amount, opp_id = offer_result
        print(f"\n✅ Offerta trovata:")
        print(f"   ID: {offer_id}")
        print(f"   Numero: {offer_number}")
        print(f"   Folder: {folder_path}")
        print(f"   Status: {status}")
        print(f"   Amount: {amount}")
        print(f"   Opportunity ID attuale: {opp_id}")
        
        # Trova opportunità corretta (108)
        opp_result = db.session.execute(text("""
            SELECT id, name, account_id
            FROM opportunities 
            WHERE id = 108
        """)).fetchone()
        
        if not opp_result:
            print("\n❌ Opportunità 108 NON TROVATA!")
            return
        
        opp_id_correct, opp_name, account_id = opp_result
        print(f"\n✅ Opportunità corretta trovata:")
        print(f"   ID: {opp_id_correct}")
        print(f"   Nome: {opp_name}")
        print(f"   Account ID: {account_id}")
        
        # Verifica se l'offerta è già associata correttamente
        if opp_id == opp_id_correct:
            print(f"\n✅ L'offerta è già associata correttamente all'opportunità {opp_id_correct}!")
            return
        
        # Associa l'offerta all'opportunità corretta
        print(f"\n🔄 Associazione offerta {offer_id} all'opportunità {opp_id_correct}...")
        db.session.execute(text("""
            UPDATE offers 
            SET opportunity_id = :opp_id
            WHERE id = :offer_id
        """), {
            "opp_id": opp_id_correct,
            "offer_id": offer_id
        })
        db.session.commit()
        
        print(f"✅ Offerta associata con successo!")
        
        # Verifica finale
        offer_updated = db.session.execute(text("""
            SELECT id, number, opportunity_id
            FROM offers 
            WHERE id = :offer_id
        """), {"offer_id": offer_id}).fetchone()
        
        print(f"\n📋 Verifica finale:")
        print(f"   Offerta ID: {offer_updated[0]}")
        print(f"   Numero: {offer_updated[1]}")
        print(f"   Opportunity ID: {offer_updated[2]}")

if __name__ == '__main__':
    verifica_e_associa()

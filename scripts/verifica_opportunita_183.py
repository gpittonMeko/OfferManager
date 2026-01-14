#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità 183 e offerte associate"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

def verifica_opportunita_183():
    """Verifica opportunità 183 e offerte associate"""
    with app.app_context():
        print("=" * 60)
        print("VERIFICA OPPORTUNITÀ 183 (K1261-25)")
        print("=" * 60)
        
        # Verifica opportunità 183
        opp_result = db.session.execute(text("""
            SELECT id, name, account_id, folder_path, stage, amount
            FROM opportunities 
            WHERE id = 183
        """)).fetchone()
        
        if not opp_result:
            print("❌ Opportunità 183 NON TROVATA nel database!")
            return
        
        opp_id, opp_name, account_id, folder_path, stage, amount = opp_result
        print(f"\n✅ Opportunità trovata:")
        print(f"   ID: {opp_id}")
        print(f"   Nome: {opp_name}")
        print(f"   Account ID: {account_id}")
        print(f"   Folder Path: {folder_path}")
        print(f"   Stage: {stage}")
        print(f"   Amount: {amount}")
        
        # Verifica offerte associate
        offers_result = db.session.execute(text("""
            SELECT id, number, folder_path, status, amount, opportunity_id
            FROM offers 
            WHERE opportunity_id = 183
        """)).fetchall()
        
        print(f"\n📋 Offerte associate a opportunity_id=183: {len(offers_result)}")
        if offers_result:
            for offer in offers_result:
                print(f"   - ID: {offer[0]}, Numero: {offer[1]}, Folder: {offer[2]}, Status: {offer[3]}, Amount: {offer[4]}")
        else:
            print("   ⚠️  Nessuna offerta associata!")
        
        # Cerca offerte con numero K1261-25 che potrebbero non essere associate
        print(f"\n🔍 Cerca offerte con numero K1261-25 (non associate):")
        offers_k1261 = db.session.execute(text("""
            SELECT id, number, folder_path, status, amount, opportunity_id
            FROM offers 
            WHERE number LIKE '%1261%' OR number LIKE '%K1261%'
        """)).fetchall()
        
        if offers_k1261:
            print(f"   Trovate {len(offers_k1261)} offerte con numero contenente '1261':")
            for offer in offers_k1261:
                print(f"   - ID: {offer[0]}, Numero: {offer[1]}, Folder: {offer[2]}, Status: {offer[3]}, Amount: {offer[4]}, Opportunity ID: {offer[5]}")
        else:
            print("   ⚠️  Nessuna offerta trovata con numero contenente '1261'")
        
        # Cerca tutte le opportunità con nome contenente K1261
        print(f"\n🔍 Cerca opportunità con nome contenente 'K1261' o '1261':")
        opps_k1261 = db.session.execute(text("""
            SELECT id, name, account_id, folder_path
            FROM opportunities 
            WHERE name LIKE '%1261%' OR name LIKE '%K1261%'
        """)).fetchall()
        
        if opps_k1261:
            print(f"   Trovate {len(opps_k1261)} opportunità:")
            for opp in opps_k1261:
                print(f"   - ID: {opp[0]}, Nome: {opp[1]}, Account ID: {opp[2]}, Folder: {opp[3]}")
        else:
            print("   ⚠️  Nessuna opportunità trovata con nome contenente '1261'")
        
        # Verifica account associato
        if account_id:
            account_result = db.session.execute(text("""
                SELECT id, name
                FROM accounts 
                WHERE id = :account_id
            """), {"account_id": account_id}).fetchone()
            
            if account_result:
                print(f"\n🏢 Account associato:")
                print(f"   ID: {account_result[0]}, Nome: {account_result[1]}")

if __name__ == '__main__':
    verifica_opportunita_183()

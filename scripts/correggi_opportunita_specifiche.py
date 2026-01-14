#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correggi opportunità specifiche segnalate dall'utente"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import re

def trova_e_associa_offerta(opp_id, opp_name):
    """Trova e associa l'offerta all'opportunità"""
    print(f"\n{'='*60}")
    print(f"Opportunità ID: {opp_id}")
    print(f"Nome: {opp_name}")
    
    # Estrai numero offerta dal nome
    match = re.search(r'K(\d{4})-(\d{2})', opp_name)
    if not match:
        # Prova pattern alternativo (es. "K0390" senza "-25")
        match = re.search(r'K(\d{4})', opp_name)
        if match:
            offer_number = f"K{match.group(1)}-25"  # Assumi anno 25
            print(f"⚠️  Pattern alternativo trovato: {offer_number}")
        else:
            print(f"❌ Nessun numero offerta trovato nel nome")
            return False
    else:
        offer_number = match.group(0)
    
    print(f"Numero offerta cercato: {offer_number}")
    
    # Verifica offerte già associate
    offers_attuali = db.session.execute(text("""
        SELECT id, number FROM offers WHERE opportunity_id = :opp_id
    """), {"opp_id": opp_id}).fetchall()
    
    if offers_attuali:
        print(f"✅ Già ha {len(offers_attuali)} offerte associate:")
        for off in offers_attuali:
            print(f"   - {off[1]}")
        return True
    
    # Cerca offerta con questo numero
    offer = db.session.execute(text("""
        SELECT id, number, opportunity_id FROM offers WHERE number = :num
    """), {"num": offer_number}).fetchone()
    
    if offer:
        print(f"✅ Offerta trovata: ID={offer[0]}, attualmente associata a opportunity_id={offer[2]}")
        if offer[2] != opp_id:
            print(f"🔄 Associazione offerta {offer[0]} all'opportunità {opp_id}...")
            db.session.execute(text("""
                UPDATE offers SET opportunity_id = :opp_id WHERE id = :offer_id
            """), {"opp_id": opp_id, "offer_id": offer[0]})
            db.session.commit()
            print(f"✅ Corretto!")
            return True
        else:
            print(f"✅ Già associata correttamente")
            return True
    else:
        print(f"❌ Offerta {offer_number} NON TROVATA nel database")
        return False

with app.app_context():
    print("=" * 60)
    print("CORREZIONE OPPORTUNITÀ SPECIFICHE")
    print("=" * 60)
    
    # Cerca opportunità per nome
    opportunita_da_correggere = [
        ("K0390", "K0390"),
        ("K1470-25", "K1470-25"),
        ("K1041-25", "K1041-25")
    ]
    
    for pattern, offer_num in opportunita_da_correggere:
        # Cerca opportunità che contengono il pattern
        opps = db.session.execute(text("""
            SELECT id, name FROM opportunities 
            WHERE name LIKE :pattern
        """), {"pattern": f"%{pattern}%"}).fetchall()
        
        for opp_id, opp_name in opps:
            trova_e_associa_offerta(opp_id, opp_name)
    
    print(f"\n{'='*60}")
    print("VERIFICA FINALE")
    print("=" * 60)
    
    # Verifica finale
    for pattern, offer_num in opportunita_da_correggere:
        opps = db.session.execute(text("""
            SELECT id, name FROM opportunities 
            WHERE name LIKE :pattern
        """), {"pattern": f"%{pattern}%"}).fetchall()
        
        for opp_id, opp_name in opps:
            offers = db.session.execute(text("""
                SELECT COUNT(*) FROM offers WHERE opportunity_id = :opp_id
            """), {"opp_id": opp_id}).fetchone()[0]
            
            if offers > 0:
                print(f"✅ Opportunità {opp_id} ({opp_name}): {offers} offerte associate")
            else:
                print(f"❌ Opportunità {opp_id} ({opp_name}): NESSUNA offerta associata")

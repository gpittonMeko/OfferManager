#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità 71"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Verifica opportunità 71
    opp = db.session.execute(text("SELECT id, name FROM opportunities WHERE id = 71")).fetchone()
    print(f"Opportunità 71: {opp[1] if opp else 'NON TROVATA'}")
    
    # Cerca offerte associate
    offers = db.session.execute(text("SELECT id, number, opportunity_id FROM offers WHERE opportunity_id = 71")).fetchall()
    print(f"Offerte associate: {len(offers)}")
    for off in offers:
        print(f"  - ID: {off[0]}, Numero: {off[1]}")
    
    # Cerca offerta K0800-25
    offer = db.session.execute(text("SELECT id, number, opportunity_id FROM offers WHERE number = 'K0800-25'")).fetchone()
    if offer:
        print(f"\nOfferta K0800-25 trovata: ID={offer[0]}, associata a opportunity_id={offer[2]}")
        if offer[2] != 71:
            print(f"🔄 Correzione: associazione offerta {offer[0]} all'opportunità 71...")
            db.session.execute(text("UPDATE offers SET opportunity_id = 71 WHERE id = :id"), {"id": offer[0]})
            db.session.commit()
            print("✅ Corretto!")
    else:
        print("❌ Offerta K0800-25 NON TROVATA nel database")

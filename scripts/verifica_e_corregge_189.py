#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica e correggi opportunità 189"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Verifica opportunità 189
    opp = db.session.execute(text("SELECT id, name FROM opportunities WHERE id = 189")).fetchone()
    print(f"Opportunità 189: {opp[1] if opp else 'NON TROVATA'}")
    
    # Cerca offerta K0800-25
    offer = db.session.execute(text("SELECT id, number, opportunity_id FROM offers WHERE number = 'K0800-25'")).fetchone()
    if offer:
        print(f"Offerta K0800-25 trovata: ID={offer[0]}, associata a opportunity_id={offer[2]}")
        if offer[2] != 189:
            print(f"🔄 Associazione offerta {offer[0]} all'opportunità 189...")
            db.session.execute(text("UPDATE offers SET opportunity_id = 189 WHERE id = :id"), {"id": offer[0]})
            db.session.commit()
            print("✅ Corretto!")
    else:
        print("❌ Offerta K0800-25 NON TROVATA nel database")

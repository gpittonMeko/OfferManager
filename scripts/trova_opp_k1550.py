#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trova opportunità K1550-25"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Trova tutte le opportunità che contengono K1550
    opps = db.session.execute(text("""
        SELECT id, name FROM opportunities 
        WHERE name LIKE '%K1550%'
        ORDER BY id
    """)).fetchall()
    
    print("Tutte le opportunità con K1550:")
    for o in opps:
        offers_count = db.session.execute(text("""
            SELECT COUNT(*) FROM offers WHERE opportunity_id = :opp_id
        """), {"opp_id": o[0]}).fetchone()[0]
        
        print(f"  ID: {o[0]}, Nome: {o[1]}, Offerte: {offers_count}")
        
        if offers_count > 0:
            offers = db.session.execute(text("""
                SELECT id, number FROM offers WHERE opportunity_id = :opp_id
            """), {"opp_id": o[0]}).fetchall()
            for off in offers:
                print(f"    - {off[1]}")

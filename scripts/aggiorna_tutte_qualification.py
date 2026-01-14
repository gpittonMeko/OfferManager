#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna tutte le opportunità a stage Qualification"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Aggiorna tutte le opportunità a Qualification
    result = db.session.execute(text("""
        UPDATE opportunities 
        SET stage = 'Qualification'
        WHERE stage IS NULL OR stage != 'Qualification'
    """))
    db.session.commit()
    
    print(f"✅ Aggiornate {result.rowcount} opportunità a stage 'Qualification'")

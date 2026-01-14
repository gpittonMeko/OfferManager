#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test connessione database"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, User, Opportunity, app

with app.app_context():
    try:
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Database file exists: {os.path.exists('crm.db')}")
        
        # Prova a contare gli utenti
        user_count = User.query.count()
        print(f"✅ Users count: {user_count}")
        
        # Prova a contare le opportunità
        opp_count = Opportunity.query.count()
        print(f"✅ Opportunities count: {opp_count}")
        
        print("✅ Database connesso correttamente!")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

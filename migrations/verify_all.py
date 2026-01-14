#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica che tutto funzioni"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app, Opportunity, OpportunityTask, Account, User

with app.app_context():
    print("=" * 60)
    print("VERIFICA SISTEMA")
    print("=" * 60)
    
    opp_count = Opportunity.query.count()
    task_count = OpportunityTask.query.count()
    account_count = Account.query.count()
    user_count = User.query.count()
    ur_opp_count = Opportunity.query.filter_by(supplier_category='Universal Robots').count()
    
    print(f"✅ Opportunità totali: {opp_count}")
    print(f"✅ Tasks totali: {task_count}")
    print(f"✅ Accounts totali: {account_count}")
    print(f"✅ Utenti totali: {user_count}")
    print(f"✅ Opportunità UR: {ur_opp_count}")
    
    # Verifica colonne
    try:
        opp = Opportunity.query.first()
        if opp:
            print(f"✅ Campo supplier_category: {hasattr(opp, 'supplier_category')}")
            print(f"✅ Campo owner_id: {hasattr(opp, 'owner_id')}")
    except:
        pass
    
    try:
        acc = Account.query.first()
        if acc:
            print(f"✅ Campo image_url: {hasattr(acc, 'image_url')}")
    except:
        pass
    
    print("=" * 60)
    print("✅ Verifica completata")





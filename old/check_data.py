#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dati nel database"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import Lead, Account, Opportunity, User, db, app

with app.app_context():
    print("=" * 60)
    print("VERIFICA DATI NEL DATABASE")
    print("=" * 60)
    
    leads_count = Lead.query.count()
    accounts_count = Account.query.count()
    opps_count = Opportunity.query.count()
    users_count = User.query.count()
    
    print(f"\n📊 Conteggi:")
    print(f"  Leads: {leads_count}")
    print(f"  Accounts: {accounts_count}")
    print(f"  Opportunities: {opps_count}")
    print(f"  Users: {users_count}")
    
    if leads_count > 0:
        print(f"\n📋 Primi 3 Leads:")
        for l in Lead.query.limit(3).all():
            print(f"  - {l.company_name} (Owner: {l.owner_id})")
    
    if accounts_count > 0:
        print(f"\n🏢 Primi 3 Accounts:")
        for a in Account.query.limit(3).all():
            print(f"  - {a.name} (Owner: {a.owner_id})")
    
    if opps_count > 0:
        print(f"\n💼 Primi 3 Opportunities:")
        for o in Opportunity.query.limit(3).all():
            print(f"  - {o.name} (Owner: {o.owner_id}, Category: {o.supplier_category})")





#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dettagliata dei leads"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import Lead, Account, Opportunity, User, db, app

with app.app_context():
    print("=" * 80)
    print("VERIFICA DETTAGLIATA LEADS")
    print("=" * 80)
    
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()
    print(f"\n📊 Totale Leads: {len(all_leads)}\n")
    
    for i, lead in enumerate(all_leads, 1):
        print(f"{i}. ID: {lead.id}")
        print(f"   Company: {lead.company_name}")
        print(f"   Contact: {lead.contact_first_name} {lead.contact_last_name}")
        print(f"   Email: {lead.email}")
        print(f"   Phone: {lead.phone}")
        print(f"   Status: {lead.status}")
        print(f"   Source: {lead.source}")
        print(f"   Owner ID: {lead.owner_id}")
        print(f"   Created: {lead.created_at}")
        print()
    
    # Cerca duplicati per company_name
    print("\n" + "=" * 80)
    print("RICERCA DUPLICATI")
    print("=" * 80)
    from collections import Counter
    company_names = [l.company_name for l in all_leads]
    duplicates = {name: count for name, count in Counter(company_names).items() if count > 1}
    
    if duplicates:
        print(f"\n⚠️  Trovati {len(duplicates)} nomi duplicati:\n")
        for name, count in duplicates.items():
            print(f"  - {name}: {count} occorrenze")
            leads_with_name = Lead.query.filter_by(company_name=name).all()
            for l in leads_with_name:
                print(f"    → ID {l.id}, Email: {l.email}, Status: {l.status}")
    else:
        print("\n✅ Nessun duplicato trovato per company_name")





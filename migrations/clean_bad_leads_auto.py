#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pulisce automaticamente leads farlocchi dal database"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import Lead, db, app

with app.app_context():
    print("=" * 80)
    print("PULIZIA AUTOMATICA LEADS FARLOcchi")
    print("=" * 80)
    
    # Trova leads problematici
    bad_patterns = [
        "Locked Partner",
        "Test Company",
        "Edit Lead Status",
        "SQL Edit"
    ]
    
    bad_leads = []
    for pattern in bad_patterns:
        leads = Lead.query.filter(Lead.company_name.contains(pattern)).all()
        bad_leads.extend(leads)
    
    # Rimuovi duplicati mantenendo l'ordine
    seen = set()
    unique_bad_leads = []
    for lead in bad_leads:
        if lead.id not in seen:
            seen.add(lead.id)
            unique_bad_leads.append(lead)
    
    print(f"\n📋 Trovati {len(unique_bad_leads)} leads problematici:\n")
    for lead in unique_bad_leads:
        print(f"  - ID {lead.id}: {lead.company_name}")
        print(f"    Contact: {lead.contact_first_name} {lead.contact_last_name}")
        print(f"    Email: {lead.email}")
        print()
    
    if unique_bad_leads:
        print(f"\n🗑️  Eliminazione di {len(unique_bad_leads)} leads problematici...")
        for lead in unique_bad_leads:
            db.session.delete(lead)
        db.session.commit()
        print(f"✅ Eliminati {len(unique_bad_leads)} leads problematici")
    else:
        print("\n✅ Nessun lead problematico trovato")





#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controlla leads nel database"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, Lead

if __name__ == '__main__':
    with app.app_context():
        leads = Lead.query.all()
        print(f"📊 Totale leads nel database: {len(leads)}")
        print("\n" + "="*80)
        
        problematic_leads = []
        for lead in leads:
            issues = []
            if 'Locked Partner' in lead.company_name or 'Edit Lead Status' in lead.company_name:
                issues.append("Company name contiene testo di sistema")
            if 'SQL Edit' in lead.company_name or 'SQL Edit' in (lead.contact_first_name or ''):
                issues.append("Nome contiene testo di sistema")
            if lead.status == 'Converted' and 'SQL' in (lead.company_name or ''):
                issues.append("Status Converted ma contiene SQL")
            if not lead.email and not lead.phone:
                issues.append("Manca email e telefono")
            
            if issues:
                problematic_leads.append((lead, issues))
                print(f"⚠️  Lead ID {lead.id}: {lead.company_name}")
                print(f"   Nome: {lead.contact_first_name} {lead.contact_last_name}")
                print(f"   Status: {lead.status}")
                print(f"   Problemi: {', '.join(issues)}")
                print()
        
        print(f"\n📊 Leads problematici: {len(problematic_leads)}/{len(leads)}")
        
        # Mostra alcuni leads corretti
        print("\n✅ Esempi leads corretti:")
        good_leads = [l for l in leads if l not in [p[0] for p in problematic_leads]][:5]
        for lead in good_leads:
            print(f"  ✓ {lead.company_name} - {lead.contact_first_name} {lead.contact_last_name} - Status: {lead.status}")





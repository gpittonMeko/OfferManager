#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test sync UR"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import Opportunity, Lead, db, app
from ur_portal_integration import sync_ur_portal

with app.app_context():
    print("=" * 60)
    print("TEST SYNC UR PORTAL")
    print("=" * 60)
    
    opp_before = Opportunity.query.count()
    lead_before = Lead.query.count()
    
    print(f"Prima: {opp_before} opportunità, {lead_before} leads")
    
    stats = sync_ur_portal(db.session, 1)
    
    opp_after = Opportunity.query.count()
    lead_after = Lead.query.count()
    
    print(f"\nDopo: {opp_after} opportunità, {lead_after} leads")
    print(f"\nStatistiche sync:")
    print(f"  Opportunità create: {stats.get('opportunities_imported', 0)}")
    print(f"  Opportunità aggiornate: {stats.get('opportunities_updated', 0)}")
    print(f"  Leads creati: {stats.get('leads_imported', 0)}")
    print(f"  Leads aggiornati: {stats.get('leads_updated', 0)}")
    print(f"  Errori: {len(stats.get('errors', []))}")
    
    print("=" * 60)





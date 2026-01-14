#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test rapido sincronizzazione UR Portal"""
from ur_portal_direct_playwright import fetch_ur_data_direct
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    stream=sys.stdout
)

print("=" * 60)
print("TEST SINCRONIZZAZIONE UR PORTAL")
print("=" * 60)

try:
    result = fetch_ur_data_direct()
    
    print("\n" + "=" * 60)
    print("RISULTATI")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Opportunities: {len(result.get('opportunities', []))}")
    print(f"Leads: {len(result.get('leads', []))}")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    if result.get('opportunities'):
        print(f"\nPrime 3 Opportunities:")
        for i, opp in enumerate(result['opportunities'][:3], 1):
            print(f"  {i}. {opp.get('name', 'N/A')[:50]} - {opp.get('account_name', 'N/A')[:30]}")
    
    if result.get('leads'):
        print(f"\nTutti i Leads trovati ({len(result['leads'])}):")
        for i, lead in enumerate(result['leads'], 1):
            print(f"  {i}. {lead.get('name', 'N/A')}")
            print(f"     Email: {lead.get('email', 'N/A')}")
            print(f"     Phone: {lead.get('phone', 'N/A')}")
            print(f"     Status: {lead.get('lead_status', 'N/A')}")
            print(f"     Country: {lead.get('country', 'N/A')}")
            print(f"     Partner: {lead.get('partner', 'N/A')}")
            print()
    else:
        print("\n⚠ Nessun lead trovato!")
    
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


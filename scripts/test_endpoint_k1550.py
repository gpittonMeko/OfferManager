#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test endpoint per K1550-25"""
import sys
import os
import requests
import json

# Test endpoint sul server AWS
server_url = "http://13.53.183.146:8000"

# Trova ID opportunità K1550-25
print("Cerca opportunità K1550-25...")
response = requests.get(f"{server_url}/api/opportunities")
if response.ok:
    data = response.json()
    opp_id = None
    for opp in data.get('opportunities', []):
        if 'K1550-25' in opp.get('name', ''):
            opp_id = opp['id']
            print(f"✅ Trovata: ID={opp_id}, Nome={opp['name']}")
            break
    
    if opp_id:
        print(f"\nTest endpoint files per opportunità {opp_id}...")
        # Simula sessione (potrebbe non funzionare senza login, ma proviamo)
        session = requests.Session()
        # Prova a fare login prima
        login_response = session.post(f"{server_url}/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        if login_response.ok:
            print("✅ Login effettuato")
        else:
            print("⚠️  Login fallito, provo comunque...")
        
        # Test endpoint files
        files_response = session.get(f"{server_url}/api/opportunities/{opp_id}/files")
        print(f"\nStatus Code: {files_response.status_code}")
        
        if files_response.ok:
            files_data = files_response.json()
            print(f"\nRisposta:")
            print(f"  File trovati: {files_data.get('files_found', 0)}")
            print(f"  Offerte associate: {files_data.get('offers_count', 0)}")
            print(f"  File: {len(files_data.get('files', []))}")
            
            if files_data.get('files'):
                print(f"\nFile trovati:")
                for f in files_data['files']:
                    print(f"  - {f.get('name')}")
            else:
                print(f"\n❌ NESSUN FILE TROVATO")
                print(f"\nDettagli risposta:")
                print(json.dumps(files_data, indent=2))
        else:
            print(f"❌ Errore: {files_response.status_code}")
            print(files_response.text)
    else:
        print("❌ Opportunità K1550-25 non trovata")
else:
    print(f"❌ Errore API: {response.status_code}")

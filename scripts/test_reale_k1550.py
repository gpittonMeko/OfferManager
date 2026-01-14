#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test REALE endpoint K1550-25 con login"""
import requests
import json
import sys
import io

# Fix encoding per Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

server_url = "http://crm.infomekosrl.it:8000"

print("=" * 60)
print("TEST ENDPOINT K1550-25")
print("=" * 60)

# Crea sessione
session = requests.Session()

# Login
print("\n1. Login...")
login_response = session.post(f"{server_url}/login", json={
    "username": "admin",
    "password": "admin"
})

if not login_response.ok:
    print(f"ERRORE Login fallito: {login_response.status_code}")
    print(login_response.text)
    exit(1)

print("OK Login effettuato")

# Trova opportunità K1550-25
print("\n2. Cerca opportunità K1550-25...")
opps_response = session.get(f"{server_url}/api/opportunities")
if not opps_response.ok:
    print(f"❌ Errore recupero opportunità: {opps_response.status_code}")
    exit(1)

opps_data = opps_response.json()
opp_id = None
for opp in opps_data.get('opportunities', []):
    if 'K1550-25' in opp.get('name', ''):
        opp_id = opp['id']
        print(f"OK Trovata: ID={opp_id}, Nome={opp['name']}")
        break

if not opp_id:
    print("ERRORE Opportunita K1550-25 non trovata")
    exit(1)

# Test endpoint files
print(f"\n3. Test endpoint files per opportunita {opp_id}...")
files_response = session.get(f"{server_url}/api/opportunities/{opp_id}/files")

print(f"Status Code: {files_response.status_code}")

if files_response.ok:
    files_data = files_response.json()
    print(f"\nOK RISPOSTA:")
    print(f"  File trovati: {files_data.get('files_found', 0)}")
    print(f"  Offerte associate: {files_data.get('offers_count', 0)}")
    print(f"  File nella lista: {len(files_data.get('files', []))}")
    
    if files_data.get('files'):
        print(f"\nFILE TROVATI:")
        for i, f in enumerate(files_data['files'], 1):
            print(f"\n  {i}. {f.get('name')}")
            print(f"     Tipo: {f.get('type')}")
            print(f"     Estensione: {f.get('extension')}")
            print(f"     Dimensione: {f.get('size', 0)} bytes")
            if f.get('smb_path'):
                print(f"     SMB Path: {f.get('smb_path')}")
            if f.get('path'):
                print(f"     Path: {f.get('path')}")
    else:
        print(f"\nERRORE NESSUN FILE TROVATO")
        print(f"\nDettagli risposta completa:")
        print(json.dumps(files_data, indent=2, ensure_ascii=False))
else:
    print(f"ERRORE: {files_response.status_code}")
    print(files_response.text)

print("\n" + "=" * 60)

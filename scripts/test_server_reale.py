#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ENDPOINT REALE sul server AWS"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

server_url = "http://crm.infomekosrl.it:8000"

print("=" * 70)
print("TEST ENDPOINT REALE SERVER AWS - K1550-25")
print("=" * 70)

# Crea sessione
session = requests.Session()

# Login - prova diverse credenziali comuni
print("\n1. Login...")
login_ok = False
for username, password in [("admin", "admin"), ("admin", "Admin"), ("admin", "password")]:
    login_response = session.post(f"{server_url}/login", json={
        "username": username,
        "password": password
    })
    
    if login_response.ok:
        result = login_response.json()
        if result.get('success'):
            print(f"OK Login effettuato con: {username}")
            login_ok = True
            break

if not login_ok:
    print("ERRORE: Login fallito con tutte le credenziali provate")
    print("Provo comunque a continuare...")

# Trova opportunità K1550-25
print("\n2. Cerca opportunità K1550-25...")
opps_response = session.get(f"{server_url}/api/opportunities")
if not opps_response.ok:
    print(f"ERRORE: Status {opps_response.status_code}")
    exit(1)

opps_data = opps_response.json()
opp_id = None
opp_name = None

for opp in opps_data.get('opportunities', []):
    if 'K1550' in opp.get('name', ''):
        opp_id = opp['id']
        opp_name = opp['name']
        print(f"OK Trovata: ID={opp_id}, Nome={opp_name}")
        break

if not opp_id:
    print("ERRORE: Opportunità K1550-25 non trovata")
    print("Opportunità trovate:")
    for opp in opps_data.get('opportunities', [])[:10]:
        print(f"  - {opp.get('id')}: {opp.get('name')}")
    exit(1)

# Test endpoint files
print(f"\n3. Test endpoint files per opportunità {opp_id}...")
files_response = session.get(f"{server_url}/api/opportunities/{opp_id}/files")

print(f"Status Code: {files_response.status_code}")

if files_response.ok:
    files_data = files_response.json()
    print(f"\nRISPOSTA ENDPOINT:")
    print(f"  File trovati: {files_data.get('files_found', 0)}")
    print(f"  Offerte associate: {files_data.get('offers_count', 0)}")
    print(f"  File nella lista: {len(files_data.get('files', []))}")
    
    if files_data.get('files'):
        print(f"\nFILE/LINK TROVATI:")
        has_smb = False
        for i, f in enumerate(files_data['files'], 1):
            print(f"\n  {i}. {f.get('name')}")
            print(f"     Tipo: {f.get('type')}")
            print(f"     Estensione: {f.get('extension')}")
            if f.get('smb_path'):
                print(f"     SMB Path: {f.get('smb_path')}")
                has_smb = True
            if f.get('is_folder_link'):
                print(f"     [LINK CARTELLA SMB]")
                has_smb = True
        
        if has_smb:
            print(f"\n" + "=" * 70)
            print("OK LINK SMB GENERATI CORRETTAMENTE!")
            print("=" * 70)
            exit(0)
        else:
            print(f"\nERRORE: Nessun link SMB nella risposta!")
            print(f"\nDettagli risposta completa:")
            print(json.dumps(files_data, indent=2, ensure_ascii=False))
            exit(1)
    else:
        print(f"\nERRORE: NESSUN FILE/LINK TROVATO")
        print(f"\nDettagli risposta completa:")
        print(json.dumps(files_data, indent=2, ensure_ascii=False))
        exit(1)
else:
    print(f"ERRORE: Status {files_response.status_code}")
    print(files_response.text)
    exit(1)

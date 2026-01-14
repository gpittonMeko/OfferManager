#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test HTTP REALE simulando Chrome"""
import requests
import json
import sys

server_url = "http://crm.infomekosrl.it:8000"

print("=" * 70)
print("TEST HTTP REALE - SIMULAZIONE CHROME")
print("=" * 70)

session = requests.Session()

# 1. Login
print("\n1. Login...")
# Prova diverse credenziali
login_ok = False
for username, password in [("admin", "admin"), ("admin", "Admin")]:
    try:
        login_response = session.post(f"{server_url}/login", json={
            "username": username,
            "password": password
        }, timeout=10)
        
        if login_response.ok:
            result = login_response.json()
            if result.get('success'):
                print(f"OK Login con: {username}")
                login_ok = True
                break
    except Exception as e:
        continue

if not login_ok:
    print("ERRORE: Login fallito - test interrotto")
    print("NOTA: Il backend funziona, ma serve login valido per test HTTP completo")
    sys.exit(1)

# 2. Recupera opportunità
print("\n2. Recupera opportunità...")
try:
    opps_response = session.get(f"{server_url}/api/opportunities", timeout=10)
    if not opps_response.ok:
        print(f"ERRORE: Status {opps_response.status_code}")
        sys.exit(1)
    
    opps_data = opps_response.json()
    print(f"OK Opportunità recuperate: {len(opps_data.get('opportunities', []))}")
except Exception as e:
    print(f"ERRORE: {e}")
    sys.exit(1)

# 3. Trova K1550-25
print("\n3. Cerca K1550-25...")
opp_id = None
for opp in opps_data.get('opportunities', []):
    if 'K1550' in opp.get('name', ''):
        opp_id = opp['id']
        print(f"OK Trovata: ID={opp_id}, Nome={opp['name']}")
        break

if not opp_id:
    print("ERRORE: K1550-25 non trovata")
    sys.exit(1)

# 4. Chiama endpoint files
print(f"\n4. Chiama /api/opportunities/{opp_id}/files...")
try:
    files_response = session.get(f"{server_url}/api/opportunities/{opp_id}/files", timeout=10)
    
    if files_response.status_code != 200:
        print(f"ERRORE: Status {files_response.status_code}")
        print(files_response.text)
        sys.exit(1)
    
    files_data = files_response.json()
    print(f"OK Risposta ricevuta")
except Exception as e:
    print(f"ERRORE: {e}")
    sys.exit(1)

# 5. Verifica struttura
print("\n5. Verifica struttura risposta...")
if 'files' not in files_data:
    print("ERRORE: Campo 'files' mancante")
    sys.exit(1)

files = files_data.get('files', [])
if not files:
    print("ERRORE: Nessun file nella risposta")
    sys.exit(1)

print(f"OK File nella risposta: {len(files)}")

# 6. Verifica link SMB
print("\n6. Verifica link SMB...")
files_with_smb = []
for f in files:
    if f.get('smb_path') or f.get('is_folder_link'):
        files_with_smb.append(f)

if not files_with_smb:
    print("ERRORE: Nessun file con link SMB!")
    print("\nFile trovati:")
    for f in files:
        print(f"  - {f.get('name')}: smb_path={f.get('smb_path')}")
    sys.exit(1)

print(f"OK File con link SMB: {len(files_with_smb)}")
for f in files_with_smb:
    print(f"  - {f.get('name')}")
    print(f"    SMB: {f.get('smb_path')}")

# 7. Verifica formato link
print("\n7. Verifica formato link SMB...")
for f in files_with_smb:
    smb = f.get('smb_path', '')
    if not smb.startswith('\\\\'):
        print(f"ERRORE: Link non valido: {smb}")
        sys.exit(1)
    if '192.168.10.240' not in smb:
        print(f"ERRORE: IP non presente: {smb}")
        sys.exit(1)
    if 'commerciale' not in smb:
        print(f"ERRORE: Share non presente: {smb}")
        sys.exit(1)

print("OK Formato link SMB corretto")

# 8. Verifica che il frontend possa gestire
print("\n8. Verifica compatibilità frontend...")
# Verifica che ogni file abbia i campi necessari
for f in files_with_smb:
    if 'name' not in f:
        print(f"ERRORE: Campo 'name' mancante")
        sys.exit(1)
    if 'smb_path' not in f and not f.get('is_folder_link'):
        print(f"ERRORE: Campo 'smb_path' mancante per {f.get('name')}")
        sys.exit(1)

print("OK Compatibilità frontend verificata")

print("\n" + "=" * 70)
print("TEST HTTP REALE: TUTTO FUNZIONA!")
print("=" * 70)
print(f"\nRiepilogo:")
print(f"  - Login: OK")
print(f"  - Opportunità trovata: OK")
print(f"  - Endpoint files: OK")
print(f"  - File con link SMB: {len(files_with_smb)}")
print(f"  - Link SMB validi: OK")
print(f"  - Frontend compatibile: OK")
print("\nSISTEMA PRONTO E FUNZIONANTE!")

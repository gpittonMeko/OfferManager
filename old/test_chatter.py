#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test specifico per la funzionalità Chatter"""
import requests

BASE_URL = "http://localhost:8000"
SESSION = requests.Session()

# Login
print("🔐 Login...")
response = SESSION.post(f"{BASE_URL}/login", json={'username': 'admin', 'password': 'admin'})
if response.status_code != 200:
    print(f"❌ Login fallito: {response.status_code}")
    exit(1)
print("✅ Login OK")

# Ottieni opportunità
print("\n📋 Recupero opportunità...")
response = SESSION.get(f"{BASE_URL}/api/opportunities")
if response.status_code != 200:
    print(f"❌ Errore recupero opportunità: {response.status_code}")
    exit(1)

data = response.json()
opportunities = data.get('opportunities', [])
if not opportunities:
    print("⚠️  Nessuna opportunità disponibile, creo una di test...")
    # Crea opportunità di test
    response = SESSION.post(f"{BASE_URL}/api/opportunities", json={
        'name': 'Test Opportunity Chatter',
        'stage': 'Qualification',
        'amount': 1000
    })
    if response.status_code == 200:
        opp_id = response.json().get('opportunity_id')
        print(f"✅ Opportunità creata: {opp_id}")
    else:
        print(f"❌ Errore creazione opportunità: {response.status_code}")
        exit(1)
else:
    opp_id = opportunities[0]['id']
    print(f"✅ Opportunità trovata: {opp_id}")

# Test GET chatter
print(f"\n💬 Test GET chatter per opportunità {opp_id}...")
response = SESSION.get(f"{BASE_URL}/api/opportunities/{opp_id}/chatter")
if response.status_code == 200:
    data = response.json()
    print(f"✅ GET chatter OK - {len(data.get('posts', []))} messaggi trovati")
else:
    print(f"❌ GET chatter fallito: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

# Test POST chatter
print(f"\n📝 Test POST messaggio chatter...")
response = SESSION.post(f"{BASE_URL}/api/opportunities/{opp_id}/chatter", json={
    'message': 'Test messaggio chatter - ' + str(__import__('datetime').datetime.now())
})
if response.status_code == 200:
    data = response.json()
    print(f"✅ POST chatter OK")
    print(f"   Messaggio ID: {data.get('post', {}).get('id')}")
    print(f"   Autore: {data.get('post', {}).get('user_name')}")
else:
    print(f"❌ POST chatter fallito: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

# Verifica messaggio salvato
print(f"\n🔍 Verifica messaggio salvato...")
response = SESSION.get(f"{BASE_URL}/api/opportunities/{opp_id}/chatter")
if response.status_code == 200:
    data = response.json()
    posts = data.get('posts', [])
    print(f"✅ Messaggi totali: {len(posts)}")
    if posts:
        print(f"   Ultimo messaggio: {posts[0].get('message', '')[:50]}...")
        print(f"   Autore: {posts[0].get('user_name')}")

print("\n✅ Test chatter completato!")





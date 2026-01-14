#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test login per tutti gli utenti"""
import requests

BASE_URL = "http://localhost:8000"

users = [
    ('admin', 'admin'),
    ('filippo', 'filippo2025'),
    ('mariuzzo', 'mariuzzo2025'),
    ('giovanni', 'giovanni2025'),
    ('davide', 'davide2025'),
    ('mauro', 'mauro2025'),
    ('fima', 'fima2025')
]

print("=" * 60)
print("TEST LOGIN UTENTI")
print("=" * 60)

for username, password in users:
    session = requests.Session()
    try:
        response = session.post(f"{BASE_URL}/login", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ {username}: Login OK")
            else:
                print(f"❌ {username}: Login fallito - {data.get('error', 'Unknown')}")
        else:
            print(f"❌ {username}: Errore HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ {username}: Errore - {e}")

print("=" * 60)





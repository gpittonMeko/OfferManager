#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di test completo per tutte le funzionalità del CRM
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
SESSION = requests.Session()

def test_login():
    """Test login"""
    print("=" * 60)
    print("TEST 1: LOGIN")
    print("=" * 60)
    try:
        # Prova login con JSON (come richiesto dal codice)
        response = SESSION.post(f"{BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin'
        }, allow_redirects=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login funziona")
                return True
            else:
                print(f"⚠️  Login fallito: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"⚠️  Login status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Errore login: {e}")
        return False

def test_api_endpoints():
    """Test tutti gli endpoint API"""
    print("\n" + "=" * 60)
    print("TEST 2: ENDPOINT API")
    print("=" * 60)
    
    endpoints = [
        ('GET', '/api/dashboard/summary', 'Dashboard Summary'),
        ('GET', '/api/leads', 'Lista Leads'),
        ('GET', '/api/accounts', 'Lista Accounts'),
        ('GET', '/api/opportunities', 'Lista Opportunities'),
        ('GET', '/api/products', 'Lista Products'),
        ('GET', '/api/offers', 'Lista Offers'),
    ]
    
    results = {}
    for method, endpoint, name in endpoints:
        try:
            if method == 'GET':
                response = SESSION.get(f"{BASE_URL}{endpoint}")
            else:
                response = SESSION.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                results[endpoint] = True
            elif response.status_code == 401:
                print(f"⚠️  {name}: Richiede autenticazione")
                results[endpoint] = 'auth_required'
            else:
                print(f"❌ {name}: Status {response.status_code}")
                results[endpoint] = False
        except Exception as e:
            print(f"❌ {name}: Errore - {e}")
            results[endpoint] = False
    
    return results

def test_convert_lead():
    """Test conversione lead"""
    print("\n" + "=" * 60)
    print("TEST 3: CONVERSIONE LEAD")
    print("=" * 60)
    
    try:
        # Prima ottieni i leads
        response = SESSION.get(f"{BASE_URL}/api/leads")
        if response.status_code != 200:
            print(f"⚠️  Impossibile ottenere leads: {response.status_code}")
            return False
        
        leads = response.json().get('leads', [])
        if not leads:
            print("⚠️  Nessun lead disponibile per test")
            return False
        
        # Prendi il primo lead non convertito
        lead_to_convert = None
        for lead in leads:
            if lead.get('status') != 'Converted':
                lead_to_convert = lead
                break
        
        if not lead_to_convert:
            print("⚠️  Nessun lead non convertito disponibile")
            return False
        
        lead_id = lead_to_convert['id']
        print(f"📋 Test conversione Lead ID: {lead_id}")
        
        # Prova conversione
        response = SESSION.post(f"{BASE_URL}/api/leads/{lead_id}/convert")
        
        if response.status_code == 200:
            print("✅ Conversione lead funziona")
            return True
        elif response.status_code == 401:
            print("⚠️  Conversione richiede autenticazione")
            return 'auth_required'
        else:
            print(f"❌ Conversione fallita: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Errore test conversione: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ur_sync():
    """Test sincronizzazione UR"""
    print("\n" + "=" * 60)
    print("TEST 4: SINCRONIZZAZIONE UR PORTAL")
    print("=" * 60)
    
    try:
        response = SESSION.post(f"{BASE_URL}/api/ur/sync")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Sincronizzazione UR funziona")
                print(f"   Leads: {data.get('stats', {}).get('leads_imported', 0)}")
                print(f"   Opportunities: {data.get('stats', {}).get('opportunities_imported', 0)}")
                return True
            else:
                print(f"⚠️  Sincronizzazione fallita: {data.get('error', 'Unknown')}")
                return False
        elif response.status_code == 401:
            print("⚠️  Sincronizzazione richiede autenticazione")
            return 'auth_required'
        else:
            print(f"❌ Sincronizzazione errore: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore test sincronizzazione: {e}")
        return False

def test_create_lead():
    """Test creazione lead"""
    print("\n" + "=" * 60)
    print("TEST 5: CREAZIONE LEAD")
    print("=" * 60)
    
    try:
        test_lead = {
            'company_name': 'Test Company ' + str(datetime.now().timestamp()),
            'contact_first_name': 'Test',
            'contact_last_name': 'User',
            'email': 'test@example.com',
            'phone': '+39 123 456 7890',
            'status': 'New',
            'interest': 'UR'
        }
        
        response = SESSION.post(f"{BASE_URL}/api/leads", json=test_lead)
        
        if response.status_code == 200:
            print("✅ Creazione lead funziona")
            return True
        elif response.status_code == 401:
            print("⚠️  Creazione lead richiede autenticazione")
            return 'auth_required'
        else:
            print(f"❌ Creazione lead fallita: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore test creazione lead: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("\n" + "=" * 60)
    print("🧪 TEST COMPLETO FUNZIONALITÀ CRM")
    print("=" * 60)
    
    from datetime import datetime
    print(f"📅 Data test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    results = {}
    
    # Test login
    results['login'] = test_login()
    
    # Test endpoint API
    results['api'] = test_api_endpoints()
    
    # Test conversione lead
    results['convert'] = test_convert_lead()
    
    # Test sincronizzazione UR
    results['ur_sync'] = test_ur_sync()
    
    # Test creazione lead
    results['create_lead'] = test_create_lead()
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO TEST")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result == True:
            print(f"✅ {test_name}: OK")
        elif result == 'auth_required':
            print(f"⚠️  {test_name}: Richiede autenticazione")
        else:
            print(f"❌ {test_name}: FALLITO")
    
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()


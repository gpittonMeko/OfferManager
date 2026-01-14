#!/usr/bin/env python3
"""
Script di test per verificare il sistema email marketing
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# Dati di login
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

def login():
    """Effettua login e ritorna la sessione"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data=LOGIN_DATA)
    if response.status_code == 200:
        print("✅ Login effettuato con successo")
        return session
    else:
        print(f"❌ Errore login: {response.status_code}")
        return None

def test_create_list(session):
    """Crea una lista di test"""
    print("\n📋 Creazione lista di test...")
    response = session.post(
        f"{BASE_URL}/api/email/lists",
        json={"name": "Test Lista", "description": "Lista per test email"}
    )
    if response.status_code == 200:
        data = response.json()
        list_id = data.get('list_id')
        print(f"✅ Lista creata con ID: {list_id}")
        return list_id
    else:
        print(f"❌ Errore creazione lista: {response.status_code} - {response.text}")
        return None

def test_add_email_to_list(session, list_id, email, name=""):
    """Aggiunge un'email manuale a una lista"""
    print(f"\n📧 Aggiunta email {email} alla lista {list_id}...")
    response = session.post(
        f"{BASE_URL}/api/email/lists/{list_id}/subscribe",
        json={"emails": [{"email": email, "name": name}]}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Email aggiunta: {data}")
        return True
    else:
        print(f"❌ Errore aggiunta email: {response.status_code} - {response.text}")
        return False

def test_get_list_subscribers(session, list_id):
    """Ottiene gli iscritti a una lista"""
    print(f"\n👥 Verifica iscritti lista {list_id}...")
    response = session.get(f"{BASE_URL}/api/email/lists/{list_id}")
    if response.status_code == 200:
        data = response.json()
        subscribers = data.get('list', {}).get('subscribers', [])
        print(f"✅ Iscritti trovati: {len(subscribers)}")
        for sub in subscribers:
            print(f"   - {sub.get('email')} ({sub.get('first_name')} {sub.get('last_name')})")
        return subscribers
    else:
        print(f"❌ Errore lettura lista: {response.status_code} - {response.text}")
        return []

def test_send_email(session, to_email, subject, html_content):
    """Invia email di test"""
    print(f"\n📨 Invio email di test a {to_email}...")
    response = session.post(
        f"{BASE_URL}/api/email/test-send",
        json={
            "to_email": to_email,
            "subject": subject,
            "html_body": html_content
        }
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ Email inviata con successo!")
            print(f"   Message ID: {data.get('message_id', 'N/A')}")
            return True
        else:
            print(f"❌ Errore invio email: {data.get('error')}")
            return False
    else:
        print(f"❌ Errore HTTP: {response.status_code} - {response.text}")
        return False

def main():
    print("🧪 Test Sistema Email Marketing")
    print("=" * 50)
    
    # Login
    session = login()
    if not session:
        sys.exit(1)
    
    # Crea lista
    list_id = test_create_list(session)
    if not list_id:
        sys.exit(1)
    
    # Aggiungi email alla lista
    test_email = "giovanni.pitton@mekosrl.it"
    test_name = "Giovanni Pitton"
    
    if test_add_email_to_list(session, list_id, test_email, test_name):
        # Verifica che sia stata aggiunta
        subscribers = test_get_list_subscribers(session, list_id)
        
        # Invia email di test
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #667eea;">🎉 Email di Test OfferManager</h1>
                <p style="color: #333; line-height: 1.6;">
                    Ciao <strong>Giovanni</strong>,
                </p>
                <p style="color: #333; line-height: 1.6;">
                    Questa è un'email di test dal sistema Email Marketing di OfferManager.
                </p>
                <p style="color: #333; line-height: 1.6;">
                    Se ricevi questa email, significa che:
                </p>
                <ul style="color: #333; line-height: 1.8;">
                    <li>✅ Il sistema Mailgun è configurato correttamente</li>
                    <li>✅ L'aggiunta di contatti alle liste funziona</li>
                    <li>✅ L'invio email funziona</li>
                </ul>
                <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        <strong>OfferManager CRM</strong><br>
                        Sistema Email Marketing
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        test_send_email(
            session,
            test_email,
            "Test Email Marketing - OfferManager",
            html_content
        )
    else:
        print("\n❌ Impossibile aggiungere email alla lista, salto invio email")

if __name__ == "__main__":
    main()








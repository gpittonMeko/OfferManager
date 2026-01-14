#!/usr/bin/env python3
"""
Script per testare e sistemare il sistema email
- Aggiunge giovanni.pitton@mekosrl.it a una lista
- Invia email di test
"""
import os
import sys

# Simula le variabili d'ambiente per il test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mailgun_direct():
    """Test diretto Mailgun"""
    from mailgun_service import MailgunService
    
    print("📧 Test diretto Mailgun...")
    try:
        mailgun = MailgunService()
        print(f"✅ Mailgun inizializzato: dominio={mailgun.domain}")
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                <h1 style="color: #667eea;">🎉 Test Email OfferManager</h1>
                <p>Ciao Giovanni,</p>
                <p>Questa è un'email di test dal sistema Email Marketing di OfferManager.</p>
                <p>Se ricevi questa email, il sistema funziona correttamente!</p>
                <hr>
                <p style="color: #666; font-size: 12px;">OfferManager CRM - Sistema Email Marketing</p>
            </div>
        </body>
        </html>
        """
        
        result = mailgun.send_email(
            to_email="giovanni.pitton@mekosrl.it",
            subject="Test Email Marketing - OfferManager",
            html_content=html_content
        )
        
        if result.get('success'):
            print(f"✅ Email inviata con successo!")
            print(f"   Message ID: {result.get('message_id')}")
            return True
        else:
            print(f"❌ Errore invio: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Test Sistema Email")
    print("=" * 50)
    test_mailgun_direct()








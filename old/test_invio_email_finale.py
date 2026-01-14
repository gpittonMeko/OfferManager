#!/usr/bin/env python3
"""
Script per testare l'invio email finale a giovanni.pitton@mekosrl.it
"""
import os
import sys
import subprocess

def load_env_from_systemd():
    """Carica variabili d'ambiente dal servizio systemd"""
    try:
        result = subprocess.run(
            ["systemctl", "show", "offermanager.service", "--property=Environment"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            env_line = result.stdout.strip()
            if env_line.startswith("Environment="):
                env_vars = env_line.replace("Environment=", "")
                for var in env_vars.split():
                    if "=" in var:
                        key, value = var.split("=", 1)
                        os.environ[key] = value.strip('"')
                return True
    except Exception as e:
        print(f"⚠️  Impossibile caricare env da systemd: {e}")
    return False

def main():
    print("📧 Test Invio Email Finale")
    print("=" * 50)
    
    # Carica variabili d'ambiente
    print("\n🔧 Caricamento configurazione...")
    if load_env_from_systemd():
        print("✅ Variabili caricate da systemd")
    else:
        print("⚠️  Usando variabili d'ambiente esistenti")
    
    # Verifica configurazione
    api_key = os.environ.get('MAILGUN_API_KEY', '')
    domain = os.environ.get('MAILGUN_DOMAIN', '')
    region = os.environ.get('MAILGUN_API_REGION', 'eu')
    
    if not api_key:
        print("❌ MAILGUN_API_KEY non trovato")
        return False
    
    if not domain:
        print("❌ MAILGUN_DOMAIN non trovato")
        return False
    
    print(f"✅ API Key: {api_key[:15]}...")
    print(f"✅ Domain: {domain}")
    print(f"✅ Region: {region}")
    
    # Test invio email
    print("\n📨 Invio email di test a giovanni.pitton@mekosrl.it...")
    
    try:
        sys.path.insert(0, '/home/ubuntu/offermanager')
        from mailgun_service import MailgunService
        
        mailgun = MailgunService()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; padding: 0; margin: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 30px auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #667eea; margin-top: 0;">🎉 Email di Test OfferManager</h1>
                <p style="color: #333; line-height: 1.6; font-size: 16px;">
                    Ciao <strong>Giovanni</strong>,
                </p>
                <p style="color: #333; line-height: 1.6; font-size: 16px;">
                    Questa è un'email di test dal sistema Email Marketing di <strong>OfferManager CRM</strong>.
                </p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #333; font-size: 16px; font-weight: bold;">
                        Se ricevi questa email, significa che:
                    </p>
                    <ul style="color: #333; line-height: 1.8; font-size: 15px; margin-top: 10px;">
                        <li>✅ Il sistema Mailgun è configurato correttamente</li>
                        <li>✅ I record DNS sono stati verificati</li>
                        <li>✅ L'invio email funziona perfettamente</li>
                        <li>✅ Il sistema Email Marketing è operativo</li>
                    </ul>
                </div>
                <p style="color: #333; line-height: 1.6; font-size: 16px;">
                    Ora puoi utilizzare il sistema Email Marketing di OfferManager per:
                </p>
                <ul style="color: #333; line-height: 1.8; font-size: 15px;">
                    <li>📧 Creare e gestire liste contatti</li>
                    <li>📝 Comporre email personalizzate</li>
                    <li>🚀 Inviare campagne email</li>
                    <li>📊 Tracciare aperture e click</li>
                </ul>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px; margin: 0;">
                    <strong>OfferManager CRM</strong><br>
                    Sistema Email Marketing<br>
                    <a href="http://crm.infomekosrl.it:8000" style="color: #667eea;">crm.infomekosrl.it:8000</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        result = mailgun.send_email(
            to_email="giovanni.pitton@mekosrl.it",
            subject="✅ Test Email Marketing - OfferManager CRM",
            html_content=html_content
        )
        
        if result.get('success'):
            print(f"\n✅ Email inviata con successo!")
            print(f"   Destinatario: giovanni.pitton@mekosrl.it")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
            print(f"   Messaggio: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"\n❌ Errore invio email:")
            print(f"   {result.get('error', 'Errore sconosciuto')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)








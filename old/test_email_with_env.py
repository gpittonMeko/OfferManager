#!/usr/bin/env python3
"""
Script per testare invio email caricando le variabili d'ambiente dal sistema
"""
import os
import subprocess
import sys

def load_env_from_systemd():
    """Carica le variabili d'ambiente dal servizio systemd"""
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
                # Parse formato "KEY1=value1 KEY2=value2"
                for var in env_vars.split():
                    if "=" in var:
                        key, value = var.split("=", 1)
                        os.environ[key] = value.strip('"')
                return True
    except Exception as e:
        print(f"⚠️  Impossibile caricare env da systemd: {e}")
    
    return False

def load_env_from_file():
    """Prova a caricare da file .env"""
    env_file = "/home/ubuntu/offermanager/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        return True
    return False

def main():
    print("🔧 Caricamento variabili d'ambiente...")
    
    # Prova a caricare da systemd
    if load_env_from_systemd():
        print("✅ Variabili caricate da systemd")
    
    # Prova a caricare da file .env
    if load_env_from_file():
        print("✅ Variabili caricate da .env")
    
    # Mostra le variabili (senza valori sensibili)
    mailgun_key = os.environ.get('MAILGUN_API_KEY', '')
    mailgun_domain = os.environ.get('MAILGUN_DOMAIN', '')
    
    if mailgun_key:
        print(f"✅ MAILGUN_API_KEY configurato: {mailgun_key[:10]}...")
    else:
        print("❌ MAILGUN_API_KEY non trovato")
        
    if mailgun_domain:
        print(f"✅ MAILGUN_DOMAIN configurato: {mailgun_domain}")
    else:
        print("❌ MAILGUN_DOMAIN non trovato")
    
    if not mailgun_key or not mailgun_domain:
        print("\n⚠️  Impossibile continuare senza configurazione Mailgun")
        return
    
    # Ora testa l'invio
    print("\n📧 Test invio email...")
    try:
        from mailgun_service import MailgunService
        
        mailgun = MailgunService()
        
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
                    Se ricevi questa email, significa che tutto funziona correttamente! ✅
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    <strong>OfferManager CRM</strong><br>
                    Sistema Email Marketing
                </p>
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
            print(f"✅ Email inviata con successo a giovanni.pitton@mekosrl.it!")
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Errore invio: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()








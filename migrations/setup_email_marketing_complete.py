#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo per inizializzare Email Marketing
"""
import os
import sys
from pathlib import Path

# Carica variabili d'ambiente da file .env se esiste
def load_env_file():
    """Carica variabili d'ambiente da file .env"""
    env_file = Path('.env')
    if env_file.exists():
        try:
            # Prova con python-dotenv se disponibile
            try:
                from dotenv import load_dotenv
                load_dotenv()
                return
            except ImportError:
                pass
            
            # Fallback: leggi manualmente il file .env
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Errore caricamento .env: {e}")

load_env_file()

# Imposta variabili d'ambiente Mailgun (da file .env o variabili d'ambiente)
# IMPORTANTE: Le chiavi API sono nel file .env locale (non committato)
# Se non trovi le variabili, usa i valori di default o fallback
if 'MAILGUN_API_KEY' not in os.environ or os.environ.get('MAILGUN_API_KEY') == 'YOUR_MAILGUN_API_KEY_HERE':
    # Se non è stato caricato dal .env, usa il valore di default
    pass  # Lascia che il codice gestisca il fallback

# Importa dopo aver settato le env
from crm_app_completo import db, app, EmailTemplate, User
from email_template_loader import get_default_templates, create_sample_content

def setup_email_marketing():
    """Inizializza completamente il sistema Email Marketing"""
    print("=" * 60)
    print("  SETUP EMAIL MARKETING COMPLETO")
    print("=" * 60)
    print()
    
    with app.app_context():
        # 1. Crea tabelle database
        print("1. Creazione tabelle database...")
        try:
            db.create_all()
            print("   ✅ Tabelle database create/verificate")
        except Exception as e:
            print(f"   ⚠️  Errore creazione tabelle: {e}")
        
        print()
        
        # 2. Trova utente admin o crea uno default
        print("2. Verifica utenti...")
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            # Prova a trovare il primo utente
            admin_user = User.query.first()
        
        if not admin_user:
            print("   ⚠️  Nessun utente trovato. I template verranno creati senza owner.")
            user_id = 1
        else:
            user_id = admin_user.id
            print(f"   ✅ Utente trovato: {admin_user.username} (ID: {user_id})")
        
        print()
        
        # 3. Carica template predefiniti
        print("3. Caricamento template predefiniti...")
        templates = get_default_templates()
        sample_content = create_sample_content()
        
        created_count = 0
        for key, template_data in templates.items():
            # Verifica se esiste già
            existing = EmailTemplate.query.filter_by(name=template_data['name']).first()
            if existing:
                print(f"   ⏭️  Template '{template_data['name']}' già esistente")
                continue
            
            # Sostituisci placeholder content
            html_content = template_data['html_content']
            if key in sample_content:
                html_content = html_content.replace('{{content}}', sample_content[key])
            
            try:
                template = EmailTemplate(
                    name=template_data['name'],
                    subject=template_data['subject'],
                    html_content=html_content,
                    category=template_data['category'],
                    owner_id=user_id
                )
                db.session.add(template)
                created_count += 1
                print(f"   ✅ Creato template: {template_data['name']}")
            except Exception as e:
                print(f"   ❌ Errore creazione template {template_data['name']}: {e}")
        
        # Commit
        try:
            db.session.commit()
            print(f"   ✅ Totale template creati: {created_count}")
        except Exception as e:
            print(f"   ❌ Errore commit: {e}")
            db.session.rollback()
        
        print()
        
        # 4. Test Mailgun Service
        print("4. Test configurazione Mailgun...")
        try:
            from mailgun_service import MailgunService
            mailgun = MailgunService()
            print("   ✅ MailgunService inizializzato correttamente")
            print(f"   📧 Dominio: {mailgun.domain}")
            print(f"   📤 From: {mailgun.from_name} <{mailgun.from_email}>")
        except Exception as e:
            print(f"   ❌ Errore Mailgun: {e}")
        
        print()
        
        # 5. Riepilogo finale
        print("=" * 60)
        print("  ✅ SETUP COMPLETATO!")
        print("=" * 60)
        print()
        print("Template disponibili:")
        all_templates = EmailTemplate.query.filter_by(is_active=True).all()
        for t in all_templates:
            print(f"  - {t.name} ({t.category})")
        print()
        print("Prossimi passi:")
        print("  1. Accedi al CRM: http://13.53.183.146:8000")
        print("  2. Vai su '📧 Email Marketing' nel menu")
        print("  3. Crea la tua prima lista email")
        print("  4. Crea e invia la tua prima campagna!")
        print()

if __name__ == '__main__':
    setup_email_marketing()








#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo per inizializzare Email Marketing
"""
import os
import sys

# Imposta variabili d'ambiente Mailgun (da file .env o variabili d'ambiente)
# IMPORTANTE: Non committare chiavi API nel repository!
# Usa variabili d'ambiente o un file .env (non tracciato da git)
if 'MAILGUN_API_KEY' not in os.environ:
    os.environ['MAILGUN_API_KEY'] = os.getenv('MAILGUN_API_KEY', 'YOUR_MAILGUN_API_KEY_HERE')
if 'MAILGUN_DOMAIN' not in os.environ:
    os.environ['MAILGUN_DOMAIN'] = os.getenv('MAILGUN_DOMAIN', 'infomekosrl.it')
if 'MAILGUN_FROM_EMAIL' not in os.environ:
    os.environ['MAILGUN_FROM_EMAIL'] = os.getenv('MAILGUN_FROM_EMAIL', 'noreply@infomekosrl.it')
if 'MAILGUN_FROM_NAME' not in os.environ:
    os.environ['MAILGUN_FROM_NAME'] = os.getenv('MAILGUN_FROM_NAME', 'ME.KO. Srl')
if 'MAILGUN_API_REGION' not in os.environ:
    os.environ['MAILGUN_API_REGION'] = os.getenv('MAILGUN_API_REGION', 'eu')

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








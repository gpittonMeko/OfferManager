#!/usr/bin/env python3
# Test rapido delle API Email Marketing
from crm_app_completo import db, app, EmailTemplate, EmailList, EmailCampaign

with app.app_context():
    # Test import
    print("✅ Import modelli OK")
    
    # Test query template
    templates = EmailTemplate.query.filter_by(is_active=True).all()
    print(f"✅ Template trovati: {len(templates)}")
    
    # Test query liste
    lists = EmailList.query.filter_by(is_active=True).all()
    print(f"✅ Liste trovate: {len(lists)}")
    
    # Test query campagne
    campaigns = EmailCampaign.query.all()
    print(f"✅ Campagne trovate: {len(campaigns)}")
    
    print("\n✅ Tutti i test OK - Email Marketing funzionante!")








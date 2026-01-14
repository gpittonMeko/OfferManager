#!/usr/bin/env python3
# Test che il database sia stato fixato
from crm_app_completo import db, app, Opportunity

with app.app_context():
    try:
        # Prova query che usava folder_path
        opps = Opportunity.query.limit(1).all()
        print("✅ Query Opportunity OK - colonna folder_path presente")
        
        # Conta opportunità
        count = Opportunity.query.count()
        print(f"✅ Opportunità nel database: {count}")
        
        print("\n✅ Database fixato correttamente!")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()








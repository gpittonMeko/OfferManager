#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rimuove account test dal database"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, Account, Opportunity, Lead

if __name__ == '__main__':
    with app.app_context():
        # Cerca account test
        test_patterns = ['test', 'Test', 'TEST', 'demo', 'Demo', 'DEMO', 'Cliente Test', 'Cliente Sconosciuto', 'Unknown Company']
        
        accounts_to_delete = []
        for account in Account.query.all():
            if any(pattern in account.name for pattern in test_patterns):
                accounts_to_delete.append(account)
                print(f"🗑️  Account da eliminare: {account.name} (ID: {account.id})")
        
        if accounts_to_delete:
            # Conta opportunità e leads collegati
            total_opps = 0
            total_leads = 0
            for acc in accounts_to_delete:
                opps = Opportunity.query.filter_by(account_id=acc.id).count()
                leads = Lead.query.filter_by(converted_account_id=acc.id).count()
                total_opps += opps
                total_leads += leads
                if opps > 0 or leads > 0:
                    print(f"   ⚠️  Ha {opps} opportunità e {leads} leads collegati")
            
            confirm = input(f"\n⚠️  Eliminare {len(accounts_to_delete)} account test? (s/n): ")
            if confirm.lower() == 's':
                for account in accounts_to_delete:
                    # Elimina opportunità collegate
                    Opportunity.query.filter_by(account_id=account.id).delete()
                    # Elimina leads collegati
                    Lead.query.filter_by(converted_account_id=account.id).update({'converted_account_id': None})
                    # Elimina account
                    db.session.delete(account)
                db.session.commit()
                print(f"✅ Eliminati {len(accounts_to_delete)} account test")
            else:
                print("❌ Operazione annullata")
        else:
            print("✅ Nessun account test trovato")





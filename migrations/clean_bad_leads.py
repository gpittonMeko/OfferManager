#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pulisce leads problematici dal database"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, Lead

if __name__ == '__main__':
    with app.app_context():
        leads = Lead.query.all()
        print(f"📊 Totale leads nel database: {len(leads)}")
        
        to_delete = []
        for lead in leads:
            should_delete = False
            reason = []
            
            if lead.company_name:
                # Controlla pattern problematici
                company_lower = lead.company_name.lower()
                # Pattern specifico: "Nome - Locked Account Engagement Comments: Item ..."
                if 'locked account engagement comments' in company_lower or 'engagement comments' in company_lower:
                    should_delete = True
                    reason.append("Company name contiene 'Locked Account Engagement Comments'")
                elif any(bad in company_lower for bad in ['locked partner', 'edit lead status', 'sql edit', 'locked account']):
                    should_delete = True
                    reason.append("Company name contiene testo di sistema")
                elif 'item' in company_lower and ('locked' in company_lower or 'edit' in company_lower):
                    should_delete = True
                    reason.append("Company name contiene pattern Locked/Edit + Item")
                elif company_lower.strip() in ['item', 'null', 'locked'] or len(lead.company_name.strip()) < 3:
                    should_delete = True
                    reason.append("Company name invalido o troppo corto")
            
            if lead.contact_first_name and 'SQL Edit' in lead.contact_first_name:
                should_delete = True
                reason.append("Nome contiene testo di sistema")
            
            if should_delete:
                to_delete.append((lead, reason))
                print(f"🗑️  Lead ID {lead.id} da eliminare: {lead.company_name}")
                print(f"   Motivo: {', '.join(reason)}")
        
        if to_delete:
            confirm = input(f"\n⚠️  Eliminare {len(to_delete)} leads problematici? (s/n): ")
            if confirm.lower() == 's':
                for lead, _ in to_delete:
                    db.session.delete(lead)
                db.session.commit()
                print(f"✅ Eliminati {len(to_delete)} leads problematici")
            else:
                print("❌ Operazione annullata")
        else:
            print("✅ Nessun lead problematico trovato")

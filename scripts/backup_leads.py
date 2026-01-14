#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per fare backup dei leads esistenti prima dell'importazione
"""
import sys
import os
import csv
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead

def backup_leads():
    """Crea un backup CSV di tutti i leads esistenti"""
    with app.app_context():
        print("=" * 60)
        print("BACKUP LEADS ESISTENTI")
        print("=" * 60)
        
        # Crea directory backup se non esiste
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nome file backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"leads_backup_{timestamp}.csv")
        
        # Recupera tutti i leads
        leads = Lead.query.all()
        
        print(f"📦 Trovati {len(leads)} leads da salvare...")
        
        # Scrive il CSV
        with open(backup_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'company_name', 'contact_first_name', 'contact_last_name',
                'email', 'phone', 'address', 'industry', 'interest', 'source',
                'rating', 'status', 'notes', 'owner_id', 'created_at', 'updated_at'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in leads:
                writer.writerow({
                    'id': lead.id,
                    'company_name': lead.company_name or '',
                    'contact_first_name': lead.contact_first_name or '',
                    'contact_last_name': lead.contact_last_name or '',
                    'email': lead.email or '',
                    'phone': lead.phone or '',
                    'address': lead.address or '',
                    'industry': lead.industry or '',
                    'interest': lead.interest or '',
                    'source': lead.source or '',
                    'rating': lead.rating or '',
                    'status': lead.status or '',
                    'notes': lead.notes or '',
                    'owner_id': lead.owner_id,
                    'created_at': lead.created_at.isoformat() if lead.created_at else '',
                    'updated_at': lead.updated_at.isoformat() if lead.updated_at else ''
                })
        
        print(f"✅ Backup completato: {backup_file}")
        print(f"   Totale leads salvati: {len(leads)}")
        print("=" * 60)
        
        return backup_file

if __name__ == "__main__":
    backup_leads()

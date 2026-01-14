#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rimuove account duplicato - filippo e mariuzzo sono la stessa persona"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, User, app

with app.app_context():
    # Rimuovi mariuzzo (mantieni filippo)
    mariuzzo = User.query.filter_by(username='mariuzzo').first()
    if mariuzzo:
        print(f"🗑️  Rimozione account duplicato: mariuzzo")
        # Trasferisci eventuali dati a filippo se necessario
        filippo = User.query.filter_by(username='filippo').first()
        if filippo:
            # Aggiorna filippo con i dati completi
            filippo.first_name = 'Filippo'
            filippo.last_name = 'Mariuzzo'  # Nome completo
            filippo.email = 'filippo.mariuzzo@mekosrl.it'
            print(f"✅ Aggiornato filippo con nome completo: Filippo Mariuzzo")
        
        db.session.delete(mariuzzo)
        db.session.commit()
        print(f"✅ Account mariuzzo rimosso")
    else:
        print("⚠️  Account mariuzzo non trovato")
    
    print("\n" + "=" * 60)
    print("UTENTI FINALI")
    print("=" * 60)
    for u in User.query.order_by(User.username).all():
        print(f"  - {u.username} ({u.first_name} {u.last_name})")





#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge immagini fittizie agli account"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app, Account

with app.app_context():
    accounts = Account.query.filter((Account.image_url == None) | (Account.image_url == '')).all()
    updated = 0
    
    for account in accounts:
        # Genera immagine fittizia basata sul nome
        account.image_url = f"https://ui-avatars.com/api/?name={account.name.replace(' ', '+')}&size=128&background=667eea&color=fff"
        updated += 1
    
    db.session.commit()
    print(f"✅ Aggiornati {updated} account con immagini fittizie")





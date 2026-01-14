#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica le liste Vox Mail create"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, EmailList, EmailListSubscription

with app.app_context():
    liste = EmailList.query.filter(EmailList.name.like('Vox Mail - %')).all()
    print(f"📋 Trovate {len(liste)} liste Vox Mail\n")
    
    for lista in liste:
        count = EmailListSubscription.query.filter_by(
            list_id=lista.id,
            status='subscribed'
        ).count()
        print(f"  - {lista.name}: {count} iscritti")

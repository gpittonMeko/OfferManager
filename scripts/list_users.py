#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista tutti gli utenti"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import User, db, app

with app.app_context():
    users = User.query.all()
    print("=" * 60)
    print("UTENTI NEL DATABASE")
    print("=" * 60)
    for u in users:
        print(f"  - {u.username} ({u.first_name} {u.last_name}) - {u.email} - {u.role}")
    print("=" * 60)
    print(f"Totale: {len(users)} utenti")





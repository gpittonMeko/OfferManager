#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna database con nuovo modello OpportunityChatter"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app

with app.app_context():
    db.create_all()
    print("✅ Database aggiornato con modello OpportunityChatter")





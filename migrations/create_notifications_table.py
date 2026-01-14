#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea la tabella notifications nel database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db

def create_notifications_table():
    with app.app_context():
        db.create_all()
        print("✅ Tabella notifications creata/verificata")

if __name__ == "__main__":
    create_notifications_table()

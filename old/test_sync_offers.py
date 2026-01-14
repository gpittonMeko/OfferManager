#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test sync offerte"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db
from sync_offers_from_folder import sync_offers

if __name__ == '__main__':
    with app.app_context():
        print("🧪 Test sync offerte...")
        try:
            sync_offers()
            print("✅ Test completato")
        except Exception as e:
            print(f"❌ Errore: {e}")
            import traceback
            traceback.print_exc()





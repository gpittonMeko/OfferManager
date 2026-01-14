#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica quale database contiene le tabelle corrette"""
import sqlite3
import os

databases = ['crm.db', 'mekocrm.db', 'crm_completo.db', 'offer_manager_crm.db']

for db_file in databases:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            conn.close()
            
            has_users = 'users' in tables
            has_opportunities = 'opportunities' in tables
            has_leads = 'leads' in tables
            
            print(f"\n📁 {db_file} ({os.path.getsize(db_file)} bytes):")
            print(f"   Tabelle: {len(tables)}")
            if has_users and has_opportunities and has_leads:
                print(f"   ✅ COMPLETO - Contiene users, opportunities, leads")
                print(f"   Tabelle: {', '.join(tables[:10])}...")
            else:
                print(f"   ❌ Incompleto")
                print(f"   users: {has_users}, opportunities: {has_opportunities}, leads: {has_leads}")
        except Exception as e:
            print(f"\n❌ {db_file}: Errore - {e}")

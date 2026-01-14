#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica struttura database"""
import sqlite3

db_file = 'crm.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"\n📁 Struttura tabella users in {db_file}:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"   {col[1]} ({col[2]})")

conn.close()

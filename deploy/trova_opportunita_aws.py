#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trova opportunità per nome"""
import sqlite3
from pathlib import Path

db_file = Path('/home/ubuntu/offermanager/instance/mekocrm.db')
if not db_file.exists():
    db_file = Path('/home/ubuntu/offermanager/mekocrm.db')

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Cerca tutte le opportunità che contengono le parole chiave
keywords = ['Eurofresi', 'Eurovo', 'Multimac', 'ITV', 'Scuola Camerana', 'Politecnico']
for keyword in keywords:
    cursor.execute("SELECT id, name FROM opportunities WHERE name LIKE ?", (f'%{keyword}%',))
    results = cursor.fetchall()
    if results:
        print(f"\n{keyword}:")
        for r in results:
            print(f"  ID {r[0]}: {r[1]}")

conn.close()

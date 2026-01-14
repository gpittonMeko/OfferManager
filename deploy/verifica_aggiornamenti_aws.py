#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica aggiornamenti opportunità"""
import sqlite3
from pathlib import Path

db_file = Path('/home/ubuntu/offermanager/instance/mekocrm.db')
if not db_file.exists():
    db_file = Path('/home/ubuntu/offermanager/mekocrm.db')

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

print("=" * 80)
print("VERIFICA AGGIORNAMENTI")
print("=" * 80)
print()

# Cerca Eurofresi
print("1. Opportunità con 'Euro' nel nome:")
cursor.execute("SELECT id, name, heat_level FROM opportunities WHERE name LIKE '%Euro%'")
euro = cursor.fetchall()
for r in euro:
    print(f"   ID {r[0]}: {r[1][:60]}... -> {r[2]}")

print()
print("2. Opportunità Multimac e Scuola Camerana:")
cursor.execute("SELECT id, name, heat_level FROM opportunities WHERE name LIKE '%Multimac%' OR name LIKE '%Scuola Camerana%'")
multimac = cursor.fetchall()
for r in multimac:
    print(f"   ID {r[0]}: {r[1][:60]}... -> {r[2]}")

print()
print("3. Attività per Eurovo (ID 567):")
cursor.execute("SELECT id, opportunity_id, task_type, description, assigned_to_id FROM opportunity_tasks WHERE opportunity_id = 567")
tasks = cursor.fetchall()
if tasks:
    for t in tasks:
        print(f"   Task ID {t[0]}: type={t[2]}, assigned_to={t[4]}, desc={t[3][:50]}")
else:
    print("   Nessuna attività trovata")

conn.close()

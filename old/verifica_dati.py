#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica che tutti i dati esistano ancora"""
import sqlite3
import os

print("=" * 60)
print("VERIFICA DATI NEL DATABASE")
print("=" * 60)

# Flask cerca automaticamente in instance/ quando si usa sqlite:///mekocrm.db
db_file = 'instance/mekocrm.db'
if not os.path.exists(db_file):
    print(f"❌ Database {db_file} NON ESISTE!")
    exit(1)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Verifica tabelle
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print(f"\n📋 Tabelle presenti: {len(tables)}")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   ✅ {table}: {count} record")

# Verifica opportunità
print("\n📊 OPPORTUNITÀ:")
cursor.execute("SELECT id, name, stage, amount FROM opportunities LIMIT 10")
opps = cursor.fetchall()
if opps:
    print(f"   ✅ Trovate {len(opps)} opportunità (prime 10):")
    for opp in opps:
        print(f"      - ID {opp[0]}: {opp[1]} ({opp[2]}) - €{opp[3]}")
else:
    print("   ❌ NESSUNA OPPORTUNITÀ TROVATA!")

# Verifica prodotti/listini
print("\n📦 PRODOTTI/LISTINI:")
cursor.execute("SELECT COUNT(*) FROM products")
prod_count = cursor.fetchone()[0]
print(f"   ✅ Prodotti: {prod_count}")

cursor.execute("SELECT COUNT(*) FROM offers")
offers_count = cursor.fetchone()[0]
print(f"   ✅ Offerte: {offers_count}")

# Verifica utenti
print("\n👥 UTENTI:")
cursor.execute("SELECT id, username, email FROM users")
users = cursor.fetchall()
if users:
    print(f"   ✅ Trovati {len(users)} utenti:")
    for user in users:
        print(f"      - {user[1]} ({user[2]})")
else:
    print("   ❌ NESSUN UTENTE TROVATO!")

# Verifica accounts
print("\n🏢 ACCOUNTS:")
cursor.execute("SELECT COUNT(*) FROM accounts")
acc_count = cursor.fetchone()[0]
print(f"   ✅ Accounts: {acc_count}")

# Verifica leads
print("\n📞 LEADS:")
cursor.execute("SELECT COUNT(*) FROM leads")
leads_count = cursor.fetchone()[0]
print(f"   ✅ Leads: {leads_count}")

conn.close()

print("\n" + "=" * 60)
print("VERIFICA COMPLETATA")
print("=" * 60)

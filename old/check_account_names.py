#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlla i nomi degli account per trovare nomi malformati o con caratteri strani
"""
import sys
import os
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, Account

def check_account_names():
    """Controlla i nomi degli account per problemi"""
    with app.app_context():
        accounts = Account.query.all()
        
        print("=" * 80)
        print("CONTROLLO NOMI ACCOUNT")
        print("=" * 80)
        print()
        
        problems = []
        good_names = []
        
        for account in accounts:
            name = account.name
            issues = []
            
            # Controlla caratteri strani o non validi
            if re.search(r'[^\w\s\-\.\,\'\(\)]', name):
                issues.append("Contiene caratteri speciali non standard")
            
            # Controlla spazi multipli
            if '  ' in name:
                issues.append("Contiene spazi multipli")
            
            # Controlla spazi all'inizio/fine
            if name != name.strip():
                issues.append("Ha spazi all'inizio o alla fine")
            
            # Controlla nomi troppo corti
            if len(name.strip()) < 2:
                issues.append("Nome troppo corto")
            
            # Controlla nomi con solo numeri
            if name.strip().isdigit():
                issues.append("Contiene solo numeri")
            
            # Controlla nomi vuoti o solo spazi
            if not name or not name.strip():
                issues.append("Nome vuoto o solo spazi")
            
            if issues:
                problems.append({
                    'id': account.id,
                    'name': name,
                    'issues': issues
                })
            else:
                good_names.append(account.id)
        
        print(f"📊 Totale account: {len(accounts)}")
        print(f"✅ Nomi corretti: {len(good_names)}")
        print(f"⚠️  Nomi con problemi: {len(problems)}")
        print()
        
        if problems:
            print("=" * 80)
            print("ACCOUNT CON PROBLEMI")
            print("=" * 80)
            print()
            for p in problems[:20]:  # Mostra i primi 20
                print(f"ID: {p['id']}")
                print(f"  Nome: '{p['name']}'")
                print(f"  Problemi: {', '.join(p['issues'])}")
                print()
            if len(problems) > 20:
                print(f"... e altri {len(problems) - 20} account con problemi")
            print()
            
            # Suggerimenti per correzione
            print("=" * 80)
            print("SUGGERIMENTI")
            print("=" * 80)
            print("1. Rimuovi caratteri speciali non standard")
            print("2. Normalizza gli spazi (rimuovi spazi multipli)")
            print("3. Rimuovi spazi all'inizio e alla fine")
            print("4. Verifica che i nomi siano significativi")
            print()
        else:
            print("✅ Tutti i nomi degli account sono corretti!")
        
        return problems

if __name__ == '__main__':
    try:
        problems = check_account_names()
        if problems:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

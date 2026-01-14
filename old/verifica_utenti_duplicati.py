#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare utenti duplicati nel database
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db, User, Opportunity

def verifica_utenti_duplicati():
    """Verifica utenti duplicati"""
    with app.app_context():
        print("=" * 80)
        print("VERIFICA UTENTI DUPLICATI")
        print("=" * 80)
        print()
        
        # Ottieni tutti gli utenti
        all_users = User.query.all()
        
        print(f"📊 Totale utenti nel database: {len(all_users)}")
        print()
        
        # Raggruppa per username
        users_by_username = {}
        for user in all_users:
            username = user.username.lower()
            if username not in users_by_username:
                users_by_username[username] = []
            users_by_username[username].append(user)
        
        # Trova duplicati
        duplicates_found = False
        for username, users in users_by_username.items():
            if len(users) > 1:
                duplicates_found = True
                print(f"⚠️  DUPLICATO trovato per username '{username}':")
                for user in users:
                    print(f"   - ID: {user.id}, Username: {user.username}, Nome: {user.first_name} {user.last_name}, Email: {user.email}, Role: {user.role}")
                print()
        
        # Raggruppa per email
        users_by_email = {}
        for user in all_users:
            if user.email:
                email = user.email.lower()
                if email not in users_by_email:
                    users_by_email[email] = []
                users_by_email[email].append(user)
        
        # Trova duplicati per email
        for email, users in users_by_email.items():
            if len(users) > 1:
                duplicates_found = True
                print(f"⚠️  DUPLICATO trovato per email '{email}':")
                for user in users:
                    print(f"   - ID: {user.id}, Username: {user.username}, Nome: {user.first_name} {user.last_name}, Email: {user.email}, Role: {user.role}")
                print()
        
        # Verifica opportunità per vedere se ci sono riferimenti a utenti duplicati
        print("=" * 80)
        print("VERIFICA OPPORTUNITÀ PER UTENTI")
        print("=" * 80)
        print()
        
        all_opps = Opportunity.query.all()
        opps_by_owner = {}
        for opp in all_opps:
            if opp.owner_id:
                if opp.owner_id not in opps_by_owner:
                    opps_by_owner[opp.owner_id] = []
                opps_by_owner[opp.owner_id].append(opp)
        
        # Mostra statistiche per ogni utente
        for user in all_users:
            opp_count = len(opps_by_owner.get(user.id, []))
            if opp_count > 0:
                print(f"👤 {user.username} ({user.first_name} {user.last_name}): {opp_count} opportunità")
        
        if not duplicates_found:
            print("\n✅ Nessun duplicato trovato!")
        else:
            print("\n❌ Duplicati trovati! È necessario pulire il database.")
        
        return duplicates_found

if __name__ == '__main__':
    try:
        verifica_utenti_duplicati()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

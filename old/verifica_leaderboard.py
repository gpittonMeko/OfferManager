#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare la leaderboard e vedere se ci sono duplicati nella visualizzazione
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db, User, Opportunity

def verifica_leaderboard():
    """Verifica la leaderboard come viene calcolata"""
    with app.app_context():
        print("=" * 80)
        print("VERIFICA LEADERBOARD")
        print("=" * 80)
        print()
        
        # Replica la logica della dashboard
        commercial_users = User.query.filter_by(role='commerciale').all()
        print(f"📊 Utenti commerciali trovati: {len(commercial_users)}")
        print()
        
        # Rimuovi duplicati per username (mantieni solo il primo)
        seen_usernames = set()
        unique_users = []
        for user in commercial_users:
            print(f"   - ID: {user.id}, Username: '{user.username}', Nome: '{user.first_name} {user.last_name}', Email: {user.email}")
            if user.username.lower() not in seen_usernames:
                seen_usernames.add(user.username.lower())
                unique_users.append(user)
            else:
                print(f"      ⚠️  DUPLICATO per username '{user.username.lower()}' - SALTATO")
        
        print()
        print(f"✅ Utenti unici dopo rimozione duplicati: {len(unique_users)}")
        print()
        
        # Calcola leaderboard
        leaderboard = []
        for user in unique_users:
            user_opps = Opportunity.query.filter_by(owner_id=user.id).all()
            
            # Calcola pipeline
            user_pipeline = 0.0
            for opp in user_opps:
                if opp.stage not in ['Closed Won', 'Closed Lost']:
                    if opp.amount and opp.amount > 0:
                        user_pipeline += opp.amount
            
            # Calcola chiusi
            user_closed_won = 0.0
            for opp in user_opps:
                if opp.stage == 'Closed Won':
                    if opp.amount and opp.amount > 0:
                        user_closed_won += opp.amount
            
            user_closed_count = len([o for o in user_opps if o.stage == 'Closed Won'])
            user_opps_count = len(user_opps)
            
            name = f"{user.first_name} {user.last_name}".strip()
            
            leaderboard.append({
                'user_id': user.id,
                'username': user.username,
                'name': name,
                'opportunities': user_opps_count,
                'pipeline': user_pipeline,
                'closed_won': user_closed_won,
                'closed_count': user_closed_count
            })
        
        # Ordina per pipeline
        leaderboard.sort(key=lambda x: x['pipeline'], reverse=True)
        
        print("=" * 80)
        print("LEADERBOARD CALCOLATA")
        print("=" * 80)
        print()
        
        # Verifica duplicati per nome
        names_seen = {}
        for entry in leaderboard:
            name = entry['name']
            if name in names_seen:
                names_seen[name].append(entry)
            else:
                names_seen[name] = [entry]
        
        duplicates_found = False
        for name, entries in names_seen.items():
            if len(entries) > 1:
                duplicates_found = True
                print(f"⚠️  DUPLICATO nella leaderboard per nome '{name}':")
                for entry in entries:
                    print(f"   - ID: {entry['user_id']}, Username: {entry['username']}, Pipeline: €{entry['pipeline']:.2f}")
                print()
        
        if not duplicates_found:
            print("✅ Nessun duplicato nella leaderboard!")
            print()
            print("Leaderboard completa:")
            for i, entry in enumerate(leaderboard[:10], 1):
                print(f"{i}. {entry['name']} ({entry['username']}) - Pipeline: €{entry['pipeline']:.2f}, Opp: {entry['opportunities']}")
        
        return duplicates_found

if __name__ == '__main__':
    try:
        verifica_leaderboard()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

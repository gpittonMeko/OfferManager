#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per rimuovere utenti duplicati mantenendo solo quello principale
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db, User, Opportunity, Ticket, TicketComment, Notification, OpportunityTask

def rimuovi_utenti_duplicati():
    """Rimuove utenti duplicati mantenendo quello principale"""
    with app.app_context():
        print("=" * 80)
        print("RIMOZIONE UTENTI DUPLICATI")
        print("=" * 80)
        print()
        
        commercial_users = User.query.filter_by(role='commerciale').all()
        
        # Raggruppa per nome completo (first_name + last_name)
        users_by_key = {}
        for user in commercial_users:
            # Usa nome completo come chiave principale
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip().lower()
            if not full_name or full_name == ' ':
                # Se non c'è nome, usa username
                key = user.username.lower()
            else:
                key = full_name
            
            if key not in users_by_key:
                users_by_key[key] = []
            users_by_key[key].append(user)
        
        # Trova duplicati e mantieni solo quello principale
        users_to_delete = []
        users_to_keep = {}
        
        for key, users in users_by_key.items():
            if len(users) > 1:
                print(f"⚠️  Duplicati trovati per '{key}':")
                
                # Trova quello principale (più opportunità o username più corto/principale)
                best_user = None
                max_opps = -1
                
                # Username principali da preferire
                preferred_usernames = ['filippo', 'giovanni', 'sandy', 'luca', 'mattia']
                
                for user in users:
                    opp_count = Opportunity.query.filter_by(owner_id=user.id).count()
                    print(f"   - ID: {user.id}, Username: {user.username}, Opp: {opp_count}")
                    
                    # Calcola score: più opportunità = meglio, username preferito = meglio
                    score = opp_count * 1000
                    if user.username.lower() in preferred_usernames:
                        score += 100
                    if len(user.username) <= 8:  # Username corti sono preferiti
                        score += 50
                    
                    if not best_user or score > max_opps:
                        max_opps = score
                        best_user = user
                
                print(f"   ✅ Mantenuto: ID {best_user.id} ({best_user.username})")
                
                # Aggiungi gli altri alla lista di eliminazione
                for user in users:
                    if user.id != best_user.id:
                        users_to_delete.append(user)
                        print(f"   🗑️  Da eliminare: ID {user.id} ({user.username})")
                        
                        # Trasferisci le opportunità al best_user
                        opps_to_transfer = Opportunity.query.filter_by(owner_id=user.id).count()
                        if opps_to_transfer > 0:
                            Opportunity.query.filter_by(owner_id=user.id).update({'owner_id': best_user.id})
                            print(f"      → Trasferite {opps_to_transfer} opportunità")
                        
                        # Trasferisci i ticket
                        tickets_owner = Ticket.query.filter_by(owner_id=user.id).count()
                        tickets_customer = Ticket.query.filter_by(customer_id=user.id).count()
                        if tickets_owner > 0:
                            Ticket.query.filter_by(owner_id=user.id).update({'owner_id': best_user.id})
                            print(f"      → Trasferiti {tickets_owner} ticket (owner)")
                        if tickets_customer > 0:
                            Ticket.query.filter_by(customer_id=user.id).update({'customer_id': best_user.id})
                            print(f"      → Trasferiti {tickets_customer} ticket (customer)")
                        
                        # Trasferisci le notifiche
                        notifs = Notification.query.filter_by(user_id=user.id).count()
                        if notifs > 0:
                            Notification.query.filter_by(user_id=user.id).update({'user_id': best_user.id})
                            print(f"      → Trasferite {notifs} notifiche")
                        
                        # Trasferisci i task (usa raw SQL per evitare problemi con account_id)
                        from sqlalchemy import text
                        try:
                            tasks_assigned = db.session.execute(
                                text("SELECT COUNT(*) FROM opportunity_tasks WHERE assigned_to_id = :user_id"),
                                {'user_id': user.id}
                            ).scalar()
                            tasks_completed = db.session.execute(
                                text("SELECT COUNT(*) FROM opportunity_tasks WHERE completed_by_id = :user_id"),
                                {'user_id': user.id}
                            ).scalar()
                            
                            if tasks_assigned > 0:
                                db.session.execute(
                                    text("UPDATE opportunity_tasks SET assigned_to_id = :best_id WHERE assigned_to_id = :user_id"),
                                    {'best_id': best_user.id, 'user_id': user.id}
                                )
                                print(f"      → Trasferiti {tasks_assigned} task (assigned)")
                            if tasks_completed > 0:
                                db.session.execute(
                                    text("UPDATE opportunity_tasks SET completed_by_id = :best_id WHERE completed_by_id = :user_id"),
                                    {'best_id': best_user.id, 'user_id': user.id}
                                )
                                print(f"      → Trasferiti {tasks_completed} task (completed)")
                        except Exception as e:
                            print(f"      ⚠️  Errore trasferimento task: {e}")
                
                print()
        
        if not users_to_delete:
            print("✅ Nessun duplicato da rimuovere!")
            return
        
        print(f"\n🗑️  Rimozione di {len(users_to_delete)} utenti duplicati...")
        print()
        
        from sqlalchemy import text
        
        for user in users_to_delete:
            user_id = user.id
            username = user.username
            print(f"   ❌ Eliminazione: ID {user_id} ({username})")
            
            # Elimina direttamente con SQL per evitare problemi con le relazioni
            try:
                db.session.execute(
                    text("DELETE FROM users WHERE id = :user_id"),
                    {'user_id': user_id}
                )
                print(f"      ✅ Eliminato con successo")
            except Exception as e:
                print(f"      ⚠️  Errore eliminazione: {e}")
        
        db.session.commit()
        
        print()
        print("✅ Utenti duplicati rimossi con successo!")
        print()
        print("Utenti finali commerciali:")
        final_users = User.query.filter_by(role='commerciale').all()
        for user in final_users:
            opp_count = Opportunity.query.filter_by(owner_id=user.id).count()
            print(f"   - {user.username} ({user.first_name} {user.last_name}): {opp_count} opportunità")

if __name__ == '__main__':
    try:
        rimuovi_utenti_duplicati()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

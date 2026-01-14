#!/usr/bin/env python3
"""
Script per creare attività di chiamata per gli operatori
Collega le chiamate agli account corrispondenti
"""
import sys
import os
from datetime import datetime, timedelta

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, User, Account, OpportunityTask
from sqlalchemy import or_

# Mapping operatori -> aziende da chiamare
OPERATOR_CALLS = {
    'GIO': [
        'WEGER',
        'PALERMO',
        'SECGO SISTEMI',
        'GEFIT',
        'RIRI',
        'SPECIAL MACHINE',
        'ISELT',
        'ACCENTURE',
        'COSATTO',
        'REDSHIFT',
        'MERLETTI',
        'MC ENGINEERING'
    ],
    'MAURO': [
        'FRAUNHOFER',
        'VERONA SALDATURE'
    ],
    'DAVIDE': [
        'LAFER',
        'MONCLER',
        'CAN SRL',
        'ALGON',
        'LAFERPACK',
        'BWS',
        'AUTECH',
        'INTEGRA',
        'KETER',
        'APPLIED MATERIALS ITALIA',
        'DAVOS',
        'WS ENGINEERING'
    ],
    'FILIPPO': [
        'SOLUZIONE INTRALOGISTICA',
        'LAFER',
        'DE LONGHI'
    ]
}

def find_account_by_name(name):
    """Trova un account per nome (fuzzy matching)"""
    # Prova match esatto
    account = Account.query.filter(Account.name.ilike(name)).first()
    if account:
        return account
    
    # Prova match parziale
    account = Account.query.filter(Account.name.ilike(f'%{name}%')).first()
    if account:
        return account
    
    # Prova senza spazi
    name_no_spaces = name.replace(' ', '')
    account = Account.query.filter(
        or_(
            Account.name.ilike(f'%{name_no_spaces}%'),
            db.func.replace(Account.name, ' ', '').ilike(f'%{name_no_spaces}%')
        )
    ).first()
    
    return account

def find_user_by_name(first_name):
    """Trova un utente per nome (cerca anche nel cognome e username)"""
    # Prova match esatto sul nome
    user = User.query.filter(
        User.first_name.ilike(first_name),
        User.role.in_(['commercial', 'commerciale'])
    ).first()
    if user:
        return user
    
    # Prova match parziale
    user = User.query.filter(
        User.first_name.ilike(f'%{first_name}%'),
        User.role.in_(['commercial', 'commerciale'])
    ).first()
    if user:
        return user
    
    # Prova anche nel cognome
    user = User.query.filter(
        User.last_name.ilike(f'%{first_name}%'),
        User.role.in_(['commercial', 'commerciale'])
    ).first()
    if user:
        return user
    
    # Prova anche nello username
    user = User.query.filter(
        User.username.ilike(f'%{first_name}%'),
        User.role.in_(['commercial', 'commerciale'])
    ).first()
    
    return user

def create_call_tasks():
    """Crea le attività di chiamata per tutti gli operatori"""
    with app.app_context():
        created_count = 0
        not_found_accounts = []
        not_found_users = []
        
        for operator_name, companies in OPERATOR_CALLS.items():
            print(f"\n{'='*60}")
            print(f"Operatore: {operator_name}")
            print(f"{'='*60}")
            
            # Trova l'utente operatore
            user = find_user_by_name(operator_name)
            if not user:
                print(f"  ⚠️  Utente '{operator_name}' non trovato!")
                not_found_users.append(operator_name)
                continue
            
            print(f"  ✓ Utente trovato: {user.first_name} {user.last_name} (ID: {user.id})")
            
            for company_name in companies:
                # Trova l'account
                account = find_account_by_name(company_name)
                
                if not account:
                    print(f"  ⚠️  Account '{company_name}' non trovato")
                    not_found_accounts.append((operator_name, company_name))
                    # Crea comunque l'attività senza account
                    task = OpportunityTask(
                        task_type='call',
                        description=f'Chiamare {company_name}',
                        assigned_to_id=user.id,
                        due_date=datetime.utcnow().date() + timedelta(days=7),  # Scadenza tra 7 giorni
                        opportunity_id=None,  # Attività globale
                        is_completed=False
                    )
                    db.session.add(task)
                    created_count += 1
                    print(f"  ✓ Attività creata (senza account): {company_name}")
                else:
                    print(f"  ✓ Account trovato: {account.name} (ID: {account.id})")
                    
                    # Cerca se esiste già un'opportunità per questo account
                    opportunity = None
                    if account.opportunities:
                        # Prendi la prima opportunità aperta o l'ultima
                        opportunity = next((o for o in account.opportunities if o.stage not in ['Closed Won', 'Closed Lost']), None)
                        if not opportunity:
                            opportunity = account.opportunities[-1] if account.opportunities else None
                    
                    # Crea l'attività
                    task = OpportunityTask(
                        task_type='call',
                        description=f'Chiamare {account.name}',
                        assigned_to_id=user.id,
                        due_date=datetime.utcnow().date() + timedelta(days=7),
                        opportunity_id=opportunity.id if opportunity else None,
                        is_completed=False
                    )
                    db.session.add(task)
                    created_count += 1
                    
                    if opportunity:
                        print(f"  ✓ Attività creata (collegata a opportunità '{opportunity.name}')")
                    else:
                        print(f"  ✓ Attività creata (collegata ad account, senza opportunità)")
        
        # Salva tutto
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Completato!")
            print(f"   Attività create: {created_count}")
            
            if not_found_accounts:
                print(f"\n⚠️  Account non trovati ({len(not_found_accounts)}):")
                for op, company in not_found_accounts:
                    print(f"   - {op}: {company}")
            
            if not_found_users:
                print(f"\n⚠️  Utenti non trovati ({len(not_found_users)}):")
                for op in not_found_users:
                    print(f"   - {op}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Errore durante il salvataggio: {e}")
            raise

if __name__ == '__main__':
    print("Creazione attività di chiamata per operatori...")
    print("=" * 60)
    create_call_tasks()


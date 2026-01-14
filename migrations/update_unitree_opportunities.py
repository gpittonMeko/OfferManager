#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiornare tutte le opportunità Unitree:
- Imposta valore a 20.000€
- Assegna a Giovanni
"""
import sys
import os
from pathlib import Path

# Aggiungi il percorso del progetto
sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db, Opportunity, User

def update_unitree_opportunities():
    """Aggiorna tutte le opportunità Unitree"""
    with app.app_context():
        # Trova Giovanni
        giovanni = User.query.filter(
            (User.username.ilike('%giovanni%')) | 
            (User.first_name.ilike('%giovanni%')) |
            (User.last_name.ilike('%giovanni%'))
        ).first()
        
        if not giovanni:
            print("❌ ERRORE: Utente Giovanni non trovato!")
            print("Utenti disponibili:")
            for u in User.query.all():
                print(f"  - ID: {u.id}, Username: {u.username}, Nome: {u.first_name} {u.last_name}")
            return False
        
        print(f"✅ Trovato Giovanni: ID {giovanni.id}, {giovanni.first_name} {giovanni.last_name}")
        
        # Trova tutte le opportunità Unitree
        # Cerca opportunità con "Unitree" nella supplier_category
        all_opps = Opportunity.query.all()
        unitree_opps = []
        
        for opp in all_opps:
            if opp.supplier_category:
                category_upper = opp.supplier_category.upper()
                if 'UNITREE' in category_upper:
                    unitree_opps.append(opp)
        
        print(f"\n📊 Trovate {len(unitree_opps)} opportunità Unitree")
        
        if not unitree_opps:
            print("⚠️ Nessuna opportunità Unitree trovata!")
            return False
        
        # Aggiorna le opportunità
        updated_count = 0
        for opp in unitree_opps:
            changes = []
            
            # Aggiorna valore
            if opp.amount != 20000:
                old_amount = opp.amount
                opp.amount = 20000.0
                changes.append(f"Valore: €{old_amount} → €20000")
            
            # Assegna a Giovanni
            if opp.owner_id != giovanni.id:
                old_owner = opp.owner.first_name + ' ' + opp.owner.last_name if opp.owner else 'N/A'
                opp.owner_id = giovanni.id
                changes.append(f"Owner: {old_owner} → {giovanni.first_name} {giovanni.last_name}")
            
            if changes:
                db.session.add(opp)
                updated_count += 1
                print(f"\n✅ Opportunità ID {opp.id}: {opp.name}")
                print(f"   Categoria: {opp.supplier_category}")
                for change in changes:
                    print(f"   - {change}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n🎉 Aggiornate {updated_count} opportunità Unitree!")
        else:
            print("\n✅ Tutte le opportunità Unitree sono già aggiornate!")
        
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("AGGIORNAMENTO OPPORTUNITÀ UNITREE")
    print("=" * 60)
    print("\nQuesto script:")
    print("  1. Trova tutte le opportunità con 'Unitree' nella categoria")
    print("  2. Imposta il valore a €20.000")
    print("  3. Assegna a Giovanni")
    print("\n" + "=" * 60 + "\n")
    
    try:
        success = update_unitree_opportunities()
        if success:
            print("\n✅ Operazione completata con successo!")
        else:
            print("\n❌ Operazione fallita!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare le opportunità Unitree assegnate a Giovanni
"""
import sys
import os
from pathlib import Path

# Aggiungi il percorso del progetto
sys.path.insert(0, str(Path(__file__).parent))

from crm_app_completo import app, db, Opportunity, User

def verifica_unitree_giovanni():
    """Verifica le opportunità Unitree assegnate a Giovanni"""
    with app.app_context():
        # Trova Giovanni
        giovanni = User.query.filter(
            (User.username.ilike('%giovanni%')) | 
            (User.first_name.ilike('%giovanni%')) |
            (User.last_name.ilike('%giovanni%'))
        ).first()
        
        if not giovanni:
            print("❌ ERRORE: Utente Giovanni non trovato!")
            return False
        
        print(f"✅ Trovato Giovanni: ID {giovanni.id}, {giovanni.first_name} {giovanni.last_name}")
        
        # Trova tutte le opportunità Unitree
        all_opps = Opportunity.query.all()
        unitree_opps = []
        
        for opp in all_opps:
            if opp.supplier_category:
                category_upper = opp.supplier_category.upper()
                if 'UNITREE' in category_upper:
                    unitree_opps.append(opp)
        
        print(f"\n📊 Trovate {len(unitree_opps)} opportunità Unitree totali")
        
        # Verifica quante sono assegnate a Giovanni
        unitree_giovanni = [o for o in unitree_opps if o.owner_id == giovanni.id]
        print(f"👤 Opportunità Unitree assegnate a Giovanni: {len(unitree_giovanni)}")
        
        # Mostra dettagli
        print("\n" + "=" * 80)
        print("OPPORTUNITÀ UNITREE ASSEGNATE A GIOVANNI")
        print("=" * 80)
        for opp in unitree_giovanni[:20]:  # Mostra prime 20
            owner_name = f"{opp.owner.first_name} {opp.owner.last_name}" if opp.owner else 'Unknown'
            print(f"\nID: {opp.id}")
            print(f"  Nome: {opp.name}")
            print(f"  Categoria: {opp.supplier_category}")
            print(f"  Owner: {owner_name} (ID: {opp.owner_id})")
            print(f"  Valore: €{opp.amount or 0:.2f}")
            print(f"  Stage: {opp.stage}")
        
        if len(unitree_giovanni) > 20:
            print(f"\n... e altre {len(unitree_giovanni) - 20} opportunità")
        
        # Verifica opportunità Unitree NON assegnate a Giovanni
        unitree_altri = [o for o in unitree_opps if o.owner_id != giovanni.id]
        if unitree_altri:
            print("\n" + "=" * 80)
            print(f"⚠️  ATTENZIONE: {len(unitree_altri)} opportunità Unitree NON assegnate a Giovanni:")
            print("=" * 80)
            for opp in unitree_altri[:10]:  # Mostra prime 10
                owner_name = f"{opp.owner.first_name} {opp.owner.last_name}" if opp.owner else 'Unknown'
                print(f"  ID {opp.id}: {opp.name} -> Owner: {owner_name} (ID: {opp.owner_id})")
        
        return True

if __name__ == '__main__':
    print("=" * 80)
    print("VERIFICA OPPORTUNITÀ UNITREE ASSEGNATE A GIOVANNI")
    print("=" * 80)
    print()
    
    try:
        success = verifica_unitree_giovanni()
        if success:
            print("\n✅ Verifica completata!")
        else:
            print("\n❌ Verifica fallita!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

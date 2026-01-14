#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna tutte le opportunità senza heat_level o con heat_level nullo a 'da_categorizzare'"""
import sys
import os
from pathlib import Path

# Aggiungi la root del progetto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from crm_app_completo import app, db, Opportunity
from sqlalchemy import text

def aggiorna_opportunita_da_categorizzare():
    with app.app_context():
        print("=" * 80)
        print("AGGIORNAMENTO OPPORTUNITÀ A 'DA CATEGORIZZARE'")
        print("=" * 80)
        print()
        
        # Conta tutte le opportunità
        total_opp = Opportunity.query.count()
        print(f"📊 Totale opportunità nel database: {total_opp}")
        
        if total_opp == 0:
            print("✅ Nessuna opportunità nel database!")
            return
        
        # Aggiorna TUTTE le opportunità a 'da_categorizzare' (come richiesto dall'utente)
        updated = Opportunity.query.update({Opportunity.heat_level: 'da_categorizzare'}, synchronize_session=False)
        
        db.session.commit()
        
        print(f"\n✅ Aggiornate {updated} opportunità a 'da_categorizzare'!")
        
        # Verifica risultato
        opp_da_categorizzare = Opportunity.query.filter_by(heat_level='da_categorizzare').count()
        
        print(f"📊 Totale opportunità 'Da Categorizzare': {opp_da_categorizzare}")
        print("\n✅ Operazione completata con successo!")

if __name__ == '__main__':
    try:
        aggiorna_opportunita_da_categorizzare()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

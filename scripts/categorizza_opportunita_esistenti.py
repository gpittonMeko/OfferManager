#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Categorizza automaticamente le opportunità esistenti basandosi sul nome e descrizione
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Opportunity

def categorizza_opportunita(nome, descrizione):
    """Categorizza automaticamente un'opportunità basandosi sul nome e descrizione"""
    testo = ((nome or '') + ' ' + (descrizione or '')).upper()
    
    categorie = []
    if 'MIR' in testo or 'MOBILE' in testo or 'AMR' in testo:
        categorie.append('MiR')
    if 'UR' in testo or 'UNIVERSAL ROBOT' in testo or 'COBOT' in testo:
        categorie.append('Universal Robots')
    if 'UNITREE' in testo or 'G1' in testo or 'GO2' in testo or 'B2' in testo or 'R1' in testo:
        categorie.append('Unitree')
    
    if len(categorie) == 0:
        return 'Altri Fornitori'
    
    return ', '.join(categorie)

def categorizza_tutte_opportunita():
    """Categorizza tutte le opportunità senza categoria o con categoria errata"""
    with app.app_context():
        print("=" * 60)
        print("CATEGORIZZAZIONE AUTOMATICA OPPORTUNITÀ")
        print("=" * 60)
        
        opps = Opportunity.query.all()
        categorizzate = 0
        aggiornate = 0
        
        for opp in opps:
            # Se non ha categoria o ha categoria generica, prova a categorizzare
            if not opp.supplier_category or opp.supplier_category in ['Altri Fornitori', 'Altro', '']:
                nuova_categoria = categorizza_opportunita(opp.name, opp.description or '')
                
                if nuova_categoria and nuova_categoria != 'Altri Fornitori':
                    opp.supplier_category = nuova_categoria
                    db.session.add(opp)
                    categorizzate += 1
                    print(f"✅ Categorizzata: {opp.name[:50]} → {nuova_categoria}")
                elif nuova_categoria:
                    categorizzate += 1
            else:
                # Verifica se la categoria è corretta
                categoria_attesa = categorizza_opportunita(opp.name, opp.description or '')
                if categoria_attesa and categoria_attesa != opp.supplier_category and categoria_attesa != 'Altri Fornitori':
                    # Potrebbe essere una categoria multipla, verifica
                    cat_upper = opp.supplier_category.upper()
                    nome_upper = (opp.name or '').upper()
                    desc_upper = (opp.description or '').upper()
                    testo = nome_upper + ' ' + desc_upper
                    
                    # Verifica se la categoria attuale è corretta
                    if 'MIR' in testo and 'MIR' not in cat_upper and 'MiR' not in cat_upper:
                        print(f"⚠️  Possibile errore: {opp.name[:50]} - Categoria: {opp.supplier_category}, Dovrebbe contenere MiR")
                    elif 'UR' in testo and 'UR' not in cat_upper and 'UNIVERSAL' not in cat_upper:
                        print(f"⚠️  Possibile errore: {opp.name[:50]} - Categoria: {opp.supplier_category}, Dovrebbe contenere UR")
                    elif 'UNITREE' in testo and 'UNITREE' not in cat_upper:
                        print(f"⚠️  Possibile errore: {opp.name[:50]} - Categoria: {opp.supplier_category}, Dovrebbe contenere Unitree")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Completato!")
        print(f"   Opportunità categorizzate: {categorizzate}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    categorizza_tutte_opportunita()

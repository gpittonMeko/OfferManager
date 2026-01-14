#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizza tutte le categorie/gruppi presenti nel file users.csv di Vox Mail
"""
import sys
import os
import csv
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))

def analizza_categorie():
    """Analizza tutte le categorie nel file users.csv"""
    file_path = "users.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return
    
    print("=" * 60)
    print("ANALISI CATEGORIE VOX MAIL")
    print("=" * 60)
    
    categorie = Counter()
    categorie_dettagliate = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                gruppi = row.get('Gruppi', '').strip()
                email = row.get('Email', '').strip()
                
                if gruppi:
                    # Conta ogni categoria
                    categorie[gruppi] += 1
                    
                    # Salva dettagli
                    if gruppi not in categorie_dettagliate:
                        categorie_dettagliate[gruppi] = []
                    categorie_dettagliate[gruppi].append(email)
        
        print(f"\n📊 TOTALE CATEGORIE TROVATE: {len(categorie)}\n")
        print("=" * 60)
        print("CATEGORIE (ordinate per frequenza):")
        print("=" * 60)
        
        for categoria, count in categorie.most_common():
            print(f"  {categoria:40s} : {count:5d} contatti")
        
        print(f"\n{'='*60}")
        print("DETTAGLIO CATEGORIE:")
        print(f"{'='*60}\n")
        
        for categoria, count in categorie.most_common():
            print(f"📋 {categoria} ({count} contatti)")
            if count <= 10:
                print(f"   Esempi: {', '.join(categorie_dettagliate[categoria][:5])}")
            print()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizza_categorie()

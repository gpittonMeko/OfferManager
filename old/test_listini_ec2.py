#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test caricamento listini su EC2"""
import os
import sys

# Aggiungi il percorso corrente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offer_generator import OfferGenerator

if __name__ == '__main__':
    print("="*60)
    print("TEST CARICAMENTO LISTINI")
    print("="*60)
    
    # Percorso listini
    pricelist_dir = os.path.join(os.path.dirname(__file__), 'listini')
    print(f"\n📂 Directory listini: {pricelist_dir}")
    print(f"   Esiste: {os.path.exists(pricelist_dir)}")
    
    if os.path.exists(pricelist_dir):
        pdf_files = [os.path.join(pricelist_dir, f) for f in os.listdir(pricelist_dir) if f.endswith('.pdf')]
        print(f"\n📄 PDF trovati: {len(pdf_files)}")
        for pdf in pdf_files[:5]:
            print(f"   - {os.path.basename(pdf)}")
        if len(pdf_files) > 5:
            print(f"   ... e altri {len(pdf_files) - 5} file")
    else:
        print("❌ Directory listini non trovata!")
        sys.exit(1)
    
    if not pdf_files:
        print("❌ Nessun PDF trovato nella directory listini!")
        sys.exit(1)
    
    # Inizializza generatore
    print("\n🔧 Inizializzazione generatore...")
    generator = OfferGenerator()
    
    # Carica listini
    print(f"\n📥 Caricamento {len(pdf_files)} listini...")
    try:
        generator.load_pricelists(pdf_files)
        products = generator.parser.get_all_products()
        print(f"\n✅ Caricamento completato!")
        print(f"   Prodotti totali: {len(products)}")
        
        if products:
            print("\n📋 Esempi prodotti:")
            for i, p in enumerate(products[:5], 1):
                print(f"   {i}. {p.code} - {p.name} ({p.category})")
        else:
            print("⚠️  Nessun prodotto estratto dai PDF!")
    except Exception as e:
        import traceback
        print(f"\n❌ Errore durante il caricamento:")
        print(f"   {str(e)}")
        traceback.print_exc()
        sys.exit(1)





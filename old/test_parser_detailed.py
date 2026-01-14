#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test dettagliato del parser PDF"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import PDFPricelistParser
from offer_generator import OfferGenerator

if __name__ == '__main__':
    print("="*60)
    print("TEST PARSER DETTAGLIATO")
    print("="*60)
    
    # Test parser diretto
    print("\n1. Test parser diretto:")
    parser = PDFPricelistParser()
    pdf_path = os.path.join('listini', 'Unitree G1.pdf')
    if os.path.exists(pdf_path):
        products = parser.parse(pdf_path)
        print(f"   Prodotti estratti: {len(products)}")
        all_products = parser.get_all_products()
        print(f"   Prodotti totali nel parser: {len(all_products)}")
        if all_products:
            print(f"   Primo prodotto: {all_products[0].name} ({all_products[0].code})")
    else:
        print(f"   ❌ File non trovato: {pdf_path}")
    
    # Test generatore
    print("\n2. Test generatore:")
    generator = OfferGenerator()
    pricelist_dir = 'listini'
    if os.path.exists(pricelist_dir):
        pdf_files = [os.path.join(pricelist_dir, f) for f in os.listdir(pricelist_dir) if f.endswith('.pdf')]
        print(f"   PDF trovati: {len(pdf_files)}")
        
        # Carica solo Unitree G1.pdf
        unitree_pdf = [f for f in pdf_files if 'Unitree G1' in f]
        if unitree_pdf:
            print(f"   Caricamento: {unitree_pdf[0]}")
            generator.load_pricelists(unitree_pdf)
            all_products = generator.parser.get_all_products()
            print(f"   Prodotti nel generatore: {len(all_products)}")
            if all_products:
                print(f"   Primi 3 prodotti:")
                for p in all_products[:3]:
                    print(f"      - {p.code}: {p.name}")
        else:
            print("   ❌ Unitree G1.pdf non trovato")
    else:
        print(f"   ❌ Directory listini non trovata")





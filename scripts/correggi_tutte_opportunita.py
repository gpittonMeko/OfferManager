#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correggi automaticamente tutte le opportunità"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.verifica_tutte_opportunita_offerte import verifica_tutte_opportunita, correggi_problemi

if __name__ == '__main__':
    print("=" * 80)
    print("CORREZIONE AUTOMATICA DI TUTTE LE OPPORTUNITÀ")
    print("=" * 80)
    
    problemi = verifica_tutte_opportunita()
    
    if problemi:
        print("\n🔄 Eseguo correzione automatica...")
        correggi_problemi(problemi)
        print("\n" + "=" * 80)
        print("VERIFICA POST-CORREZIONE")
        print("=" * 80)
        problemi_finali = verifica_tutte_opportunita()
        
        # Conta solo i problemi reali (opportunità senza offerte associate)
        problemi_reali = [p for p in problemi_finali if not p['offers']]
        
        if problemi_reali:
            print(f"\n⚠️  Rimangono {len(problemi_reali)} opportunità SENZA offerte associate")
            print(f"   (Le altre sono falsi positivi - un'opportunità può avere più offerte)")
        else:
            print("\n✅ TUTTE LE OPPORTUNITÀ HANNO ALMENO UNA OFFERTA ASSOCIATA!")
            print("   (Le opportunità con più offerte sono corrette)")
    else:
        print("\n✅ Nessun problema trovato!")

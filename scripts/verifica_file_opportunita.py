#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica perché non trova i file per queste opportunità"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text

opp_ids = [34, 122, 90]  # K0390, K1470-25, K1041-25

with app.app_context():
    for opp_id in opp_ids:
        print(f"\n{'='*60}")
        print(f"Opportunità ID: {opp_id}")
        
        # Trova opportunità
        opp = db.session.execute(text("""
            SELECT id, name FROM opportunities WHERE id = :id
        """), {"id": opp_id}).fetchone()
        
        if not opp:
            print("❌ Opportunità non trovata")
            continue
        
        print(f"Nome: {opp[1]}")
        
        # Trova offerte associate
        offers = db.session.execute(text("""
            SELECT id, number, folder_path FROM offers WHERE opportunity_id = :id
        """), {"id": opp_id}).fetchall()
        
        print(f"Offerte associate: {len(offers)}")
        
        for offer_id, offer_num, folder_path in offers:
            print(f"\n  Offerta: {offer_num}")
            print(f"  Folder Path (DB): {folder_path}")
            
            if not folder_path:
                print(f"  ❌ PROBLEMA: Nessun folder_path associato!")
                continue
            
            # Verifica se la cartella esiste
            if folder_path.startswith('K:'):
                # Prova percorso Windows diretto
                if os.path.exists(folder_path):
                    print(f"  ✅ Cartella trovata direttamente: {folder_path}")
                    # Conta file
                    try:
                        files = [f for f in os.listdir(folder_path) 
                                if os.path.isfile(os.path.join(folder_path, f)) 
                                and f.lower().endswith(('.pdf', '.docx', '.doc'))]
                        print(f"  📄 File trovati: {len(files)}")
                        if files:
                            print(f"     Esempi: {', '.join(files[:3])}")
                    except Exception as e:
                        print(f"  ❌ Errore leggendo cartella: {e}")
                else:
                    print(f"  ❌ Cartella NON trovata: {folder_path}")
                    # Prova percorso UNC
                    relative_path = folder_path.replace('K:\\', '').replace('K:/', '').replace('\\', '/')
                    unc_path = f"\\\\192.168.10.240\\commerciale\\{relative_path}"
                    print(f"  🔄 Provo percorso UNC: {unc_path}")
                    if os.path.exists(unc_path):
                        print(f"  ✅ Cartella trovata via UNC!")
                        try:
                            files = [f for f in os.listdir(unc_path) 
                                    if os.path.isfile(os.path.join(unc_path, f)) 
                                    and f.lower().endswith(('.pdf', '.docx', '.doc'))]
                            print(f"  📄 File trovati: {len(files)}")
                        except Exception as e:
                            print(f"  ❌ Errore leggendo cartella: {e}")
                    else:
                        print(f"  ❌ Anche percorso UNC non trovato")
            else:
                print(f"  ⚠️  Percorso non inizia con K: - potrebbe essere un percorso Linux")
                if os.path.exists(folder_path):
                    print(f"  ✅ Cartella trovata: {folder_path}")
                else:
                    print(f"  ❌ Cartella NON trovata: {folder_path}")

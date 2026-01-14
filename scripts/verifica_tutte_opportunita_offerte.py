#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica TUTTE le opportunità e le loro offerte associate"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import re

def verifica_tutte_opportunita():
    """Verifica tutte le opportunità e le loro offerte"""
    with app.app_context():
        print("=" * 80)
        print("VERIFICA COMPLETA: TUTTE LE OPPORTUNITÀ E OFFERTE ASSOCIATE")
        print("=" * 80)
        
        # Recupera tutte le opportunità
        all_opps = db.session.execute(text("""
            SELECT id, name, account_id, folder_path
            FROM opportunities 
            ORDER BY id
        """)).fetchall()
        
        print(f"\n📊 Totale opportunità nel database: {len(all_opps)}\n")
        
        problemi = []
        ok_count = 0
        
        for opp_id, opp_name, account_id, folder_path in all_opps:
            # Estrai numero offerta dal nome (es. "Offerta K1261-25 - CLIENTE" -> "K1261-25")
            match = re.search(r'K(\d{4})-(\d{2})', opp_name)
            offer_number_in_name = match.group(0) if match else None
            
            # Trova offerte associate
            offers = db.session.execute(text("""
                SELECT id, number, folder_path, opportunity_id
                FROM offers 
                WHERE opportunity_id = :opp_id
            """), {"opp_id": opp_id}).fetchall()
            
            # Verifica se ci sono problemi
            has_problem = False
            problem_msg = []
            
            if not offers:
                has_problem = True
                problem_msg.append(f"❌ NESSUNA OFFERTA ASSOCIATA")
                
                # Cerca se esiste un'offerta con il numero nel nome
                if offer_number_in_name:
                    matching_offers = db.session.execute(text("""
                        SELECT id, number, opportunity_id
                        FROM offers 
                        WHERE number = :offer_num
                    """), {"offer_num": offer_number_in_name}).fetchall()
                    
                    if matching_offers:
                        for off in matching_offers:
                            if off[2] != opp_id:
                                problem_msg.append(f"   ⚠️  Offerta {off[1]} esiste ma è associata all'opportunità {off[2]} invece di {opp_id}")
            else:
                # Verifica che le offerte associate abbiano il numero corretto
                for offer in offers:
                    offer_id, offer_number, offer_folder, offer_opp_id = offer
                    if offer_number_in_name and offer_number != offer_number_in_name:
                        has_problem = True
                        problem_msg.append(f"   ⚠️  Offerta associata {offer_number} non corrisponde al numero nel nome {offer_number_in_name}")
            
            if has_problem:
                problemi.append({
                    'opp_id': opp_id,
                    'opp_name': opp_name,
                    'offers': offers,
                    'problem': problem_msg,
                    'offer_number_in_name': offer_number_in_name
                })
            else:
                ok_count += 1
        
        print(f"✅ Opportunità OK: {ok_count}")
        print(f"❌ Opportunità con problemi: {len(problemi)}\n")
        
        if problemi:
            print("=" * 80)
            print("PROBLEMI TROVATI:")
            print("=" * 80)
            for p in problemi:
                print(f"\n🔴 Opportunità ID: {p['opp_id']}")
                print(f"   Nome: {p['opp_name']}")
                print(f"   Numero offerta nel nome: {p['offer_number_in_name']}")
                print(f"   Offerte associate: {len(p['offers'])}")
                for msg in p['problem']:
                    print(f"   {msg}")
                
                # Mostra offerte associate
                if p['offers']:
                    print(f"   Offerte associate:")
                    for off in p['offers']:
                        print(f"      - ID: {off[0]}, Numero: {off[1]}, Folder: {off[2]}")
        
        return problemi

def correggi_problemi(problemi):
    """Correggi automaticamente i problemi trovati - NON CORREGGE, solo associa offerte mancanti"""
    if not problemi:
        print("\n✅ Nessun problema da correggere!")
        return
    
    print("\n" + "=" * 80)
    print("CORREZIONE AUTOMATICA DEI PROBLEMI")
    print("=" * 80)
    print("NOTA: Non rimuoviamo offerte già associate, solo aggiungiamo quelle mancanti")
    print("=" * 80)
    
    correzioni = 0
    
    for p in problemi:
        opp_id = p['opp_id']
        opp_name = p['opp_name']
        offer_number_in_name = p['offer_number_in_name']
        
        # Se non c'è numero nel nome, skip
        if not offer_number_in_name:
            continue
        
        # Cerca offerta con questo numero
        matching_offers = db.session.execute(text("""
            SELECT id, number, opportunity_id
            FROM offers 
            WHERE number = :offer_num
        """), {"offer_num": offer_number_in_name}).fetchall()
        
        if not matching_offers:
            continue
        
        # Se l'offerta con il numero nel nome NON è associata a questa opportunità, associamola
        for offer in matching_offers:
            offer_id, offer_number, current_opp_id = offer
            if current_opp_id != opp_id:
                print(f"\n🔄 Associazione: Offerta {offer_number} (ID: {offer_id})")
                print(f"   Da opportunità {current_opp_id} → a opportunità {opp_id} ({opp_name})")
                
                # Verifica che l'opportunità di destinazione esista
                dest_opp = db.session.execute(text("""
                    SELECT id, name FROM opportunities WHERE id = :opp_id
                """), {"opp_id": opp_id}).fetchone()
                
                if not dest_opp:
                    print(f"   ❌ Opportunità {opp_id} non esiste - SKIP")
                    continue
                
                # Aggiorna associazione
                db.session.execute(text("""
                    UPDATE offers 
                    SET opportunity_id = :opp_id
                    WHERE id = :offer_id
                """), {
                    "opp_id": opp_id,
                    "offer_id": offer_id
                })
                correzioni += 1
                print(f"   ✅ Associata!")
        
        # Se non ci sono offerte associate, associa quella trovata
        if not p['offers'] and matching_offers:
            offer_id = matching_offers[0][0]
            offer_number = matching_offers[0][1]
            current_opp_id = matching_offers[0][2]
            
            if current_opp_id != opp_id:
                print(f"\n🔄 Associazione: Offerta {offer_number} (ID: {offer_id}) a opportunità {opp_id}")
                db.session.execute(text("""
                    UPDATE offers 
                    SET opportunity_id = :opp_id
                    WHERE id = :offer_id
                """), {
                    "opp_id": opp_id,
                    "offer_id": offer_id
                })
                correzioni += 1
                print(f"   ✅ Associata!")
    
    if correzioni > 0:
        db.session.commit()
        print(f"\n✅ Totale correzioni: {correzioni}")
    else:
        print(f"\n⚠️  Nessuna correzione necessaria")

if __name__ == '__main__':
    problemi = verifica_tutte_opportunita()
    
    if problemi:
        risposta = input("\nVuoi correggere automaticamente i problemi? (s/n): ")
        if risposta.lower() == 's':
            correggi_problemi(problemi)
            print("\n" + "=" * 80)
            print("VERIFICA POST-CORREZIONE")
            print("=" * 80)
            verifica_tutte_opportunita()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare le associazioni tra offerte e cartelle
Verifica che ogni offerta abbia una cartella associata e viceversa
"""
import sys
import os
import platform
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, OfferDocument, Opportunity

# Cartelle da verificare
if platform.system() == 'Windows':
    OFFERS_FOLDERS = [
        r"K:\OFFERTE - K\OFFERTE 2025 - K",
        r"K:\OFFERTE - K\OFFERTE 2026 - K",
    ]
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    OFFERS_FOLDERS = [
        os.path.join(base_dir, 'offerte_2025_backup'),
        os.path.join(base_dir, 'offerte_2026_backup'),
        os.environ.get('OFFERS_FOLDER', '/mnt/k/OFFERTE - K/OFFERTE 2025 - K'),
    ]

# Estensioni file offerte
OFFER_EXTENSIONS = ['.docx', '.pdf', '.doc']


def normalize_path(path):
    """Normalizza un percorso per il confronto"""
    if not path:
        return None
    # Normalizza separatori
    path = path.replace('\\', '/')
    # Rimuovi trailing slash
    path = path.rstrip('/')
    return path.lower()


def find_offer_folders():
    """Trova tutte le cartelle che contengono offerte"""
    folders_with_offers = {}
    
    for base_folder in OFFERS_FOLDERS:
        if not os.path.exists(base_folder):
            print(f"⚠️  Cartella non trovata: {base_folder}")
            continue
        
        print(f"🔍 Scansione cartella: {base_folder}")
        
        # Scansiona ricorsivamente
        for root, dirs, files in os.walk(base_folder):
            # Controlla se ci sono file offerte in questa cartella
            offer_files = [
                f for f in files 
                if any(f.lower().endswith(ext) for ext in OFFER_EXTENSIONS)
            ]
            
            if offer_files:
                normalized_root = normalize_path(root)
                folders_with_offers[normalized_root] = {
                    'path': root,
                    'files': offer_files,
                    'count': len(offer_files)
                }
    
    return folders_with_offers


def verify_associations():
    """Verifica le associazioni tra offerte e cartelle"""
    print("=" * 80)
    print("VERIFICA ASSOCIAZIONI OFFERTE - CARTELLE")
    print("=" * 80)
    
    with app.app_context():
        # Recupera tutte le offerte dal database
        all_offers = OfferDocument.query.all()
        print(f"\n📊 Totale offerte nel database: {len(all_offers)}")
        
        # Trova tutte le cartelle con offerte sul filesystem
        folders_with_offers = find_offer_folders()
        print(f"📂 Totale cartelle con offerte trovate: {len(folders_with_offers)}")
        
        # Analizza offerte nel database
        offers_with_folder = []
        offers_without_folder = []
        offers_with_invalid_folder = []
        
        for offer in all_offers:
            if not offer.folder_path:
                offers_without_folder.append(offer)
            else:
                normalized_db_path = normalize_path(offer.folder_path)
                # Verifica se la cartella esiste fisicamente
                if normalized_db_path in folders_with_offers:
                    offers_with_folder.append(offer)
                else:
                    # Verifica se esiste una cartella simile (potrebbe essere un problema di normalizzazione)
                    found = False
                    for folder_key, folder_info in folders_with_offers.items():
                        # Confronta i percorsi base
                        db_base = os.path.basename(offer.folder_path).lower()
                        fs_base = os.path.basename(folder_info['path']).lower()
                        if db_base == fs_base:
                            found = True
                            break
                    
                    if not found:
                        offers_with_invalid_folder.append(offer)
                    else:
                        offers_with_folder.append(offer)
        
        # Analizza cartelle sul filesystem
        folders_with_db_offer = []
        folders_without_db_offer = []
        
        for folder_key, folder_info in folders_with_offers.items():
            found_offer = False
            for offer in all_offers:
                if offer.folder_path:
                    normalized_offer_path = normalize_path(offer.folder_path)
                    # Confronta percorsi normalizzati
                    if normalized_offer_path == folder_key:
                        found_offer = True
                        break
                    # Confronta anche i nomi base delle cartelle
                    db_base = os.path.basename(offer.folder_path).lower()
                    fs_base = os.path.basename(folder_info['path']).lower()
                    if db_base == fs_base:
                        found_offer = True
                        break
            
            if found_offer:
                folders_with_db_offer.append(folder_info)
            else:
                folders_without_db_offer.append(folder_info)
        
        # Report
        print("\n" + "=" * 80)
        print("RISULTATI VERIFICA")
        print("=" * 80)
        
        print(f"\n✅ Offerte con cartella valida: {len(offers_with_folder)}")
        print(f"❌ Offerte senza cartella: {len(offers_without_folder)}")
        print(f"⚠️  Offerte con cartella non trovata: {len(offers_with_invalid_folder)}")
        
        print(f"\n✅ Cartelle con offerta nel DB: {len(folders_with_db_offer)}")
        print(f"❌ Cartelle senza offerta nel DB: {len(folders_without_db_offer)}")
        
        # Dettagli offerte senza cartella
        if offers_without_folder:
            print("\n" + "-" * 80)
            print("OFFERTE SENZA CARTELLA ASSOCIATA:")
            print("-" * 80)
            for offer in offers_without_folder[:20]:  # Mostra prime 20
                print(f"  • ID: {offer.id}, Numero: {offer.number}, Opportunità: {offer.opportunity_id}")
            if len(offers_without_folder) > 20:
                print(f"  ... e altre {len(offers_without_folder) - 20} offerte")
        
        # Dettagli offerte con cartella non trovata
        if offers_with_invalid_folder:
            print("\n" + "-" * 80)
            print("OFFERTE CON CARTELLA NON TROVATA:")
            print("-" * 80)
            for offer in offers_with_invalid_folder[:20]:  # Mostra prime 20
                print(f"  • ID: {offer.id}, Numero: {offer.number}")
                print(f"    Cartella DB: {offer.folder_path}")
            if len(offers_with_invalid_folder) > 20:
                print(f"  ... e altre {len(offers_with_invalid_folder) - 20} offerte")
        
        # Dettagli cartelle senza offerta nel DB
        if folders_without_db_offer:
            print("\n" + "-" * 80)
            print("CARTELLE SENZA OFFERTA NEL DATABASE:")
            print("-" * 80)
            for folder_info in folders_without_db_offer[:20]:  # Mostra prime 20
                print(f"  • {folder_info['path']}")
                print(f"    File offerte: {', '.join(folder_info['files'][:3])}")
                if len(folder_info['files']) > 3:
                    print(f"    ... e altri {len(folder_info['files']) - 3} file")
            if len(folders_without_db_offer) > 20:
                print(f"  ... e altre {len(folders_without_db_offer) - 20} cartelle")
        
        # Statistiche per opportunità
        print("\n" + "-" * 80)
        print("STATISTICHE PER OPPORTUNITÀ:")
        print("-" * 80)
        
        opportunities_stats = defaultdict(lambda: {'total': 0, 'with_folder': 0, 'without_folder': 0})
        
        for offer in all_offers:
            opp_id = offer.opportunity_id if offer.opportunity_id else 'Nessuna'
            opportunities_stats[opp_id]['total'] += 1
            if offer.folder_path and normalize_path(offer.folder_path) in folders_with_offers:
                opportunities_stats[opp_id]['with_folder'] += 1
            else:
                opportunities_stats[opp_id]['without_folder'] += 1
        
        for opp_id, stats in sorted(opportunities_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            opp_name = "Nessuna opportunità"
            if opp_id != 'Nessuna':
                # Usa query SQL diretta per evitare problemi con colonne mancanti
                from sqlalchemy import text
                try:
                    result = db.session.execute(
                        text("SELECT name FROM opportunities WHERE id = :opp_id"),
                        {"opp_id": opp_id}
                    )
                    opp_row = result.fetchone()
                    if opp_row:
                        opp_name = opp_row[0]
                    else:
                        opp_name = f"Opportunità ID {opp_id} (non trovata)"
                except Exception:
                    opp_name = f"Opportunità ID {opp_id}"
            
            print(f"\n  {opp_name}:")
            print(f"    Totale offerte: {stats['total']}")
            print(f"    Con cartella: {stats['with_folder']}")
            print(f"    Senza cartella: {stats['without_folder']}")
        
        # Verifica struttura tabella
        print("\n" + "-" * 80)
        print("VERIFICA STRUTTURA TABELLA:")
        print("-" * 80)
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'offers' in inspector.get_table_names():
            cols = inspector.get_columns('offers')
            print("\nColonne tabella 'offers':")
            folder_path_exists = False
            opportunity_id_exists = False
            
            for col in cols:
                print(f"  ✓ {col['name']} ({col['type']})")
                if col['name'] == 'folder_path':
                    folder_path_exists = True
                if col['name'] == 'opportunity_id':
                    opportunity_id_exists = True
            
            print(f"\n✓ Campo 'folder_path' presente: {folder_path_exists}")
            print(f"✓ Campo 'opportunity_id' presente: {opportunity_id_exists}")
            
            if not folder_path_exists:
                print("⚠️  ATTENZIONE: Campo 'folder_path' mancante nella tabella!")
            if not opportunity_id_exists:
                print("⚠️  ATTENZIONE: Campo 'opportunity_id' mancante nella tabella!")
        else:
            print("❌ Tabella 'offers' non trovata nel database!")
        
        # Verifica opportunità con folder_path
        print("\n" + "-" * 80)
        print("VERIFICA OPPORTUNITÀ CON CARTELLE:")
        print("-" * 80)
        
        try:
            # Prova a recuperare le opportunità, gestendo colonne mancanti
            from sqlalchemy import text
            result = db.session.execute(text("SELECT id, name, folder_path FROM opportunities"))
            opportunities_data = result.fetchall()
            
            all_opportunities_count = len(opportunities_data)
            opps_with_folder = [o for o in opportunities_data if o[2]]  # folder_path è alla posizione 2
            opps_without_folder = [o for o in opportunities_data if not o[2]]
            
            print(f"\nTotale opportunità: {all_opportunities_count}")
            print(f"Con cartella: {len(opps_with_folder)}")
            print(f"Senza cartella: {len(opps_without_folder)}")
            
            if opps_without_folder:
                print("\nPrime 10 opportunità senza cartella:")
                for opp in opps_without_folder[:10]:
                    print(f"  • ID: {opp[0]}, Nome: {opp[1]}")
        except Exception as e:
            print(f"\n⚠️  Errore nel recupero delle opportunità: {e}")
            print("   (Potrebbe essere un problema di schema del database)")
            all_opportunities_count = 0
            opps_without_folder = []
        
        # Suggerimenti
        print("\n" + "=" * 80)
        print("SUGGERIMENTI:")
        print("=" * 80)
        
        if len(all_offers) == 0:
            print("\n⚠️  Nessuna offerta trovata nel database!")
            print("💡 Esegui la sincronizzazione delle offerte:")
            print("   python sync_offers_from_folder.py")
        
        if len(folders_without_db_offer) > 0:
            print(f"\n⚠️  {len(folders_without_db_offer)} cartelle senza offerte nel database")
            print("💡 Esegui la sincronizzazione per associare le cartelle alle offerte")
        
        if len(offers_without_folder) > 0:
            print(f"\n⚠️  {len(offers_without_folder)} offerte senza cartella associata")
            print("💡 Verifica i percorsi delle cartelle nelle offerte")
        
        print("\n" + "=" * 80)
        print("VERIFICA COMPLETATA")
        print("=" * 80)
        
        return {
            'offers_without_folder': offers_without_folder,
            'offers_with_invalid_folder': offers_with_invalid_folder,
            'folders_without_db_offer': folders_without_db_offer,
            'total_offers': len(all_offers),
            'total_folders': len(folders_with_offers),
            'total_opportunities': all_opportunities_count if 'all_opportunities_count' in locals() else 0,
            'opps_without_folder': len(opps_without_folder) if 'opps_without_folder' in locals() else 0
        }


if __name__ == '__main__':
    verify_associations()

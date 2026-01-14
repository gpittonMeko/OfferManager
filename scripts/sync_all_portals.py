#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per sincronizzare tutti i portali:
- Portale UR (Universal Robots)
- Portale Offerte (sincronizzazione cartelle)
- Portale Wix Studio (form contatti)
"""
import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import app, db
from sqlalchemy import text

def sync_ur_portal():
    """Sincronizza il portale Universal Robots"""
    print("🔄 Sincronizzazione Portale UR...")
    try:
        # Prova a importare il modulo UR
        try:
            from utils.ur_portal_integration import sync_ur_portal
            
            with app.app_context():
                admin_user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
                if admin_user:
                    stats = sync_ur_portal(db.session, admin_user[0])
                    print(f"  ✅ UR: {stats.get('opportunities_imported', 0)} opportunità importate")
                    return True
                else:
                    print("  ❌ Utente admin non trovato")
                    return False
        except ImportError:
            print("  ⚠️  Modulo UR non disponibile. Salto sincronizzazione UR.")
            return True  # Non è un errore critico
    except Exception as e:
        print(f"  ⚠️  Errore sincronizzazione UR: {str(e)}")
        return True  # Non è un errore critico


def sync_offers_folder():
    """Sincronizza le offerte dalle cartelle"""
    print("🔄 Sincronizzazione Offerte da cartelle...")
    try:
        # Importa la funzione di sincronizzazione offerte
        # Assumendo che esista sync_offers_from_folder.py
        import subprocess
        result = subprocess.run(
            ['python3', '/home/ubuntu/offermanager/sync_offers_from_folder.py'],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/offermanager'
        )
        
        if result.returncode == 0:
            print("  ✅ Offerte sincronizzate")
            return True
        else:
            print(f"  ❌ Errore: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Errore sincronizzazione offerte: {str(e)}")
        return False


def sync_wix_forms():
    """Sincronizza i form da Wix Studio"""
    print("🔄 Sincronizzazione Form Wix Studio...")
    try:
        from utils.wix_forms_import import import_wix_submissions_from_json
        
        # Per ora, richiede un file JSON con i dati
        # In futuro si può integrare con API Wix
        wix_json_path = '/home/ubuntu/offermanager/data/wix_submissions.json'
        
        if os.path.exists(wix_json_path):
            with app.app_context():
                admin_user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
                if admin_user:
                    imported, skipped = import_wix_submissions_from_json(wix_json_path, admin_user[0])
                    print(f"  ✅ Wix: {imported} opportunità importate, {skipped} saltate")
                    return True
                else:
                    print("  ❌ Utente admin non trovato")
                    return False
        else:
            print(f"  ⚠️  File {wix_json_path} non trovato. Salto sincronizzazione Wix.")
            return True  # Non è un errore critico
    except Exception as e:
        print(f"  ⚠️  Errore sincronizzazione Wix: {str(e)}")
        return True  # Non è un errore critico


def sync_maritime_database():
    """Sincronizza contatti dal database marittimo/ROV"""
    print("🔄 Sincronizzazione Database Marittimo/ROV...")
    try:
        with app.app_context():
            # Conta Lead ROV/Marittimi da convertire
            leads_count = db.session.execute(text("""
                SELECT COUNT(*) FROM leads 
                WHERE status != 'Converted'
                AND (
                    interest LIKE '%ROV%' OR 
                    industry LIKE '%Marina%' OR 
                    industry LIKE '%Marittim%' OR
                    notes LIKE '%ROV%' OR
                    notes LIKE '%marittimo%' OR
                    notes LIKE '%subacqueo%'
                )
            """)).fetchone()[0]
            
            if leads_count > 0:
                # Importa direttamente la funzione invece di chiamare script esterno
                import sys
                sys.path.insert(0, '/home/ubuntu/offermanager/scripts')
                try:
                    from importa_lead_rov_como_opportunita import convert_all_rov_leads
                    converted, skipped, errors = convert_all_rov_leads()
                    print(f"  ✅ Marittimo/ROV: {converted} opportunità create, {skipped} saltate")
                    return True
                except ImportError:
                    # Fallback: esegui script esterno
                    import subprocess
                    result = subprocess.run(
                        ['python3', '/home/ubuntu/offermanager/scripts/importa_lead_rov_como_opportunita.py'],
                        capture_output=True,
                        text=True,
                        cwd='/home/ubuntu/offermanager',
                        timeout=300
                    )
                    if result.returncode == 0:
                        print(f"  ✅ Marittimo/ROV: Lead convertiti")
                        return True
                    else:
                        print(f"  ⚠️  Errore conversione: {result.stderr[:200]}")
                        return True
            else:
                print(f"  ℹ️  Nessun Lead ROV/Marittimo da convertire")
                return True
    except Exception as e:
        print(f"  ⚠️  Errore sincronizzazione Marittimo: {str(e)}")
        return True  # Non critico


def sync_voxmail_contacts():
    """Sincronizza contatti da VOX Mail"""
    print("🔄 Sincronizzazione VOX Mail...")
    try:
        with app.app_context():
            # Verifica se ci sono Lead/Contatti da VOX da importare
            vox_leads = db.session.execute(text("""
                SELECT COUNT(*) FROM leads 
                WHERE (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%')
                AND status != 'Converted'
            """)).fetchone()[0]
            
            if vox_leads > 0:
                print(f"  ℹ️  Trovati {vox_leads} Lead VOX da convertire")
                # Converti anche questi Lead in Opportunità
                # Usa la stessa logica dei Lead ROV
                from scripts.importa_lead_rov_como_opportunita import convert_vox_leads
                try:
                    converted, skipped, errors = convert_vox_leads()
                    print(f"  ✅ VOX: {converted} opportunità create")
                    return True
                except:
                    print(f"  ⚠️  Usa lo script importa_lead_rov_como_opportunita.py per convertirli")
                    return True
            else:
                print(f"  ℹ️  Nessun contatto VOX da sincronizzare")
                return True
    except Exception as e:
        print(f"  ⚠️  Errore sincronizzazione VOX: {str(e)}")
        return True  # Non critico




def main():
    """Esegue tutte le sincronizzazioni"""
    print("=" * 70)
    print(f"🔄 Sincronizzazione Portali - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    results = {
        'UR': sync_ur_portal(),
        'Offerte': sync_offers_folder(),
        'Wix': sync_wix_forms(),
        'Marittimo': sync_maritime_database(),
        'VoxMail': sync_voxmail_contacts()
    }
    
    print()
    print("=" * 70)
    print("📊 Riepilogo:")
    for portal, success in results.items():
        status = "✅ OK" if success else "❌ ERRORE"
        print(f"  {portal}: {status}")
    print("=" * 70)


if __name__ == '__main__':
    main()

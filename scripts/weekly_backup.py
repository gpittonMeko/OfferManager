#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per backup settimanale rotativo del database
Mantiene 4 settimane di backup, alla 5a sovrascrive la 1a
"""
import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Aggiungi il percorso root al path per importare l'app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_path():
    """Trova il percorso del database"""
    # Il database è configurato come 'sqlite:///mekocrm.db' che Flask cerca in instance/
    base_dir = Path(__file__).parent.parent
    instance_path = base_dir / 'instance' / 'mekocrm.db'
    
    # Se non esiste in instance/, prova nella root
    if not instance_path.exists():
        root_path = base_dir / 'mekocrm.db'
        if root_path.exists():
            return str(root_path)
    
    return str(instance_path)

def get_backup_directory():
    """Crea e restituisce la directory per i backup"""
    base_dir = Path(__file__).parent.parent
    backup_dir = base_dir / 'backups' / 'weekly'
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def get_week_number(date=None):
    """Calcola il numero della settimana (1-4) per la rotazione"""
    if date is None:
        date = datetime.now()
    
    # Calcola il numero di settimane dall'inizio dell'anno
    # e usa modulo 4 per ottenere 1-4
    year_start = datetime(date.year, 1, 1)
    days_since_start = (date - year_start).days
    week_number = ((days_since_start // 7) % 4) + 1
    
    return week_number

def create_backup():
    """Crea un backup del database"""
    try:
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            print(f"❌ Database non trovato: {db_path}")
            return False
        
        backup_dir = get_backup_directory()
        week_number = get_week_number()
        
        # Nome file backup: mekocrm_backup_week_N_YYYY-MM-DD.db
        today = datetime.now()
        backup_filename = f"mekocrm_backup_week_{week_number}_{today.strftime('%Y-%m-%d')}.db"
        backup_path = backup_dir / backup_filename
        
        # Se esiste già un backup per questa settimana, sovrascrivilo
        # (in caso di esecuzione multipla nella stessa settimana)
        if backup_path.exists():
            print(f"⚠️  Backup settimana {week_number} già esistente, sovrascrivo...")
        
        # Copia il database
        shutil.copy2(db_path, backup_path)
        
        # Verifica che il backup sia stato creato correttamente
        if backup_path.exists() and os.path.getsize(backup_path) > 0:
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            print(f"✅ Backup creato con successo!")
            print(f"   📁 Percorso: {backup_path}")
            print(f"   📅 Settimana: {week_number}/4")
            print(f"   💾 Dimensione: {size_mb:.2f} MB")
            
            # Pulisci backup vecchi (oltre 4 settimane)
            cleanup_old_backups(backup_dir)
            
            return True
        else:
            print(f"❌ Errore: backup non creato correttamente")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il backup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_old_backups(backup_dir):
    """Rimuove backup più vecchi di 4 settimane"""
    try:
        current_week = get_week_number()
        current_date = datetime.now()
        
        # Trova tutti i file di backup
        backup_files = list(backup_dir.glob('mekocrm_backup_week_*.db'))
        
        for backup_file in backup_files:
            try:
                # Estrai la data dal nome file
                filename = backup_file.name
                # Formato: mekocrm_backup_week_N_YYYY-MM-DD.db
                parts = filename.replace('.db', '').split('_')
                if len(parts) >= 5:
                    date_str = parts[-1]  # Ultima parte è la data
                    backup_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    # Calcola differenza in settimane
                    weeks_diff = (current_date - backup_date).days // 7
                    
                    # Se più vecchio di 4 settimane, elimina
                    if weeks_diff >= 4:
                        backup_file.unlink()
                        print(f"🗑️  Rimosso backup vecchio: {backup_file.name} ({weeks_diff} settimane fa)")
            except Exception as e:
                print(f"⚠️  Errore processando {backup_file.name}: {e}")
                continue
                
    except Exception as e:
        print(f"⚠️  Errore durante pulizia backup vecchi: {e}")

def list_backups():
    """Lista tutti i backup disponibili"""
    backup_dir = get_backup_directory()
    backup_files = sorted(backup_dir.glob('mekocrm_backup_week_*.db'), key=os.path.getmtime, reverse=True)
    
    if not backup_files:
        print("📦 Nessun backup trovato")
        return
    
    print(f"📦 Backup disponibili ({len(backup_files)}):\n")
    for backup_file in backup_files:
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_file))
        print(f"   📁 {backup_file.name}")
        print(f"      💾 {size_mb:.2f} MB")
        print(f"      📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup settimanale rotativo database MekoCRM')
    parser.add_argument('--list', action='store_true', help='Lista i backup disponibili')
    parser.add_argument('--force', action='store_true', help='Forza creazione backup anche se già esiste')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups()
    else:
        create_backup()

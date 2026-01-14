#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copia le offerte da K:\\OFFERTE - K\\OFFERTE 2025 - K su EC2
NON sposta, solo copia!
"""
import os
import subprocess
import sys

# Percorso sorgente (Windows)
SOURCE_DIR = r"K:\OFFERTE - K\OFFERTE 2025 - K"

# Destinazione EC2
EC2_HOST = "ubuntu@13.53.183.146"
EC2_KEY = r"C:\Users\user\Documents\LLM_14.pem"
EC2_DEST = "~/offermanager/offerte_2025_backup"

def main():
    print("="*60)
    print("COPIA OFFERTE DA K:\\ SU EC2")
    print("="*60)
    
    # Verifica che la cartella sorgente esista
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Cartella sorgente non trovata: {SOURCE_DIR}")
        print("💡 Verifica che la cartella K:\\ sia montata/accessibile")
        return False
    
    print(f"\nCartella sorgente: {SOURCE_DIR}")
    
    # Conta file
    file_count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        file_count += len([f for f in files if f.endswith(('.docx', '.pdf', '.doc'))])
    
    print(f"File offerte trovati: {file_count}")
    
    if file_count == 0:
        print("Nessun file offerta trovato!")
        return False
    
    # Conferma (skip in ambiente non interattivo)
    print(f"\nProcedo con la copia di {file_count} file...")
    
    # Crea directory su EC2
    print(f"\nCreazione directory su EC2: {EC2_DEST}")
    ssh_cmd = f'ssh -i "{EC2_KEY}" {EC2_HOST} "mkdir -p {EC2_DEST}"'
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Errore creazione directory: {result.stderr}")
        return False
    
    # Copia file con rsync (preserva struttura cartelle)
    print(f"\nCopia file in corso...")
    rsync_cmd = [
        'rsync',
        '-avz',
        '--progress',
        f'-e', f'ssh -i "{EC2_KEY}"',
        f'{SOURCE_DIR}/',
        f'{EC2_HOST}:{EC2_DEST}/'
    ]
    
    try:
        result = subprocess.run(rsync_cmd, check=True)
        print(f"\nCopia completata!")
        print(f"   File copiati su: {EC2_HOST}:{EC2_DEST}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nErrore durante la copia: {e}")
        return False
    except FileNotFoundError:
        print("\nrsync non trovato. Installazione alternativa con scp...")
        # Fallback: usa scp per copiare (più lento)
        return copy_with_scp()

def copy_with_scp():
    """Copia usando scp (fallback se rsync non disponibile)"""
    print("\nCopia con scp (puo richiedere tempo)...")
    # Per semplicità, copia solo i file nella root (non ricorsivo)
    # Per una copia completa ricorsiva, meglio usare rsync
    scp_cmd = f'scp -i "{EC2_KEY}" -r "{SOURCE_DIR}"/* {EC2_HOST}:{EC2_DEST}/'
    result = subprocess.run(scp_cmd, shell=True)
    if result.returncode == 0:
        print("Copia completata!")
        return True
    else:
        print("Errore durante la copia")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


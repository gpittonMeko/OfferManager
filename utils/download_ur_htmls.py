#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per scaricare gli HTML delle pagine UR dalla macchina SSH alla cartella Download locale
"""
import os
import subprocess
from pathlib import Path

# Configurazione SSH
SSH_KEY = r"C:\Users\user\Documents\LLM_14.pem"
SSH_HOST = "ubuntu@13.53.183.146"
REMOTE_PATH = "/tmp"
LOCAL_DOWNLOADS = Path.home() / "Downloads"

# File da scaricare
FILES_TO_DOWNLOAD = [
    "0_pagina_login.html",
    "1_pagina_dopo_login.html",
    "2_pagina_leads.html",
    "3_pagina_opportunita.html"
]

def download_html_files():
    """Scarica gli HTML dalla macchina SSH alla cartella Download"""
    print("=" * 60)
    print("DOWNLOAD HTML PAGINE UR")
    print("=" * 60)
    print(f"Cartella Download: {LOCAL_DOWNLOADS}")
    print("=" * 60)
    
    downloaded = []
    failed = []
    
    for filename in FILES_TO_DOWNLOAD:
        remote_file = f"{REMOTE_PATH}/{filename}"
        local_file = LOCAL_DOWNLOADS / filename
        
        print(f"\nScaricamento: {filename}...")
        
        try:
            # Usa scp per scaricare il file
            cmd = [
                "scp",
                "-i", SSH_KEY,
                f"{SSH_HOST}:{remote_file}",
                str(local_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if local_file.exists():
                    size = local_file.stat().st_size
                    print(f"  OK Scaricato: {local_file}")
                    print(f"     Dimensione: {size:,} bytes")
                    downloaded.append(filename)
                else:
                    print(f"  ATTENZIONE File non trovato dopo download")
                    failed.append(filename)
            else:
                print(f"  ERRORE: {result.stderr}")
                failed.append(filename)
                
        except subprocess.TimeoutExpired:
            print(f"  ERRORE Timeout durante download")
            failed.append(filename)
        except Exception as e:
            print(f"  ERRORE: {e}")
            failed.append(filename)
    
    print("\n" + "=" * 60)
    print("RISULTATI DOWNLOAD")
    print("=" * 60)
    print(f"Scaricati: {len(downloaded)}/{len(FILES_TO_DOWNLOAD)}")
    
    if downloaded:
        print("\nFile scaricati:")
        for filename in downloaded:
            print(f"   OK {filename}")
    
    if failed:
        print(f"\nFile non scaricati: {len(failed)}")
        for filename in failed:
            print(f"   ERRORE {filename}")
    
    print(f"\nCartella Download: {LOCAL_DOWNLOADS}")
    print("=" * 60)
    
    return len(downloaded) == len(FILES_TO_DOWNLOAD)

if __name__ == "__main__":
    success = download_html_files()
    exit(0 if success else 1)


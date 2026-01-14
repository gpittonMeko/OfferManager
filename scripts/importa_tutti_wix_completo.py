#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa TUTTI i 104 contatti dal form Wix Studio come Opportunità
Versione completa con tutti i contatti
"""
import sys
import os
import json
sys.path.insert(0, '/home/ubuntu/offermanager')

from utils.wix_forms_import import import_wix_submissions_from_json
from crm_app_completo import app, db
from sqlalchemy import text

# LEGGI TUTTI I CONTATTI DAL FILE JSON SE ESISTE, ALTRIMENTI USA QUESTO ARRAY
# Per aggiungere tutti i 104 contatti, esporta da Wix Studio in JSON e salvalo in data/wix_submissions.json

if __name__ == '__main__':
    with app.app_context():
        # Ottieni user admin
        admin_user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
        if not admin_user:
            print("❌ Utente admin non trovato!")
            sys.exit(1)
        
        user_id = admin_user[0]
        
        # Prova a leggere da file JSON completo se esiste
        json_file = '/home/ubuntu/offermanager/data/wix_submissions.json'
        
        if os.path.exists(json_file):
            print(f"📂 Lettura da file: {json_file}")
            imported, skipped = import_wix_submissions_from_json(json_file, user_id)
        else:
            print(f"⚠️  File {json_file} non trovato!")
            print(f"\n💡 Per importare tutti i 104 contatti:")
            print(f"   1. Esporta i dati da Wix Studio")
            print(f"   2. Salva in formato JSON in: {json_file}")
            print(f"   3. Riesegui questo script")
            print(f"\n   Oppure usa lo script importa_tutti_wix.py con i contatti hardcoded")
            sys.exit(1)
        
        print(f"\n{'='*70}")
        print(f"✅ COMPLETATO!")
        print(f"   Importate: {imported} opportunità")
        print(f"   Saltate: {skipped} (già esistenti)")
        print(f"{'='*70}")

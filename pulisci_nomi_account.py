#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulisce i nomi degli account rimuovendo caratteri strani come ~$ e normalizzando
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db, Account

def clean_account_name(name):
    """Pulisce il nome account rimuovendo caratteri strani e normalizzando"""
    if not name:
        return ""
    
    # Rimuovi prefissi ~$ (file temporanei Windows) e altri caratteri strani all'inizio
    cleaned = re.sub(r'^[~\$\s]+', '', name)
    
    # Rimuovi caratteri speciali non standard (mantieni solo lettere, numeri, spazi, trattini, apostrofi, parentesi, virgole, punti)
    cleaned = re.sub(r'[^\w\s\-\.\,\'\(\)]', '', cleaned)
    
    # Rimuovi spazi multipli
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Rimuovi spazi all'inizio e alla fine
    cleaned = cleaned.strip()
    
    # Se il nome è troppo corto o contiene solo caratteri strani, ritorna stringa vuota
    if len(cleaned) < 2:
        return ""
    
    # Capitalizza correttamente (prima lettera di ogni parola, ma mantieni maiuscole esistenti per sigle)
    words = cleaned.split()
    cleaned_words = []
    for word in words:
        # Se è tutto maiuscolo o contiene numeri, mantieni com'è (probabilmente una sigla)
        if word.isupper() or any(c.isdigit() for c in word):
            cleaned_words.append(word)
        else:
            # Capitalizza solo la prima lettera
            cleaned_words.append(word.capitalize())
    
    cleaned = ' '.join(cleaned_words)
    
    return cleaned

def pulisci_nomi_account():
    """Pulisce tutti i nomi degli account nel database"""
    with app.app_context():
        accounts = Account.query.all()
        
        print("=" * 80)
        print("PULIZIA NOMI ACCOUNT")
        print("=" * 80)
        print()
        
        updated_count = 0
        skipped_count = 0
        
        for account in accounts:
            original_name = account.name
            cleaned_name = clean_account_name(original_name)
            
            if cleaned_name != original_name and cleaned_name:
                # Verifica se esiste già un account con questo nome pulito
                existing = Account.query.filter_by(name=cleaned_name).first()
                
                if existing and existing.id != account.id:
                    print(f"⚠️  SKIP: '{original_name}' -> '{cleaned_name}' (esiste già account ID {existing.id})")
                    skipped_count += 1
                else:
                    account.name = cleaned_name
                    updated_count += 1
                    print(f"✅ '{original_name}' -> '{cleaned_name}'")
            elif not cleaned_name:
                print(f"⚠️  SKIP: '{original_name}' -> (nome vuoto dopo pulizia)")
                skipped_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print()
            print("=" * 80)
            print(f"✅ Aggiornati {updated_count} account")
            if skipped_count > 0:
                print(f"⚠️  Saltati {skipped_count} account (duplicati)")
            print("=" * 80)
        else:
            print()
            print("=" * 80)
            print("✅ Nessun account da aggiornare")
            if skipped_count > 0:
                print(f"⚠️  Saltati {skipped_count} account (duplicati)")
            print("=" * 80)

if __name__ == '__main__':
    try:
        pulisci_nomi_account()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

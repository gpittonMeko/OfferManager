#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea liste email basate sulle categorie/gruppi di Vox Mail
"""
import sys
import os
import csv
import re
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User, EmailList, EmailListSubscription
from datetime import datetime

def estrai_categorie_da_gruppi(gruppi):
    """Estrae tutte le categorie da una stringa di gruppi (separate da virgola)"""
    if not gruppi:
        return []
    
    # Separa per virgola e pulisci
    categorie = [c.strip() for c in str(gruppi).split(',')]
    # Rimuovi vuoti
    categorie = [c for c in categorie if c]
    return categorie

def crea_liste_categorie_voxmail():
    """Crea liste email per ogni categoria trovata in Vox Mail"""
    with app.app_context():
        print("=" * 60)
        print("CREAZIONE LISTE PER CATEGORIE VOX MAIL")
        print("=" * 60)
        
        # Verifica admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("❌ Errore: Nessun utente admin trovato")
            return
        
        # Leggi il file users.csv per trovare tutte le categorie
        users_file = os.path.join(os.path.dirname(__file__), "users.csv")
        if not os.path.exists(users_file):
            print(f"❌ File users.csv non trovato: {users_file}")
            return
        
        # Raccogli tutte le categorie uniche
        categorie_counter = Counter()
        
        with open(users_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                gruppi = row.get('Gruppi', '').strip()
                if gruppi:
                    categorie = estrai_categorie_da_gruppi(gruppi)
                    for cat in categorie:
                        categorie_counter[cat] += 1
        
        print(f"\n📋 Trovate {len(categorie_counter)} categorie uniche\n")
        
        # Crea una lista per ogni categoria (solo quelle con almeno 5 contatti)
        liste_create = 0
        totale_iscrizioni = 0
        
        for categoria, count in categorie_counter.most_common():
            if count < 5:  # Salta categorie troppo piccole
                continue
            
            lista_name = f"Vox Mail - {categoria}"
            
            try:
                # Verifica se la lista esiste già
                lista_esistente = EmailList.query.filter_by(name=lista_name).first()
                if lista_esistente:
                    print(f"⏭️  Lista già esistente: {lista_name}")
                    lista = lista_esistente
                else:
                    lista = EmailList(
                        name=lista_name,
                        description=f"Contatti da Vox Mail - Categoria: {categoria} ({count} contatti nel file)",
                        owner_id=admin.id
                    )
                    db.session.add(lista)
                    db.session.flush()
                    print(f"✅ Lista creata: {lista_name} ({count} contatti nel file)")
                    liste_create += 1
                
                # Iscrivi i leads che hanno questa categoria nei gruppi
                # Cerca nei notes (dove abbiamo salvato i gruppi)
                # Usa una ricerca più precisa per evitare match parziali
                all_leads = Lead.query.filter(Lead.source == 'VOX MAIL').all()
                leads = []
                for lead in all_leads:
                    if not lead.notes:
                        continue
                    # Estrai i gruppi dai notes
                    if 'Gruppi:' in lead.notes:
                        gruppi_part = lead.notes.split('Gruppi:')[1].split('\n')[0].strip()
                        categorie_lead = estrai_categorie_da_gruppi(gruppi_part)
                        if categoria in categorie_lead:
                            leads.append(lead)
                
                iscritti_questa_lista = 0
                for lead in leads:
                    if not lead.email:
                        continue
                    
                    # Verifica se già iscritto
                    esistente = EmailListSubscription.query.filter_by(
                        list_id=lista.id,
                        lead_id=lead.id
                    ).first()
                    
                    if not esistente:
                        subscription = EmailListSubscription(
                            list_id=lista.id,
                            lead_id=lead.id,
                            email=lead.email,
                            first_name=lead.contact_first_name,
                            last_name=lead.contact_last_name,
                            status='subscribed',
                            subscribed_at=datetime.utcnow()
                        )
                        db.session.add(subscription)
                        iscritti_questa_lista += 1
                        totale_iscrizioni += 1
                
                if iscritti_questa_lista > 0:
                    print(f"   📧 Iscritti {iscritti_questa_lista} contatti alla lista")
                
            except Exception as e:
                print(f"❌ Errore creando lista {lista_name}: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Completato!")
        print(f"   Liste create: {liste_create}")
        print(f"   Totale iscrizioni: {totale_iscrizioni}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    crea_liste_categorie_voxmail()

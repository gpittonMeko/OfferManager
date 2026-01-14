#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rimuove le liste Vox Mail esistenti e le ricrea correttamente
"""
import sys
import os
import csv
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User, EmailList, EmailListSubscription
from datetime import datetime

def estrai_categorie_da_gruppi(gruppi):
    """Estrae tutte le categorie da una stringa di gruppi (separate da virgola)"""
    if not gruppi:
        return []
    categorie = [c.strip() for c in str(gruppi).split(',')]
    return [c for c in categorie if c]

def ricrea_liste_categorie_voxmail():
    """Rimuove e ricrea le liste Vox Mail correttamente"""
    with app.app_context():
        print("=" * 60)
        print("RICREAZIONE LISTE VOX MAIL")
        print("=" * 60)
        
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("❌ Errore: Nessun utente admin trovato")
            return
        
        # 1. Rimuovi tutte le liste Vox Mail esistenti
        print("\n🗑️  Rimozione liste esistenti...")
        liste_esistenti = EmailList.query.filter(EmailList.name.like('Vox Mail - %')).all()
        for lista in liste_esistenti:
            # Rimuovi iscrizioni
            EmailListSubscription.query.filter_by(list_id=lista.id).delete()
            # Rimuovi lista
            db.session.delete(lista)
        db.session.commit()
        print(f"   ✅ Rimosse {len(liste_esistenti)} liste")
        
        # 2. Leggi il file users.csv per mappare email -> categorie
        users_file = os.path.join(os.path.dirname(__file__), "users.csv")
        if not os.path.exists(users_file):
            print(f"❌ File users.csv non trovato: {users_file}")
            return
        
        email_to_categorie = {}
        categorie_counter = Counter()
        
        print("\n📖 Lettura file users.csv...")
        with open(users_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                email = row.get('Email', '').strip().lower()
                gruppi = row.get('Gruppi', '').strip()
                if email and gruppi:
                    categorie = estrai_categorie_da_gruppi(gruppi)
                    email_to_categorie[email] = categorie
                    for cat in categorie:
                        categorie_counter[cat] += 1
        
        print(f"   ✅ Letti {len(email_to_categorie)} contatti con categorie")
        print(f"   ✅ Trovate {len(categorie_counter)} categorie uniche\n")
        
        # 3. Crea liste per categorie con almeno 5 contatti
        liste_create = 0
        totale_iscrizioni = 0
        
        for categoria, count in categorie_counter.most_common():
            if count < 5:
                continue
            
            lista_name = f"Vox Mail - {categoria}"
            
            try:
                lista = EmailList(
                    name=lista_name,
                    description=f"Contatti da Vox Mail - Categoria: {categoria}",
                    owner_id=admin.id
                )
                db.session.add(lista)
                db.session.flush()
                print(f"✅ Lista creata: {lista_name}")
                liste_create += 1
                
                # Trova tutti i leads con email che corrispondono a questa categoria
                iscritti_questa_lista = 0
                for email_lower, categorie_lead in email_to_categorie.items():
                    if categoria not in categorie_lead:
                        continue
                    
                    # Cerca il lead per email
                    lead = Lead.query.filter(
                        Lead.email.ilike(email_lower),
                        Lead.source == 'VOX MAIL'
                    ).first()
                    
                    if not lead:
                        continue
                    
                    # Verifica se già iscritto (non dovrebbe esserci, ma controlliamo)
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
                
                print(f"   📧 Iscritti {iscritti_questa_lista} contatti")
                
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
    ricrea_liste_categorie_voxmail()

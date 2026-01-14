#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per creare liste contatti basate su source e interest
e iscrivere automaticamente i leads alle liste corrispondenti
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User
from datetime import datetime

# Provo a importare EmailList se esiste
try:
    from crm_app_completo import EmailList, EmailListSubscription
    HAS_EMAIL_LIST = True
except ImportError:
    HAS_EMAIL_LIST = False
    print("⚠️  Modelli EmailList non trovati - creerò solo le liste logiche")

def crea_liste_contatti():
    """Crea liste contatti e iscrive i leads"""
    with app.app_context():
        print("=" * 60)
        print("CREAZIONE LISTE CONTATTI")
        print("=" * 60)
        
        # Verifica admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("❌ Errore: Nessun utente admin trovato")
            return
        
        # Definisci le liste da creare
        liste_da_creare = [
            {
                'name': 'Tutti i Contatti',
                'description': 'Lista completa di tutti i contatti per campagne email generali',
                'filter': None  # Tutti
            },
            {
                'name': 'Sito Web - Unitree',
                'description': 'Contatti dal sito web interessati a Unitree',
                'filter': {'source': 'SITO WEB', 'interest': 'Unitree'}
            },
            {
                'name': 'Sito Web - Universal Robots',
                'description': 'Contatti dal sito web interessati a Universal Robots',
                'filter': {'source': 'SITO WEB', 'interest': 'UR'}
            },
            {
                'name': 'Sito Web - MiR',
                'description': 'Contatti dal sito web interessati a MiR',
                'filter': {'source': 'SITO WEB', 'interest': 'MIR'}
            },
            {
                'name': 'Vox Mail - Unitree',
                'description': 'Contatti da Vox Mail interessati a Unitree',
                'filter': {'source': 'VOX MAIL', 'interest': 'Unitree'}
            },
            {
                'name': 'Vox Mail - Universal Robots',
                'description': 'Contatti da Vox Mail interessati a Universal Robots',
                'filter': {'source': 'VOX MAIL', 'interest': 'UR'}
            },
            {
                'name': 'Vox Mail - MiR',
                'description': 'Contatti da Vox Mail interessati a MiR',
                'filter': {'source': 'VOX MAIL', 'interest': 'MIR'}
            },
            {
                'name': 'Tutti - Sito Web',
                'description': 'Tutti i contatti provenienti dal sito web',
                'filter': {'source': 'SITO WEB'}
            },
            {
                'name': 'Tutti - Vox Mail',
                'description': 'Tutti i contatti provenienti da Vox Mail',
                'filter': {'source': 'VOX MAIL'}
            },
            {
                'name': 'Tutti - Unitree',
                'description': 'Tutti i contatti interessati a Unitree (qualsiasi source)',
                'filter': {'interest': 'Unitree'}
            },
            {
                'name': 'Tutti - Universal Robots',
                'description': 'Tutti i contatti interessati a Universal Robots (qualsiasi source)',
                'filter': {'interest': 'UR'}
            },
            {
                'name': 'Tutti - MiR',
                'description': 'Tutti i contatti interessati a MiR (qualsiasi source)',
                'filter': {'interest': 'MIR'}
            }
        ]
        
        liste_create = 0
        totale_iscrizioni = 0
        
        for lista_info in liste_da_creare:
            try:
                    # Crea la lista (se il modello esiste)
                if HAS_EMAIL_LIST:
                    # Verifica se la lista esiste già
                    lista_esistente = EmailList.query.filter_by(name=lista_info['name']).first()
                    if lista_esistente:
                        print(f"⏭️  Lista già esistente: {lista_info['name']}")
                        lista = lista_esistente
                    else:
                        # Prova con owner_id
                        try:
                            lista = EmailList(
                                name=lista_info['name'],
                                description=lista_info['description'],
                                owner_id=admin.id
                            )
                            db.session.add(lista)
                            db.session.flush()  # Per ottenere l'ID
                            print(f"✅ Lista creata: {lista_info['name']}")
                            liste_create += 1
                        except Exception as e:
                            print(f"❌ Errore creando lista {lista_info['name']}: {e}")
                            db.session.rollback()
                            lista = None
                else:
                    # Se non esiste il modello, crea direttamente con SQL
                    try:
                        # Verifica se la tabella esiste
                        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='email_lists'"))
                        if result.fetchone():
                            # Tabella esiste, crea la lista
                            db.session.execute(
                                db.text("INSERT OR IGNORE INTO email_lists (name, description, created_at, updated_at) VALUES (:name, :description, :now, :now)"),
                                {'name': lista_info['name'], 'description': lista_info['description'], 'now': datetime.utcnow()}
                            )
                            db.session.commit()
                            print(f"✅ Lista creata (SQL): {lista_info['name']}")
                            liste_create += 1
                            lista = {'id': None}  # Placeholder
                        else:
                            print(f"⚠️  Tabella email_lists non esiste - lista logica: {lista_info['name']}")
                            lista = None
                    except Exception as e:
                        print(f"⚠️  Errore creando lista {lista_info['name']}: {e} - lista logica")
                        lista = None
                
                # Trova i leads che corrispondono al filtro
                query = Lead.query
                if lista_info['filter']:
                    if 'source' in lista_info['filter']:
                        query = query.filter_by(source=lista_info['filter']['source'])
                    if 'interest' in lista_info['filter']:
                        query = query.filter_by(interest=lista_info['filter']['interest'])
                else:
                    # Tutti i leads
                    pass
                
                leads = query.all()
                
                # Iscrivi i leads alla lista (solo se la lista è stata creata)
                if lista:
                    try:
                        # Prova con modello se disponibile
                        if HAS_EMAIL_LIST and hasattr(lista, 'id'):
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
                                        subscribed_at=datetime.utcnow()
                                    )
                                    db.session.add(subscription)
                                    totale_iscrizioni += 1
                        else:
                            # Usa SQL diretto
                            list_id_result = db.session.execute(
                                db.text("SELECT id FROM email_lists WHERE name = :name"),
                                {'name': lista_info['name']}
                            ).fetchone()
                            if list_id_result:
                                list_id = list_id_result[0]
                                for lead in leads:
                                    if not lead.email:
                                        continue
                                    # Verifica se già iscritto
                                    esistente = db.session.execute(
                                        db.text("SELECT id FROM email_list_subscriptions WHERE list_id = :list_id AND lead_id = :lead_id"),
                                        {'list_id': list_id, 'lead_id': lead.id}
                                    ).fetchone()
                                    
                                    if not esistente:
                                        db.session.execute(
                                            db.text("INSERT INTO email_list_subscriptions (list_id, lead_id, email, subscribed_at) VALUES (:list_id, :lead_id, :email, :now)"),
                                            {'list_id': list_id, 'lead_id': lead.id, 'email': lead.email, 'now': datetime.utcnow()}
                                        )
                                        totale_iscrizioni += 1
                    except Exception as e:
                        print(f"   ⚠️  Errore iscrivendo leads: {e}")
                
                print(f"   → {len(leads)} leads trovati per questa lista")
                
            except Exception as e:
                print(f"❌ Errore creando lista {lista_info['name']}: {e}")
                db.session.rollback()
                continue
        
        if HAS_EMAIL_LIST:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Completato!")
            print(f"   Liste create: {liste_create}")
            print(f"   Totale iscrizioni: {totale_iscrizioni}")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print(f"⚠️  Modelli EmailList non disponibili")
            print(f"   Liste logiche definite: {len(liste_da_creare)}")
            print(f"   (Le liste verranno create quando i modelli saranno disponibili)")
            print(f"{'='*60}\n")

if __name__ == "__main__":
    crea_liste_contatti()

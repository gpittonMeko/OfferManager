#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica se ci sono contatti duplicati tra le liste email
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, EmailList, EmailListSubscription, Lead
from collections import defaultdict

def verifica_duplicati():
    """Verifica duplicati tra liste"""
    with app.app_context():
        print("=" * 60)
        print("VERIFICA DUPLICATI TRA LISTE EMAIL")
        print("=" * 60)
        
        # Recupera tutte le liste
        liste = EmailList.query.all()
        print(f"\n📋 Totale liste: {len(liste)}\n")
        
        # Per ogni lista, recupera gli email
        liste_emails = {}
        for lista in liste:
            subscriptions = EmailListSubscription.query.filter_by(
                list_id=lista.id,
                status='subscribed'
            ).all()
            emails = [s.email.lower().strip() for s in subscriptions if s.email]
            liste_emails[lista.id] = {
                'name': lista.name,
                'emails': set(emails),
                'count': len(emails)
            }
            print(f"  - {lista.name}: {len(emails)} contatti")
        
        # Trova email che compaiono in più liste
        email_to_lists = defaultdict(list)
        for list_id, data in liste_emails.items():
            for email in data['emails']:
                email_to_lists[email].append(list_id)
        
        # Conta duplicati
        duplicates = {email: lists for email, lists in email_to_lists.items() if len(lists) > 1}
        
        print(f"\n{'='*60}")
        print(f"📊 ANALISI DUPLICATI")
        print(f"{'='*60}")
        print(f"  Totale email unici: {len(email_to_lists)}")
        print(f"  Email in più liste: {len(duplicates)}")
        
        if duplicates:
            print(f"\n⚠️  TROVATI {len(duplicates)} CONTATTI DUPLICATI!")
            print(f"\nEsempi (primi 10):")
            count = 0
            for email, list_ids in list(duplicates.items())[:10]:
                list_names = [liste_emails[lid]['name'] for lid in list_ids]
                print(f"  - {email}: in {len(list_ids)} liste ({', '.join(list_names)})")
                count += 1
                if count >= 10:
                    break
        
        # Calcola totale unico
        total_unique = len(email_to_lists)
        total_with_duplicates = sum(data['count'] for data in liste_emails.values())
        
        print(f"\n{'='*60}")
        print(f"📈 TOTALE CONTATTI")
        print(f"{'='*60}")
        print(f"  Somma contatti (con duplicati): {total_with_duplicates}")
        print(f"  Contatti unici (senza duplicati): {total_unique}")
        print(f"  Differenza (duplicati): {total_with_duplicates - total_unique}")
        
        # Verifica "Tutti i Contatti"
        lista_tutti = EmailList.query.filter_by(name='Tutti i Contatti').first()
        if lista_tutti:
            subs_tutti = EmailListSubscription.query.filter_by(
                list_id=lista_tutti.id,
                status='subscribed'
            ).all()
            count_tutti = len([s.email for s in subs_tutti if s.email])
            print(f"\n  Lista 'Tutti i Contatti': {count_tutti} contatti")
            if count_tutti != total_unique:
                print(f"  ⚠️  La lista 'Tutti i Contatti' non corrisponde ai contatti unici!")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    verifica_duplicati()

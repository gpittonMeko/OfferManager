#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di inizializzazione completo per MekoCRM
- Carica listini
- Importa offerte passate
- Sincronizza UR portal
"""
import sys
from crm_app_completo import app, db, init_db, User
from price_loader import load_price_catalog
from analyze_past_offers import analyze_offers_folder, import_offers_to_crm
from ur_portal_integration import sync_ur_portal

def main():
    print("=" * 60)
    print("MEKOCRM - Inizializzazione Completa")
    print("=" * 60)
    
    with app.app_context():
        # 1. Inizializza database
        print("\n1. Inizializzazione database...")
        init_db()
        print("   ✓ Database inizializzato")
        
        # 2. Carica listini
        print("\n2. Caricamento listini...")
        try:
            catalog = load_price_catalog()
            
            # Sincronizza nel database
            from crm_app_completo import Product, PriceBookEntry
            
            synced = 0
            for code, entry in catalog.items():
                product = Product.query.filter_by(code=code).first()
                if not product:
                    product = Product(
                        code=code,
                        name=entry.name,
                        description=entry.description,
                        category=entry.category,
                        family=entry.family,
                        is_active=True
                    )
                    db.session.add(product)
                    db.session.flush()
                    synced += 1
                
                # Aggiorna prezzi
                for level, amount in entry.price_levels.items():
                    price_entry = PriceBookEntry.query.filter_by(
                        product_id=product.id,
                        price_level=level
                    ).first()
                    
                    if not price_entry:
                        price_entry = PriceBookEntry(
                            product_id=product.id,
                            price_level=level,
                            amount=amount,
                            currency='EUR',
                            source=entry.sources.get(level, 'official'),
                            is_active=True
                        )
                        db.session.add(price_entry)
            
            db.session.commit()
            print(f"   ✓ Sincronizzati {synced} nuovi prodotti")
            print(f"   ✓ Totale prodotti nel catalogo: {len(catalog)}")
            
        except Exception as e:
            print(f"   ✗ Errore caricamento listini: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Importa offerte passate
        print("\n3. Importazione offerte passate...")
        try:
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User.query.first()
            
            if user:
                offers_data = analyze_offers_folder()
                imported = import_offers_to_crm(offers_data, db.session, user.id)
                print(f"   ✓ Importate {imported} offerte")
            else:
                print("   ⚠ Nessun utente trovato, salto importazione")
                
        except Exception as e:
            print(f"   ✗ Errore importazione offerte: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Sincronizza UR portal (opzionale)
        print("\n4. Sincronizzazione UR Portal...")
        try:
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User.query.first()
            
            if user:
                stats = sync_ur_portal(db.session, user.id)
                if stats['errors']:
                    print(f"   ⚠ Errori: {stats['errors']}")
                else:
                    print(f"   ✓ Leads importati: {stats['leads_imported']}")
                    print(f"   ✓ Opportunities importate: {stats['opportunities_imported']}")
                    print(f"   ✓ Accounts creati: {stats['accounts_created']}")
            else:
                print("   ⚠ Nessun utente trovato, salto sincronizzazione UR")
                
        except Exception as e:
            print(f"   ⚠ Errore sincronizzazione UR (non critico): {e}")
        
        print("\n" + "=" * 60)
        print("✓ Inizializzazione completata!")
        print("=" * 60)


if __name__ == "__main__":
    main()










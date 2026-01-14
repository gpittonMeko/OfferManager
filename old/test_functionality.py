#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test delle funzionalità principali"""
import sys
import traceback

print("=" * 60)
print("TEST FUNZIONALITÀ MEKOCRM")
print("=" * 60)

# Test 1: Price Loader
print("\n1. Test Price Loader...")
try:
    from price_loader import load_price_catalog
    catalog = load_price_catalog()
    print(f"   ✓ Prodotti caricati: {len(catalog)}")
    if len(catalog) > 0:
        sample = list(catalog.items())[0]
        print(f"   ✓ Esempio: {sample[0]} - {sample[1].name}")
        print(f"   ✓ Livelli prezzo: {list(sample[1].price_levels.keys())}")
    else:
        print("   ✗ ERRORE: Nessun prodotto caricato!")
except Exception as e:
    print(f"   ✗ ERRORE: {e}")
    traceback.print_exc()

# Test 2: Database sync
print("\n2. Test Database Sync...")
try:
    from crm_app_completo import app, db, Product, PriceBookEntry
    with app.app_context():
        from price_loader import load_price_catalog
        catalog = load_price_catalog()
        
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
        
        total_products = Product.query.count()
        total_prices = PriceBookEntry.query.count()
        print(f"   ✓ Totale prodotti nel DB: {total_products}")
        print(f"   ✓ Totale prezzi nel DB: {total_prices}")
        
except Exception as e:
    print(f"   ✗ ERRORE: {e}")
    traceback.print_exc()

# Test 3: UR Portal Integration
print("\n3. Test UR Portal Integration...")
try:
    from ur_portal_integration import sync_ur_portal
    from crm_app_completo import app, db, User
    with app.app_context():
        user = User.query.first()
        if user:
            stats = sync_ur_portal(db.session, user.id)
            print(f"   ✓ Leads importati: {stats['leads_imported']}")
            print(f"   ✓ Opportunities importate: {stats['opportunities_imported']}")
            print(f"   ✓ Accounts creati: {stats['accounts_created']}")
            if stats['errors']:
                print(f"   ⚠ Errori: {stats['errors']}")
        else:
            print("   ⚠ Nessun utente trovato")
except Exception as e:
    print(f"   ✗ ERRORE: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETATI")
print("=" * 60)










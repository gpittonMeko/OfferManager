#!/usr/bin/env python3
from price_loader import load_price_catalog

cat = load_price_catalog('./listini')
print(f'Totale prodotti: {len(cat)}')
print('Esempi:', list(cat.keys())[:30])









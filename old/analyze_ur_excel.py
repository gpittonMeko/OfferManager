#!/usr/bin/env python3
"""Analizza Excel UR per capire struttura"""
import pandas as pd
from pathlib import Path

excel_path = Path("listini/MEKO SRL - LISTINO UR 2025.xlsx")
if not excel_path.exists():
    excel_path = Path("C:/Users/user/Documents/Listini/MEKO SRL - LISTINO UR 2025.xlsx")

df = pd.read_excel(excel_path, sheet_name="UR", header=None)

print("Shape:", df.shape)
print("\n=== PRIME 15 RIGHE ===")
for i in range(min(15, len(df))):
    print(f"Riga {i}: {df.iloc[i, :15].tolist()}")

print("\n=== CERCA PRODOTTI UR ===")
product_codes = []
for row_idx in range(len(df)):
    for col_idx in range(len(df.columns)):
        cell = df.iloc[row_idx, col_idx]
        if pd.notna(cell):
            cell_str = str(cell).strip().upper()
            if cell_str.startswith('UR') and len(cell_str) <= 10 and cell_str not in ['UR', 'UR ']:
                if cell_str not in product_codes:
                    product_codes.append(cell_str)
                    print(f"Trovato {cell_str} alla riga {row_idx}, colonna {col_idx}")

print(f"\n=== TOTALE PRODOTTI TROVATI: {len(product_codes)} ===")
print(product_codes)









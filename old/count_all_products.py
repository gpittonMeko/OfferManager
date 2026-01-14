#!/usr/bin/env python3
"""Conta tutti i prodotti da tutti i listini"""
from pathlib import Path
import pdfplumber
import pandas as pd
import re

listini_dir = Path("./listini")
if not listini_dir.exists():
    listini_dir = Path("C:/Users/user/Documents/Listini")

all_products = set()

# UR Excel
ur_excel = listini_dir / "MEKO SRL - LISTINO UR 2025.xlsx"
if ur_excel.exists():
    df = pd.read_excel(ur_excel, sheet_name="UR", header=None)
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            cell = df.iloc[row_idx, col_idx]
            if pd.notna(cell):
                cell_str = str(cell).strip().upper()
                if cell_str.startswith('UR') and len(cell_str) <= 10:
                    all_products.add(cell_str)
    print(f"UR Excel: {len([p for p in all_products if p.startswith('UR')])} prodotti")

# MiR PDFs
mir_pdfs = list(listini_dir.glob("*MiR*.pdf"))
mir_count = 0
for pdf_path in mir_pdfs:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Cerca codici prodotto MiR (es: MiR100, MiR250, MiR500, etc.)
                mir_codes = re.findall(r'MiR\s*\d+[A-Z]?', text, re.IGNORECASE)
                for code in mir_codes:
                    all_products.add(code.upper().replace(' ', ''))
                    mir_count += 1
    except Exception as e:
        print(f"Errore {pdf_path.name}: {e}")
print(f"MiR PDFs: ~{mir_count} riferimenti trovati")

# Unitree PDFs
unitree_pdfs = list(listini_dir.glob("*Unitree*.pdf")) + list(listini_dir.glob("*unitree*.pdf"))
unitree_count = 0
for pdf_path in unitree_pdfs:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Cerca codici Unitree (es: Go1, Go2, H1, etc.)
                unitree_codes = re.findall(r'\b(Go\d+|H\d+|Aliengo|A1)\b', text, re.IGNORECASE)
                for code in unitree_codes:
                    all_products.add(code.upper())
                    unitree_count += 1
    except Exception as e:
        print(f"Errore {pdf_path.name}: {e}")
print(f"Unitree PDFs: ~{unitree_count} riferimenti trovati")

# ROEQ PDFs
roeq_pdfs = list(listini_dir.glob("*ROEQ*.pdf"))
roeq_count = 0
for pdf_path in roeq_pdfs:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Cerca codici ROEQ
                roeq_codes = re.findall(r'ROEQ\s*[-]?\s*\w+', text, re.IGNORECASE)
                for code in roeq_codes:
                    all_products.add(code.upper().replace(' ', ''))
                    roeq_count += 1
    except Exception as e:
        print(f"Errore {pdf_path.name}: {e}")
print(f"ROEQ PDFs: ~{roeq_count} riferimenti trovati")

print(f"\n=== TOTALE PRODOTTI UNICI: {len(all_products)} ===")
print(f"Prodotti trovati: {sorted(list(all_products))[:50]}")









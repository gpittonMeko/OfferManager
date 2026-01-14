#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Price Loader - Carica prezzi da tutti i listini ufficiali
Supporta: UR Excel, MiR PDF, Unitree PDF, ROEQ PDF, Servizi
"""
import pdfplumber
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Optional, List
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from datetime import date


@dataclass
class CatalogEntry:
    """Entry del catalogo con tutti i livelli di prezzo"""
    code: str
    name: str
    description: str = ""
    category: str = ""
    family: str = ""
    price_levels: Dict[str, float] = field(default_factory=dict)
    sources: Dict[str, str] = field(default_factory=dict)  # price_level -> source file
    
    def apply_price(self, level: str, amount: float, source: str = ""):
        """Applica un prezzo a un livello"""
        if amount and amount > 0:
            self.price_levels[level] = amount
            if source:
                self.sources[level] = source


def _decimal_from_string(s: str) -> Optional[float]:
    """Converte stringa prezzo in float"""
    if not s or pd.isna(s):
        return None
    s = str(s).strip().replace(',', '.').replace('€', '').replace('EUR', '').strip()
    # Rimuovi spazi e caratteri non numerici tranne punto
    s = ''.join(c for c in s if c.isdigit() or c == '.')
    try:
        return float(s) if s else None
    except (ValueError, InvalidOperation):
        return None


def _ensure_entry(code: str, catalog: Dict[str, CatalogEntry], name: str = "", desc: str = "") -> CatalogEntry:
    """Crea o recupera entry nel catalogo"""
    if code not in catalog:
        catalog[code] = CatalogEntry(code=code, name=name or code, description=desc)
    return catalog[code]


def _load_ur_pricebook(path: Path, catalog: Dict[str, CatalogEntry]):
    """Carica listino UR da Excel"""
    if not path.exists():
        return
    
    try:
        df = pd.read_excel(path, sheet_name="UR", header=None)
        
        # Trova header prodotti dalla riga 5 (colonne 2-7)
        product_codes = []
        product_headers = df.iloc[5, 2:8].tolist()
        for code in product_headers:
            if pd.notna(code):
                code_str = str(code).strip().upper()
                if code_str.startswith('UR'):
                    product_codes.append(code_str)
        
        # Mappa label -> price level
        label_map = {
            "Acquisto": "ur_acquisto",
            "C.S.I.": "ur_csi",
            "S.I.": "ur_si",
            "E.U. Prezzo suggerito": "ur_msrp",
            "Acquisto con spedizione": "ur_acquisto_spedizione",
            "E.U. Prezzo suggerito con spedizione": "ur_msrp_spedizione",
        }
        
        # Estrai prezzi per ogni livello
        for label, level in label_map.items():
            row = df[df[1] == label]
            if row.empty:
                continue
            row_values = row.iloc[0]
            for idx, product_code in enumerate(product_codes):
                if idx + 2 < len(row_values):
                    price = _decimal_from_string(row_values.iloc[2 + idx])
                    if price:
                        entry = _ensure_entry(product_code, catalog)
                        entry.apply_price(level, price, source=f"UR|{path.name}")
        
        # Mappature compatibilità bronze/silver/gold
        priority = [
            ("bronze", "ur_acquisto"),
            ("silver", "ur_si"),
            ("gold", "ur_msrp"),
        ]
        for product_code in product_codes:
            entry = _ensure_entry(product_code, catalog)
            for alias, original in priority:
                if original in entry.price_levels:
                    entry.apply_price(alias, entry.price_levels[original], source="alias")
                    
    except Exception as e:
        print(f"Errore caricamento UR {path.name}: {e}")


def _load_mir_pricebook_pdf(path: Path, catalog: Dict[str, CatalogEntry]):
    """Carica listino MiR da PDF"""
    if not path.exists():
        return
    
    try:
        import re
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Cerca TUTTI i codici MiR nel testo (MiR100, MiR250, MiR500, MiR600, MiR1000, MiR1200, MiR1350, etc.)
                mir_pattern = r'MiR\s*(\d+[A-Z]?)'
                matches = re.finditer(mir_pattern, text, re.IGNORECASE)
                
                for match in matches:
                    code_num = match.group(1)
                    code_full = f"MIR{code_num}".upper()
                    
                    # Cerca prezzi dopo il codice prodotto (nelle prossime 10 righe)
                    match_start = match.start()
                    text_after = text[match_start:match_start+500]  # 500 caratteri dopo il match
                    
                    # Cerca "Distributor Price EUR" o "Distributor Price"
                    distributor_match = re.search(r'Distributor\s+Price\s+(?:EUR\s+)?[:\s]*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', text_after, re.IGNORECASE)
                    if distributor_match:
                        distributor_price = _decimal_from_string(distributor_match.group(1))
                        if distributor_price:
                            entry = _ensure_entry(code_full, catalog, name=f"MiR {code_num}")
                            entry.apply_price("mir_distributor", distributor_price, source=f"MiR|{path.name}")
                            entry.apply_price("bronze", distributor_price, source="alias")
                    
                    # Cerca "List Price EUR" o "List Price"
                    list_match = re.search(r'List\s+Price\s+(?:EUR\s+)?[:\s]*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', text_after, re.IGNORECASE)
                    if list_match:
                        list_price = _decimal_from_string(list_match.group(1))
                        if list_price:
                            entry = _ensure_entry(code_full, catalog)
                            entry.apply_price("mir_list", list_price, source=f"MiR|{path.name}")
                            entry.apply_price("gold", list_price, source="alias")
                            
    except Exception as e:
        print(f"Errore caricamento MiR PDF {path.name}: {e}")


def _load_unitree_pricebook(path: Path, catalog: Dict[str, CatalogEntry]):
    """Carica listino Unitree da PDF"""
    if not path.exists():
        return
    
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Pattern prodotti Unitree: G1, GO2, B2, H1, A2, R1
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line_upper = line.upper()
                    # Cerca codici prodotto
                    product_codes = ['G1', 'GO2', 'B2', 'H1', 'A2', 'R1']
                    for code_base in product_codes:
                        if code_base in line_upper:
                            # Estrai variante (EDU, PRO, W, U6, etc.)
                            variant = ""
                            if 'EDU' in line_upper:
                                variant = "-EDU"
                            elif 'PRO' in line_upper:
                                variant = "-PRO"
                            elif 'W' in line_upper and ('WHEELED' in line_upper or ' W ' in line_upper):
                                variant = "-W"
                            elif 'U6' in line_upper:
                                variant = "-U6"
                            
                            code = f"{code_base}{variant}" if variant else code_base
                            
                            # Cerca prezzi nelle righe successive
                            for j in range(i, min(i+10, len(lines))):
                                price_line = lines[j]
                                prices = re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', price_line)
                                if prices:
                                    price = _decimal_from_string(prices[0])
                                    if price:
                                        entry = _ensure_entry(code, catalog, name=f"Unitree {code}")
                                        entry.category = "Unitree"
                                        entry.apply_price("bronze", price, source=f"Unitree|{path.name}")
                                        break
                                        
    except Exception as e:
        print(f"Errore caricamento Unitree {path.name}: {e}")


def _load_roeq_pricebook(path: Path, catalog: Dict[str, CatalogEntry]):
    """Carica listino ROEQ da PDF"""
    if not path.exists():
        return
    
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Pattern prodotti ROEQ
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'ROEQ' in line.upper() or 'GRIPPER' in line.upper() or 'VACUUM' in line.upper():
                        # Estrai codice prodotto
                        code = None
                        if 'GRIPPER 2F' in line.upper() or '2-FINGER' in line.upper():
                            code = "ROEQ-GRIPPER-2F"
                        elif 'GRIPPER 3F' in line.upper() or '3-FINGER' in line.upper():
                            code = "ROEQ-GRIPPER-3F"
                        elif 'VACUUM' in line.upper():
                            code = "ROEQ-VACUUM"
                        elif 'VISION 2D' in line.upper():
                            code = "ROEQ-VISION-2D"
                        elif 'VISION 3D' in line.upper():
                            code = "ROEQ-VISION-3D"
                        elif 'FORCE' in line.upper() or 'TORQUE' in line.upper():
                            code = "ROEQ-FORCE-SENSOR"
                        
                        if code:
                            # Cerca prezzi
                            for j in range(i, min(i+5, len(lines))):
                                price_line = lines[j]
                                prices = re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', price_line)
                                if prices:
                                    price = _decimal_from_string(prices[0])
                                    if price:
                                        entry = _ensure_entry(code, catalog)
                                        entry.category = "ROEQ"
                                        entry.apply_price("bronze", price, source=f"ROEQ|{path.name}")
                                        break
                                        
    except Exception as e:
        print(f"Errore caricamento ROEQ {path.name}: {e}")


def load_price_catalog(listini_dir: str = None) -> Dict[str, CatalogEntry]:
    """
    Carica catalogo completo da tutti i listini
    
    Args:
        listini_dir: Directory contenente i listini (default: Windows path o ./listini su Linux)
    
    Returns:
        Dict[code, CatalogEntry] con tutti i prodotti e prezzi
    """
    import re
    
    if listini_dir is None:
        # Su Linux usa path diverso, su Windows il path originale
        import platform
        if platform.system() == 'Windows':
            listini_dir = r"C:\Users\user\Documents\Listini"
        else:
            # Su Linux/EC2 cerca nella directory listini locale
            listini_dir = "./listini"
    
    base_path = Path(listini_dir)
    if not base_path.exists():
        print(f"Directory listini non trovata: {listini_dir}")
        return {}
    
    catalog: Dict[str, CatalogEntry] = {}
    
    # Carica UR Excel
    ur_excel = base_path / "MEKO SRL - LISTINO UR 2025.xlsx"
    if ur_excel.exists():
        print(f"Caricamento UR Excel: {ur_excel.name}")
        _load_ur_pricebook(ur_excel, catalog)
    
    # Carica MiR PDF
    mir_pdfs = list(base_path.glob("*MiR*.pdf"))
    for pdf_path in mir_pdfs:
        print(f"Caricamento MiR PDF: {pdf_path.name}")
        _load_mir_pricebook_pdf(pdf_path, catalog)
    
    # Carica Unitree PDF
    unitree_pdfs = list(base_path.glob("*Unitree*.pdf")) + list(base_path.glob("*unitree*.pdf"))
    for pdf_path in unitree_pdfs:
        print(f"Caricamento Unitree PDF: {pdf_path.name}")
        _load_unitree_pricebook(pdf_path, catalog)
    
    # Carica ROEQ PDF
    roeq_pdfs = list(base_path.glob("*ROEQ*.pdf"))
    for pdf_path in roeq_pdfs:
        print(f"Caricamento ROEQ PDF: {pdf_path.name}")
        _load_roeq_pricebook(pdf_path, catalog)
    
    # Aggiungi servizi manuali
    servizi = {
        "TRAINING-BASE": ("Formazione Base (1 giorno)", "Servizi"),
        "TRAINING-ADV": ("Formazione Avanzata (3 giorni)", "Servizi"),
        "INSTALLATION": ("Installazione e Commissioning", "Servizi"),
        "SUPPORT-1Y": ("Supporto Tecnico 1 Anno", "Servizi"),
        "SUPPORT-3Y": ("Supporto Tecnico 3 Anni", "Servizi"),
        "CUSTOMIZATION": ("Sviluppo Custom", "Servizi"),
    }
    
    for code, (name, cat) in servizi.items():
        entry = _ensure_entry(code, catalog, name=name)
        entry.category = cat
    
    print(f"\n✓ Catalogo caricato: {len(catalog)} prodotti")
    return catalog


if __name__ == "__main__":
    catalog = load_price_catalog()
    for code, entry in list(catalog.items())[:10]:
        print(f"\n{code}: {entry.name}")
        for level, price in entry.price_levels.items():
            print(f"  {level}: €{price:,.2f}")


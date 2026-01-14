#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizza offerte PDF passate e le importa nel CRM
"""
import pdfplumber
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def extract_offer_number(folder_name: str) -> Optional[str]:
    """Estrae numero offerta dal nome cartella"""
    match = re.search(r'K\d{4}-\d{2}', folder_name)
    return match.group(0) if match else None


def extract_date_from_folder(folder_name: str) -> Optional[datetime]:
    """Estrae data dal nome cartella"""
    # Pattern: K0001-25 - CLIENTE - PRODOTTO - 01-01-2025
    date_patterns = [
        r'(\d{2}-\d{2}-\d{4})',
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, folder_name)
        if match:
            date_str = match.group(1)
            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
    return None


def extract_client_name(folder_name: str) -> str:
    """Estrae nome cliente dal nome cartella"""
    # Pattern: K0001-25 - CLIENTE - PRODOTTO - DATA
    parts = folder_name.split(' - ')
    if len(parts) > 1:
        return parts[1].strip()
    return "Cliente Sconosciuto"


def extract_products_from_pdf(pdf_path: Path) -> List[Dict]:
    """Estrae prodotti e prezzi da PDF offerta"""
    products = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            # Cerca prodotti comuni
            product_patterns = {
                'MIR': r'(MIR\s*\d{3,4}|MiR\s*\d{3,4})',
                'UR': r'(UR\d+e?|UR\s*\d+e?)',
                'Unitree': r'(G1|GO2|B2|H1|A2|R1|Unitree)',
                'ROEQ': r'(ROEQ|Gripper|Vacuum)',
            }
            
            found_products = []
            for category, pattern in product_patterns.items():
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    product_code = match.group(1).strip().upper()
                    found_products.append({
                        'code': product_code,
                        'category': category,
                        'name': product_code
                    })
            
            # Cerca totale offerta
            total_patterns = [
                r'Totale[:\s]+€?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'Total[:\s]+€?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'Importo[:\s]+€?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            ]
            
            total_amount = None
            for pattern in total_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        total_amount = float(amount_str)
                        break
                    except:
                        continue
            
            return {
                'products': found_products,
                'total_amount': total_amount,
                'text': full_text[:1000]  # Primi 1000 caratteri per debug
            }
            
    except Exception as e:
        print(f"Errore analisi PDF {pdf_path.name}: {e}")
        return {'products': [], 'total_amount': None, 'text': ''}
    
    return {'products': [], 'total_amount': None, 'text': ''}


def analyze_offers_folder(offers_dir: str = None) -> List[Dict]:
    """
    Analizza tutte le offerte nella cartella
    
    Args:
        offers_dir: Directory offerte (default: C:\Users\user\Documents\Offerte)
    
    Returns:
        Lista di dict con dati offerte
    """
    if offers_dir is None:
        offers_dir = r"C:\Users\user\Documents\Offerte"
    
    base_path = Path(offers_dir)
    if not base_path.exists():
        print(f"Directory offerte non trovata: {offers_dir}")
        return []
    
    results = []
    
    # Itera su tutte le cartelle
    for folder in base_path.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        
        # Estrai info base
        offer_number = extract_offer_number(folder_name)
        if not offer_number:
            continue
        
        client_name = extract_client_name(folder_name)
        offer_date = extract_date_from_folder(folder_name)
        
        # Cerca PDF nella cartella
        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            # Cerca anche DOCX
            docx_files = list(folder.glob("*.docx"))
            if docx_files:
                # Per ora salta DOCX, solo PDF
                continue
            continue
        
        # Analizza primo PDF trovato
        pdf_path = pdf_files[0]
        pdf_data = extract_products_from_pdf(pdf_path)
        
        # Determina categoria principale
        categories = [p['category'] for p in pdf_data['products']]
        main_category = categories[0] if categories else 'Altro'
        
        # Determina stato (basato su data - se vecchia probabilmente chiusa)
        status = 'draft'
        if offer_date:
            days_old = (datetime.now() - offer_date).days
            if days_old > 90:
                status = 'expired'
            elif days_old > 30:
                status = 'sent'
        
        result = {
            'number': offer_number,
            'client_name': client_name,
            'date': offer_date.isoformat() if offer_date else None,
            'category': main_category,
            'products': pdf_data['products'],
            'total_amount': pdf_data['total_amount'],
            'status': status,
            'pdf_path': str(pdf_path),
            'folder_path': str(folder)
        }
        
        results.append(result)
    
    return results


def import_offers_to_crm(offers_data: List[Dict], db_session, user_id: int = 1):
    """
    Importa offerte nel database CRM
    
    Args:
        offers_data: Lista di dict con dati offerte
        db_session: SQLAlchemy session
        user_id: ID utente proprietario
    """
    from crm_app_completo import OfferDocument, Opportunity, Account, Contact, OpportunityLineItem, Product
    
    imported = 0
    
    for offer_data in offers_data:
        # Crea o trova Account
        account = Account.query.filter_by(name=offer_data['client_name']).first()
        if not account:
            account = Account(
                name=offer_data['client_name'],
                owner_id=user_id
            )
            db_session.add(account)
            db_session.flush()
        
        # Crea Opportunity se non esiste
        opp_name = f"Opportunity {offer_data['number']}"
        opportunity = Opportunity.query.filter_by(name=opp_name).first()
        if not opportunity:
            close_date = None
            if offer_data['date']:
                close_date = datetime.fromisoformat(offer_data['date']).date()
            
            opportunity = Opportunity(
                name=opp_name,
                stage='Closed Won' if offer_data['status'] == 'expired' else 'Proposal',
                amount=offer_data['total_amount'] or 0.0,
                close_date=close_date,
                account_id=account.id,
                owner_id=user_id
            )
            db_session.add(opportunity)
            db_session.flush()
        
        # Crea OfferDocument
        offer_doc = OfferDocument.query.filter_by(number=offer_data['number']).first()
        if not offer_doc:
            offer_doc = OfferDocument(
                number=offer_data['number'],
                status=offer_data['status'],
                amount=offer_data['total_amount'] or 0.0,
                description=f"Importata da cartella: {Path(offer_data['folder_path']).name}",
                pdf_path=offer_data['pdf_path'],
                folder_path=offer_data['folder_path'],
                opportunity_id=opportunity.id,
                owner_id=user_id
            )
            db_session.add(offer_doc)
            
            # Aggiungi prodotti come line items
            for prod_data in offer_data['products']:
                # Cerca prodotto nel catalogo
                product = Product.query.filter(
                    Product.code.ilike(f"%{prod_data['code']}%")
                ).first()
                
                if product:
                    # Usa primo prezzo disponibile
                    unit_price = 0.0
                    if product.prices:
                        unit_price = product.prices[0].amount
                    
                    line_item = OpportunityLineItem(
                        opportunity_id=opportunity.id,
                        product_id=product.id,
                        quantity=1,
                        unit_price=unit_price,
                        total_price=unit_price
                    )
                    db_session.add(line_item)
            
            imported += 1
    
    db_session.commit()
    return imported


if __name__ == "__main__":
    print("Analisi offerte passate...")
    offers = analyze_offers_folder()
    print(f"\n✓ Trovate {len(offers)} offerte")
    
    for offer in offers[:5]:  # Mostra prime 5
        print(f"\n{offer['number']}: {offer['client_name']}")
        print(f"  Categoria: {offer['category']}")
        print(f"  Totale: €{offer['total_amount']:,.2f}" if offer['total_amount'] else "  Totale: N/D")
        print(f"  Prodotti: {len(offer['products'])}")









